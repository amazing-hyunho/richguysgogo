from __future__ import annotations

# Morning sender for latest report markdown.

import json
import argparse
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from committee.adapters.telegram_sender import send_report


def main() -> None:
    """Send a readable morning brief via Telegram or console.

    We keep the nightly pipeline artifacts intact and simply format them:
    - snapshot.json: indicators (markets + macro daily/monthly/quarterly/structural)
    - committee_result.json: consensus + key points
    - report.md: optional detailed report (off by default)
    """
    parser = argparse.ArgumentParser(description="아침 브리프를 텔레그램으로 전송합니다.")
    parser.add_argument(
        "--include-report",
        action="store_true",
        help="브리프 뒤에 runs/.../report.md를 덧붙입니다.",
    )
    args = parser.parse_args()

    runs_dir = ROOT_DIR / "runs"
    latest_dir = _latest_run_dir(runs_dir)
    if latest_dir is None:
        print("실행 결과가 없습니다.")
        return

    snapshot_path = latest_dir / "snapshot.json"
    stances_path = latest_dir / "stances.json"
    committee_path = latest_dir / "committee_result.json"
    report_path = latest_dir / "report.md"

    if not snapshot_path.exists():
        print("snapshot.json을 찾을 수 없습니다.")
        return

    snapshot = json.loads(snapshot_path.read_text(encoding="utf-8"))
    stances = json.loads(stances_path.read_text(encoding="utf-8")) if stances_path.exists() else []
    committee = json.loads(committee_path.read_text(encoding="utf-8")) if committee_path.exists() else None
    report_text = report_path.read_text(encoding="utf-8") if (args.include_report and report_path.exists()) else ""

    text = _build_morning_brief(
        snapshot=snapshot,
        stances=stances,
        committee=committee,
        report_text=report_text,
    )
    send_report(text)


def _latest_run_dir(runs_dir: Path) -> Path | None:
    """Return the latest run directory by name."""
    if not runs_dir.exists():
        return None
    dirs = [path for path in runs_dir.iterdir() if path.is_dir()]
    if not dirs:
        return None
    return sorted(dirs, key=lambda path: path.name)[-1]


def _fmt(value, digits: int = 2, suffix: str = "") -> str:
    """Format a number or None for display."""
    if value is None:
        return "n/a"
    try:
        return f"{float(value):.{digits}f}{suffix}"
    except Exception:
        return "n/a"


