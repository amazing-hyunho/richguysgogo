from __future__ import annotations

"""Human-readable Markdown rendering for radar reports."""

from committee.research_radar.models import RadarReport, STAGE_LABELS


_DIRECTION_LABELS = {"positive": "긍정", "neutral": "중립", "negative": "부정"}
_DIRECTNESS_LABELS = {"direct": "직접", "enabler": "핵심 공급", "adjacent": "인접", "speculative": "가설"}


def _cell(value: object) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ").strip()


def render_markdown(report: RadarReport) -> str:
    lines = [
        f"# Research-to-Market Radar — {report.name}",
        "",
        f"- 기준일: `{report.as_of}`",
        f"- 현재 단계: **{report.status_label}** (`{report.status}`)",
        f"- 체인 성숙도: **{report.chain_score:.2f}/100**",
        f"- 근거 확신도: **{report.confidence:.2f}/100**",
        f"- 핵심 가설: {_cell(report.thesis)}",
        "",
        "> 이 점수는 근거 체인의 성숙도와 상장사 연결 강도를 나타낼 뿐, 기대수익률·적정가치·매수 추천이 아닙니다.",
        "",
        "## 단계별 판정",
        "",
        "| 단계 | 점수 | 확신도 | 근거 | 독립 출처 | 판정 |",
        "|---|---:|---:|---:|---:|---|",
    ]
    for stage in report.stages:
        verdict = "통과" if stage.passed else "미통과"
        lines.append(
            f"| {STAGE_LABELS[stage.stage]} | {stage.score:.2f} | {stage.confidence:.2f} | "
            f"{stage.evidence_count} | {stage.distinct_source_count} | {verdict} |"
        )

    lines.extend(
        [
            "",
            "## 공개시장 연결고리",
            "",
            "| 종목 | 기업 | 역할 | 연결 유형 | 연결 강도 | 사용 근거 |",
            "|---|---|---|---|---:|---|",
        ]
    )
    if report.public_companies:
        for company in report.public_companies:
            ticker = f"{company.market}:{company.ticker}"
            evidence_ids = ", ".join(f"`{item}`" for item in company.evidence_ids) or "없음"
            lines.append(
                f"| {_cell(ticker)} | {_cell(company.company_name)} | {_cell(company.role)} | "
                f"{_DIRECTNESS_LABELS[company.directness]} | {company.link_strength:.2f} | {evidence_ids} |"
            )
            lines.append(f"|  |  | 가설 |  |  | {_cell(company.thesis)} |")
    else:
        lines.append("| - | - | - | - | 0.00 | 연결된 상장사 없음 |")

    lines.extend(
        [
            "",
            "## 증거 타임라인",
            "",
            "| 사건일 | 인지일 | 단계 | 방향 | 근거와 주장 | 출처 |",
            "|---|---|---|---|---|---|",
        ]
    )
    if report.evidence:
        for evidence in report.evidence:
            source = f"[{_cell(evidence.source_name)}]({evidence.source_url})"
            title_and_claim = f"**{_cell(evidence.title)}** — {_cell(evidence.claim)}"
            lines.append(
                f"| {evidence.event_date.isoformat()} | {evidence.known_at.isoformat()} | "
                f"{STAGE_LABELS[evidence.stage]} | {_DIRECTION_LABELS[evidence.direction]} | "
                f"{title_and_claim} | {source} |"
            )
    else:
        lines.append("| - | - | - | - | 기준일 현재 사용 가능한 근거 없음 | - |")

    lines.extend(["", "## 데이터 공백과 한계", ""])
    cautions = [*report.data_gaps, *report.limitations]
    if cautions:
        lines.extend(f"- {_cell(item)}" for item in cautions)
    else:
        lines.append("- 입력에 명시된 추가 한계가 없습니다.")

    if report.excluded_evidence:
        lines.extend(["", "### 기준일 이후라 제외한 근거", ""])
        lines.extend(
            f"- `{row.evidence_id}`: known_at={row.known_at} ({row.reason})"
            for row in report.excluded_evidence
        )

    lines.extend(
        [
            "",
            "## 판정 규칙",
            "",
            "- 단계 순서: 연구 검증 → 인재 이동·창업 → 자본 형성 → 인프라 병목 → 상장사 실적 확인",
            "- 단계 통과: 점수 60 이상이면서 확신도 50 이상",
            "- 시점 계약: `known_at <= as_of`인 근거만 사용",
            "- 체인 성숙도: 다섯 단계 점수의 고정 가중합",
            "- 상장사 연결 강도: 근거 품질·강도와 연결 유형을 반영하며 밸류에이션은 반영하지 않음",
            "",
        ]
    )
    return "\n".join(lines)
