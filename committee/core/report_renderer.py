from __future__ import annotations

# Report assembly and rendering utilities.

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import List

from pydantic import BaseModel, Field

from committee.schemas.committee_result import CommitteeResult
from committee.schemas.snapshot import Snapshot
from committee.schemas.stance import Stance


class Report(BaseModel):
    """Structured report for daily output."""
    generated_at: str = Field(..., description="ISO-8601 timestamp (UTC).")
    market_date: str = Field(..., description="Market date (YYYY-MM-DD).")
    snapshot: Snapshot
    stances: List[Stance]
    committee_result: CommitteeResult

    class Config:
        extra = "forbid"


def build_report(
    market_date: str,
    snapshot: Snapshot,
    stances: List[Stance],
    committee_result: CommitteeResult,
) -> Report:
    """Build a report from pipeline artifacts."""
    return Report(
        generated_at=datetime.now(timezone.utc).isoformat(),
        market_date=market_date,
        snapshot=snapshot,
        stances=stances,
        committee_result=committee_result,
    )


def render_report(report: Report, output_path: Path) -> None:
    """Write report JSON to disk."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(report.model_dump(), handle, ensure_ascii=False, indent=2)


def build_report_markdown(report: Report) -> str:
    """Render a structured markdown report focused on readability."""

    def _fmt(value: float | None, digits: int = 2, suffix: str = "") -> str:
        if value is None:
            return "n/a"
        try:
            return f"{float(value):.{digits}f}{suffix}"
        except Exception:
            return "n/a"

    def _fmt_signed(value: float | None, digits: int = 2, suffix: str = "") -> str:
        if value is None:
            return "n/a"
        try:
            return f"{float(value):+.{digits}f}{suffix}"
        except Exception:
            return "n/a"

    lines = [
        "# 데일리 AI 투자위원회 리포트",
        "",
        f"- 시장 기준일: **{report.market_date}**",
        f"- 생성 시각(UTC): `{report.generated_at}`",
        "",
        "## 1) 한눈에 보기",
        f"- **위원회 합의**: {_translate_sentence(report.committee_result.consensus)}",
    ]

    tag_counts = {"RISK_ON": 0, "NEUTRAL": 0, "RISK_OFF": 0}
    for stance in report.stances:
        tag_counts[stance.regime_tag.value] = tag_counts.get(stance.regime_tag.value, 0) + 1
    majority_tag = max(tag_counts, key=lambda key: tag_counts[key])
    lines.append(
        f"- **국면 투표**: NEUTRAL={tag_counts['NEUTRAL']}, RISK_ON={tag_counts['RISK_ON']}, RISK_OFF={tag_counts['RISK_OFF']}"
    )
    lines.append(f"- **다수 국면**: {majority_tag}")

    lines.extend(["", "## 2) 운영 가이드"])
    for guidance in report.committee_result.ops_guidance:
        lines.append(
            f"- [{guidance.level}/{_translate_level(guidance.level.value)}] {_translate_sentence(guidance.text)}"
        )

    lines.extend(["", "## 3) 시장/매크로 스냅샷"])
    m = report.snapshot.markets
    lines.append(
        f"- **국내 지수**: KOSPI {_fmt_signed(m.kr.kospi_pct, 2, '%')} / KOSDAQ {_fmt_signed(m.kr.kosdaq_pct, 2, '%')}"
    )
    lines.append(
        f"- **미국 지수**: S&P500 {_fmt_signed(m.us.sp500_pct, 2, '%')} / NASDAQ {_fmt_signed(m.us.nasdaq_pct, 2, '%')} / DOW {_fmt_signed(m.us.dow_pct, 2, '%')}"
    )
    lines.append(
        f"- **환율/변동성**: USD/KRW {_fmt(m.fx.usdkrw, 2)} ({_fmt_signed(m.fx.usdkrw_pct, 2, '%')}) / VIX {_fmt(m.volatility.vix, 1)}"
    )

    s = report.snapshot.market_summary
    f = report.snapshot.flow_summary
    lines.append(f"- **시장 요약 노트**: {s.note}")
    lines.append(f"- **수급 요약**: 외국인 {_fmt_signed(f.foreign_net, 0)}억 / 기관 {_fmt_signed(f.institution_net, 0)}억 / 개인 {_fmt_signed(f.retail_net, 0)}억")

    if report.snapshot.macro is not None:
        macro = report.snapshot.macro
        d = macro.daily
        mth = macro.monthly
        q = macro.quarterly
        st = macro.structural
        lines.append(
            f"- **일간 매크로**: 미10년 {_fmt(d.us10y, 2, '%')} / 미2년 {_fmt(d.us2y, 2, '%')} / 2-10 {_fmt(d.spread_2_10, 2, '%p')} / DXY {_fmt(d.dxy, 2)}"
        )
        lines.append(
            f"- **월간 매크로**: 실업률 {_fmt(mth.unemployment_rate, 2, '%')} / CPI YoY {_fmt(mth.cpi_yoy, 2, '%')} / Core CPI YoY {_fmt(mth.core_cpi_yoy, 2, '%')} / PMI {_fmt(mth.pmi, 1)}"
        )
        lines.append(f"- **분기/구조**: GDP QoQ 연율 {_fmt(q.gdp_qoq_annualized, 2, '%')} / 기준금리 {_fmt(st.fed_funds_rate, 2, '%')} / 실질금리 {_fmt(st.real_rate, 2, '%')}")

    lines.extend(["", "## 4) 위원회 핵심 포인트"])
    for key_point in report.committee_result.key_points:
        sources = ", ".join(key_point.sources)
        lines.append(f"- {_translate_phrase(key_point.point)}")
        lines.append(f"  ↳ 출처: `{sources}`")

    lines.extend(["", "## 5) AI 에이전트 의견"])
    for stance in report.stances:
        agent_label = _agent_label(stance.agent_name.value)
        lines.append(f"### {agent_label}")
        if stance.korean_comment:
            lines.append(f"- 한줄 요약: {stance.korean_comment}")
        lines.append(f"- 국면 태그: {stance.regime_tag.value} / 신뢰도: {stance.confidence.value}")
        for claim in stance.core_claims:
            lines.append(f"- 핵심 주장: {claim}")
        lines.append("")

    lines.extend(["## 6) 이견 사항"])
    if not report.committee_result.disagreements:
        lines.append("- 이견 없음")
    else:
        for disagreement in report.committee_result.disagreements:
            agents = ", ".join(disagreement.minority_agents)
            lines.append(
                f"- {_translate_phrase(disagreement.topic)}: 다수={disagreement.majority}, 소수={disagreement.minority}, 에이전트=[{agents}]"
            )
            lines.append(f"  - 의미: {_translate_sentence(disagreement.why_it_matters)}")

    lines.extend(["", "## 7) AI 원문 응답 (디버깅/검토용)"])
    for stance in report.stances:
        agent_label = _agent_label(stance.agent_name.value)
        lines.append(f"### {agent_label}")
        if stance.raw_response:
            lines.append("```text")
            lines.extend(stance.raw_response.splitlines())
            lines.append("```")
        else:
            lines.append("(stub or raw response unavailable)")

    return "\n".join(lines)


def _translate_level(level: str) -> str:
    """Translate ops guidance level to Korean."""
    return {
        "OK": "유지",
        "CAUTION": "주의",
        "AVOID": "회피",
    }.get(level, level)


def _translate_phrase(text: str) -> str:
    """Translate common fixed phrases for readability."""
    mapping = {
        "Majority regime tag": "다수 국면 태그",
        "Shared evidence focus": "공통 근거",
        "Regime tags": "국면 태그",
    }
    for key, value in mapping.items():
        if text.startswith(key):
            return text.replace(key, value, 1)
    return text


def _translate_sentence(text: str) -> str:
    """Translate known sentences or return original."""
    mapping = {
        "Committee agrees on a neutral stance with selective monitoring.": "위원회는 선별적 모니터링 하에 중립적 스탠스를 유지합니다.",
        "Committee maintains a neutral posture with selective positioning.": "위원회는 선별적 포지셔닝을 전제로 중립적 입장을 유지합니다.",
        "Committee adopts a defensive posture and reduces risk exposure.": "위원회는 방어적 입장을 채택하고 위험 노출을 줄입니다.",
        "No dissenting regime tags are present.": "다른 국면 태그의 이견은 없습니다.",
        "Minority risk regime can change positioning boundaries.": "소수 의견 국면은 포지션 경계에 영향을 줄 수 있습니다.",
        "Maintain balanced exposure.": "노출을 균형 있게 유지합니다.",
        "Keep risk limits tight.": "리스크 한도를 엄격히 유지합니다.",
        "Avoid aggressive leverage.": "과도한 레버리지는 피합니다.",
        "Keep watchlist tight and avoid overexposure.": "관심 종목을 좁게 유지하고 과도한 노출을 피합니다.",
        "Keep position sizes moderate.": "포지션 규모를 보수적으로 유지합니다.",
    }
    return mapping.get(text, text)


def _agent_label(agent_name: str) -> str:
    """Map agent identifiers to Korean labels."""
    mapping = {
        "macro": "매크로",
        "flow": "수급",
        "sector": "섹터",
        "risk": "리스크",
    }
    return mapping.get(agent_name, agent_name)
