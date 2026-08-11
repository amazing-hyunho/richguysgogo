from __future__ import annotations

"""Pure, deterministic scoring for the five-stage research-to-market chain."""

from statistics import fmean

from committee.research_radar.models import (
    DIRECTNESS_WEIGHTS,
    SOURCE_RELIABILITY,
    STAGE_LABELS,
    STAGE_ORDER,
    STAGE_WEIGHTS,
    CompanyAssessment,
    Evidence,
    ExcludedEvidence,
    RadarReport,
    StageAssessment,
    ThemeInput,
)


STAGE_SCORE_THRESHOLD = 60.0
STAGE_CONFIDENCE_THRESHOLD = 50.0

_STATUS_AFTER_STAGE = {
    "research_validation": ("validating", "연구 검증"),
    "talent_mobility": ("talent_moving", "인재 이동·창업 확인"),
    "capital_formation": ("capital_forming", "자본 형성 확인"),
    "infrastructure_bottleneck": ("bottleneck_visible", "인프라 병목 가시화"),
    "earnings_confirmation": ("earnings_confirmed", "상장사 실적 확인"),
}


def _round_score(value: float) -> float:
    return round(max(0.0, min(100.0, value)), 2)


def _assess_stage(stage: str, evidence: list[Evidence]) -> StageAssessment:
    if not evidence:
        return StageAssessment(
            stage=stage,
            score=0.0,
            net_signal=0.0,
            confidence=0.0,
            evidence_count=0,
            distinct_source_count=0,
            positive_count=0,
            neutral_count=0,
            negative_count=0,
            evidence_ids=(),
            passed=False,
        )

    signals = [row.signed_signal for row in evidence]
    net_signal = max(-100.0, min(100.0, fmean(signals) * 100.0))
    score = _round_score(max(0.0, net_signal))
    domains = {row.source_domain for row in evidence if row.source_domain}
    quantity = min(1.0, len(domains) / 2.0)
    quality = fmean(row.reliability for row in evidence)
    absolute_total = sum(abs(value) for value in signals)
    agreement = abs(sum(signals)) / absolute_total if absolute_total else 1.0
    confidence = 100.0 * (0.55 * quantity + 0.45 * quality) * (0.70 + 0.30 * agreement)
    confidence = _round_score(confidence)
    passed = score >= STAGE_SCORE_THRESHOLD and confidence >= STAGE_CONFIDENCE_THRESHOLD
    return StageAssessment(
        stage=stage,
        score=score,
        net_signal=round(net_signal, 2),
        confidence=confidence,
        evidence_count=len(evidence),
        distinct_source_count=len(domains),
        positive_count=sum(row.direction == "positive" for row in evidence),
        neutral_count=sum(row.direction == "neutral" for row in evidence),
        negative_count=sum(row.direction == "negative" for row in evidence),
        evidence_ids=tuple(sorted(row.evidence_id for row in evidence)),
        passed=passed,
    )


def _assess_companies(theme: ThemeInput, available: dict[str, Evidence]) -> tuple[CompanyAssessment, ...]:
    result: list[CompanyAssessment] = []
    for link in theme.public_companies:
        linked = [available[evidence_id] for evidence_id in link.evidence_ids if evidence_id in available]
        unavailable = tuple(sorted(set(link.evidence_ids) - set(available)))
        if linked:
            evidence_strength = fmean(row.strength * row.reliability for row in linked)
            link_strength = _round_score(100.0 * evidence_strength * DIRECTNESS_WEIGHTS[link.directness])
        else:
            link_strength = 0.0
        result.append(
            CompanyAssessment(
                ticker=link.ticker,
                market=link.market,
                company_name=link.company_name,
                role=link.role,
                directness=link.directness,
                thesis=link.thesis,
                link_strength=link_strength,
                evidence_ids=tuple(row.evidence_id for row in linked),
                unavailable_evidence_ids=unavailable,
                positive_count=sum(row.direction == "positive" for row in linked),
                negative_count=sum(row.direction == "negative" for row in linked),
            )
        )
    return tuple(sorted(result, key=lambda row: (-row.link_strength, row.market, row.ticker)))