def _build_morning_brief(snapshot: dict, stances: list, committee: dict | None, report_text: str) -> str:
    """Build a readable text brief from run artifacts."""
    # Snapshot structure is stable, but indicators may be missing (NULL/None).
    markets = snapshot.get("markets", {}) or {}
    kr = (markets.get("kr") or {}) if isinstance(markets, dict) else {}
    us = (markets.get("us") or {}) if isinstance(markets, dict) else {}
    fx = (markets.get("fx") or {}) if isinstance(markets, dict) else {}
    vol = (markets.get("volatility") or {}) if isinstance(markets, dict) else {}

    macro = snapshot.get("macro") or {}
    daily = (macro.get("daily") or {}) if isinstance(macro, dict) else {}
    monthly = (macro.get("monthly") or {}) if isinstance(macro, dict) else {}
    quarterly = (macro.get("quarterly") or {}) if isinstance(macro, dict) else {}
    structural = (macro.get("structural") or {}) if isinstance(macro, dict) else {}

    lines: list[str] = []
    lines.append("오늘의 데일리 브리프")
    lines.append(f"- 요약: {snapshot.get('market_summary', {}).get('note', 'n/a')}")
    lines.append(f"- 상세 리포트: {'포함' if report_text.strip() else '미포함'}")
    lines.append("")

    lines.append("[글로벌 시장]")
    lines.append(
        f"- 국내: KOSPI {_fmt(kr.get('kospi_pct'), 2, '%')}, KOSDAQ {_fmt(kr.get('kosdaq_pct'), 2, '%')}"
    )
    lines.append(
        f"- 미국: S&P500 {_fmt(us.get('sp500_pct'), 2, '%')}, NASDAQ {_fmt(us.get('nasdaq_pct'), 2, '%')}, DOW {_fmt(us.get('dow_pct'), 2, '%')}"
    )
    lines.append(
        f"- 환율: USD/KRW {_fmt(fx.get('usdkrw'), 2)} (Δ {_fmt(fx.get('usdkrw_pct'), 2, '%')})"
    )
    lines.append(f"- VIX: {_fmt(vol.get('vix'), 1)}")
    lines.append("")

    lines.append("[일간 매크로]")
    lines.append(
        f"- 미10년 {_fmt(daily.get('us10y'), 2, '%')} / 미2년 {_fmt(daily.get('us2y'), 2, '%')} / 2-10 {_fmt(daily.get('spread_2_10'), 2, '%p')}"
    )
    lines.append(
        f"- DXY {_fmt(daily.get('dxy'), 2)} / USDKRW {_fmt(daily.get('usdkrw'), 2)} / VIX {_fmt(daily.get('vix'), 1)}"
    )
    lines.append("")

    lines.append("[월간 매크로]")
    lines.append(f"- 실업률 {_fmt(monthly.get('unemployment_rate'), 2, '%')}")
    lines.append(
        f"- CPI YoY {_fmt(monthly.get('cpi_yoy'), 2, '%')} / Core CPI YoY {_fmt(monthly.get('core_cpi_yoy'), 2, '%')} / PCE YoY {_fmt(monthly.get('pce_yoy'), 2, '%')}"
    )
    lines.append(f"- PMI {_fmt(monthly.get('pmi'), 1)}")
    lines.append(
        f"- 임금 레벨 {_fmt(monthly.get('wage_level'), 2)} / 임금 YoY {_fmt(monthly.get('wage_yoy'), 2, '%')}"
    )
    lines.append("")

    lines.append("[분기 매크로]")
    lines.append(f"- 실질 GDP {_fmt(quarterly.get('real_gdp'), 2)}")
    lines.append(f"- GDP QoQ 연율 {_fmt(quarterly.get('gdp_qoq_annualized'), 2, '%')}")
    lines.append("")

    lines.append("[구조 지표]")
    lines.append(f"- 기준금리 {_fmt(structural.get('fed_funds_rate'), 2, '%')}")
    lines.append(f"- 실질금리 {_fmt(structural.get('real_rate'), 2, '%')}")
    lines.append("")

    if committee:
        lines.append("[위원회]")
        consensus = committee.get("consensus")
        if consensus:
            lines.append(f"- 합의: {consensus}")
        key_points = committee.get("key_points") or []
        for kp in key_points[:3]:
            point = kp.get("point")
            if point:
                lines.append(f"- {point}")
        lines.append("")

    if stances:
        lines.append("[AI 한줄 의견]")
        for stance in stances:
            agent = _agent_label(stance.get("agent_name"))
            comment = stance.get("korean_comment")
            if agent and comment:
                lines.append(f"- {agent}: {comment}")
        lines.append("")

        lines.append("[AI 핵심 주장]")
        for stance in stances:
            agent = _agent_label(stance.get("agent_name"))
            claims = stance.get("core_claims") or []
            if not agent:
                continue
            lines.append(f"- {agent}:")
            for claim in claims:
                lines.append(f"  · {claim}")
        lines.append("")

    if report_text.strip():
        lines.append("-----")
        lines.append("[상세 리포트]")
        lines.append(report_text.strip())

    return "\n".join(lines)


def _agent_label(agent_name: str | None) -> str:
    """Map agent identifiers to Korean labels."""
    mapping = {
        "macro": "매크로",
        "flow": "수급",
        "sector": "섹터",
        "risk": "리스크",
    }
    return mapping.get(agent_name or "", agent_name or "")


if __name__ == "__main__":
    main()
