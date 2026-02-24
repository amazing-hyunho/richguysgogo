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
    """Render a minimal markdown report for human review."""
    def _fmt(value: float | None, digits: int = 2, suffix: str = "") -> str:
        if value is None:
            return "n/a"
        try:
            return f"{float(value):.{digits}f}{suffix}"
        except Exception:
            return "n/a"

    lines = [
        "# 데일리 AI 투자위원회",
        "",
        f"날짜: {report.market_date}",
        f"생성 시각: {report.generated_at}",
        "",
        "## 합의 결과",
        _translate_sentence(report.committee_result.consensus),
        "",
        "## 핵심 포인트",
    ]
    for key_point in report.committee_result.key_points:
        sources = ", ".join(key_point.sources)
        lines.append(f"- {_translate_phrase(key_point.point)} (출처: {sources})")

    lines.extend(["", "## AI 한줄 의견"])
    for stance in report.stances:
        agent_label = _agent_label(stance.agent_name.value)
        lines.append(f"- {agent_label}: {stance.korean_comment}")

    lines.extend(["", "## AI 핵심 주장"])
    for stance in report.stances:
        agent_label = _agent_label(stance.agent_name.value)
        lines.append(f"### {agent_label}")
        for claim in stance.core_claims:
            lines.append(f"- {claim}")

    lines.extend(["", "## AI 원문 응답"])
    for stance in report.stances:
        agent_label = _agent_label(stance.agent_name.value)
        lines.append(f"### {agent_label}")
        if stance.raw_response:
            lines.append("```")
            lines.extend(stance.raw_response.splitlines())
            lines.append("```")
        else:
            lines.append("(stub or raw response unavailable)")

    tag_counts = {"RISK_ON": 0, "NEUTRAL": 0, "RISK_OFF": 0}
    for stance in report.stances:
        tag_counts[stance.regime_tag.value] = tag_counts.get(stance.regime_tag.value, 0) + 1
    lines.append("")
    lines.append(
        "국면 투표: "
        f"NEUTRAL={tag_counts['NEUTRAL']}, "
        f"RISK_ON={tag_counts['RISK_ON']}, "
        f"RISK_OFF={tag_counts['RISK_OFF']}"
    )
    majority_tag = max(tag_counts, key=lambda key: tag_counts[key])
    lines.append(f"요약: 현재 국면은 {majority_tag}로 판단됩니다.")

    lines.extend(["", "## 이견"])
    for disagreement in report.committee_result.disagreements:
        agents = ", ".join(disagreement.minority_agents)
        lines.append(
            f"- {_translate_phrase(disagreement.topic)}: 다수={disagreement.majority}, "
            f"소수={disagreement.minority}, 에이전트=[{agents}]. "
            f"{_translate_sentence(disagreement.why_it_matters)}"
        )

    lines.extend(["", "## 운영 가이드"])
    for guidance in report.committee_result.ops_guidance:
        lines.append(
            f"- [{guidance.level}/{_translate_level(guidance.level.value)}] "
            f"{_translate_sentence(guidance.text)}"
        )

    lines.extend(["", "## 글로벌 시장"])
    m = report.snapshot.markets
    lines.append(
        f"국내: KOSPI {m.kr.kospi_pct:+.2f}%, KOSDAQ {m.kr.kosdaq_pct:+.2f}%"
    )
    lines.append(
        f"미국: S&P500 {m.us.sp500_pct:+.2f}%, NASDAQ {m.us.nasdaq_pct:+.2f}%, DOW {m.us.dow_pct:+.2f}%"
    )
    lines.append(f"환율: USD/KRW {m.fx.usdkrw:.2f} ({m.fx.usdkrw_pct:+.2f}%)")

    lines.extend(["", "## 시장 지표"])
    s = report.snapshot.market_summary
    lines.append(f"- KOSPI 일일 등락: **{s.kospi_change_pct:+.2f}%**")
    lines.append(f"- USD/KRW: **{s.usdkrw:.2f}**")
    lines.append(f"- 요약: {s.note}")

    lines.extend(["", "## 수급 (억원, 순매수)"])
    f = report.snapshot.flow_summary
    lines.append(f"- 외국인: **{f.foreign_net:+.0f}** / 기관: **{f.institution_net:+.0f}** / 개인: **{f.retail_net:+.0f}**")
    lines.append(f"- 비고: {f.note}")

    # Optional: Korean market flow breakdown (KOSPI/KOSDAQ) via PyKRX.
    lines.extend(["", "## 한국 수급 (KOSPI/KOSDAQ, 억원 순매수)"])
    kf = report.snapshot.korean_market_flow
    if kf is None:
        lines.append("- 데이터: unavailable (PyKRX 미설치/실패/휴장일 등)")
    else:
        lines.append(f"- 기준일: {kf.date}")
        for mk in ["KOSPI", "KOSDAQ"]:
            inv = kf.market.get(mk)
            if inv is None:
                lines.append(f"- {mk}: n/a")
                continue
            lines.append(
                f"- {mk}: 외국인 **{inv.foreign:+d}** / 기관 **{inv.institution:+d}** / 개인 **{inv.individual:+d}**"
            )

    # Optional macro block (daily/monthly/quarterly/structural). Missing values are shown as n/a.
    if report.snapshot.macro is not None:
        macro = report.snapshot.macro
        lines.extend(["", "## 매크로 (요약)"])

        d = macro.daily
        lines.append(
            f"- 일간: 미10년 {_fmt(d.us10y, 2, '%')} / 미2년 {_fmt(d.us2y, 2, '%')} / 2-10 {_fmt(d.spread_2_10, 2, '%p')}"
        )
        lines.append(
            f"        DXY {_fmt(d.dxy, 2)} / USDKRW {_fmt(d.usdkrw, 2)} / VIX {_fmt(d.vix, 1)}"
        )

        mth = macro.monthly
        lines.append(
            f"- 월간: 실업률 {_fmt(mth.unemployment_rate, 2, '%')}, "
            f"CPI YoY {_fmt(mth.cpi_yoy, 2, '%')}, Core CPI YoY {_fmt(mth.core_cpi_yoy, 2, '%')}, "
            f"PCE YoY {_fmt(mth.pce_yoy, 2, '%')}, PMI {_fmt(mth.pmi, 1)}"
        )
        lines.append(
            f"          임금 레벨 {_fmt(mth.wage_level, 2)}, 임금 YoY {_fmt(mth.wage_yoy, 2, '%')}"
        )

        q = macro.quarterly
        lines.append(
            f"- 분기: 실질 GDP {_fmt(q.real_gdp, 2)}, GDP QoQ 연율 {_fmt(q.gdp_qoq_annualized, 2, '%')}"
        )

        st = macro.structural
        lines.append(
            f"- 구조: 기준금리 {_fmt(st.fed_funds_rate, 2, '%')}, 실질금리 {_fmt(st.real_rate, 2, '%')}"
        )

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