def _data_gaps(
    stages: tuple[StageAssessment, ...],
    evidence: tuple[Evidence, ...],
    excluded: tuple[ExcludedEvidence, ...],
    companies: tuple[CompanyAssessment, ...],
) -> tuple[str, ...]:
    gaps: list[str] = []
    for stage in stages:
        label = STAGE_LABELS[stage.stage]
        if stage.evidence_count == 0:
            gaps.append(f"{label}: 기준일 현재 사용 가능한 근거가 없습니다.")
        elif stage.score < STAGE_SCORE_THRESHOLD:
            gaps.append(f"{label}: 순신호 {stage.net_signal:.2f}점으로 단계 통과 기준에 미달합니다.")
        elif stage.confidence < STAGE_CONFIDENCE_THRESHOLD:
            gaps.append(f"{label}: 독립 출처 또는 출처 품질이 부족해 확신도 기준에 미달합니다.")
    if evidence and not any(row.direction == "negative" for row in evidence):
        gaps.append("반증·부정 근거가 없어 낙관 편향을 별도로 점검해야 합니다.")
    if excluded:
        gaps.append(f"기준일 이후에 알려진 근거 {len(excluded)}건을 사후정보 방지를 위해 제외했습니다.")
    if not companies:
        gaps.append("근거와 연결된 상장사가 없습니다.")
    for company in companies:
        if company.unavailable_evidence_ids:
            gaps.append(
                f"{company.market}:{company.ticker}: 기준일에 사용할 수 없는 연결 근거 "
                f"{', '.join(company.unavailable_evidence_ids)}"
            )
    return tuple(gaps)


def analyze_theme(theme: ThemeInput) -> RadarReport:
    """Analyze one validated theme without I/O or external calls."""
    included = tuple(
        sorted(
            (row for row in theme.evidence if row.known_at <= theme.as_of),
            key=lambda row: (row.event_date, row.known_at, row.evidence_id),
        )
    )
    excluded = tuple(
        ExcludedEvidence(
            evidence_id=row.evidence_id,
            reason="not_known_as_of",
            known_at=row.known_at.isoformat(),
        )
        for row in sorted(theme.evidence, key=lambda row: (row.known_at, row.evidence_id))
        if row.known_at > theme.as_of
    )
    by_stage = {stage: [row for row in included if row.stage == stage] for stage in STAGE_ORDER}
    stages = tuple(_assess_stage(stage, by_stage[stage]) for stage in STAGE_ORDER)

    status = "emerging"
    status_label = "초기 관찰"
    for assessment in stages:
        if not assessment.passed:
            break
        status, status_label = _STATUS_AFTER_STAGE[assessment.stage]

    chain_score = _round_score(sum(row.score * STAGE_WEIGHTS[row.stage] for row in stages))
    confidence = _round_score(sum(row.confidence * STAGE_WEIGHTS[row.stage] for row in stages))
    available = {row.evidence_id: row for row in included}
    companies = _assess_companies(theme, available)
    gaps = _data_gaps(stages, included, excluded, companies)
    methodology = {
        "stage_order": list(STAGE_ORDER),
        "stage_weights": dict(STAGE_WEIGHTS),
        "stage_score_threshold": STAGE_SCORE_THRESHOLD,
        "stage_confidence_threshold": STAGE_CONFIDENCE_THRESHOLD,
        "source_reliability": dict(SOURCE_RELIABILITY),
        "lookahead_rule": "Include evidence only when known_at <= as_of.",
        "score_formula": "mean(direction * strength * source_reliability) * 100, floored at 0",
        "confidence_formula": "source-domain diversity, source quality, and evidence agreement",
        "company_link_formula": "mean(strength * source_reliability) * directness_weight * 100",
        "interpretation": "Chain and link scores measure evidence maturity/connection, not expected return or valuation.",
    }
    return RadarReport(
        theme_id=theme.theme_id,
        name=theme.name,
        thesis=theme.thesis,
        as_of=theme.as_of.isoformat(),
        status=status,
        status_label=status_label,
        chain_score=chain_score,
        confidence=confidence,
        stages=stages,
        public_companies=companies,
        evidence=included,
        excluded_evidence=excluded,
        data_gaps=gaps,
        limitations=theme.limitations,
        methodology=methodology,
    )
