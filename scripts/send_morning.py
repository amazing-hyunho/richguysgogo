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
    parser = argparse.ArgumentParser(description="Send morning brief to Telegram.")
    parser.add_argument(
        "--include-report",
        action="store_true",
        help="Append detailed runs/.../report.md after the brief.",
    )
    args = parser.parse_args()

    runs_dir = ROOT_DIR / "runs"
    latest_dir = _latest_run_dir(runs_dir)
    if latest_dir is None:
        print("No runs found.")
        return

    snapshot_path = latest_dir / "snapshot.json"
    committee_path = latest_dir / "committee_result.json"
    report_path = latest_dir / "report.md"

    if not snapshot_path.exists():
        print("snapshot.json not found.")
        return

    snapshot = json.loads(snapshot_path.read_text(encoding="utf-8"))
    committee = json.loads(committee_path.read_text(encoding="utf-8")) if committee_path.exists() else None
    report_text = report_path.read_text(encoding="utf-8") if (args.include_report and report_path.exists()) else ""

    text = _build_morning_brief(snapshot=snapshot, committee=committee, report_text=report_text)
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


def _build_morning_brief(snapshot: dict, committee: dict | None, report_text: str) -> str:
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
    lines.append(f"- run: {snapshot.get('market_summary', {}).get('note', 'n/a')}")
    lines.append(f"- 상세리포트: {'포함' if report_text.strip() else '미포함'}")
    lines.append("")

    lines.append("[Global Markets]")
    lines.append(
        f"- KR: KOSPI {_fmt(kr.get('kospi_pct'), 2, '%')}, KOSDAQ {_fmt(kr.get('kosdaq_pct'), 2, '%')}"
    )
    lines.append(
        f"- US: S&P500 {_fmt(us.get('sp500_pct'), 2, '%')}, NASDAQ {_fmt(us.get('nasdaq_pct'), 2, '%')}, DOW {_fmt(us.get('dow_pct'), 2, '%')}"
    )
    lines.append(
        f"- FX: USD/KRW {_fmt(fx.get('usdkrw'), 2)} (Δ {_fmt(fx.get('usdkrw_pct'), 2, '%')})"
    )
    lines.append(f"- VIX: {_fmt(vol.get('vix'), 1)}")
    lines.append("")

    lines.append("[Daily Macro]")
    lines.append(
        f"- US10Y {_fmt(daily.get('us10y'), 2, '%')} / US2Y {_fmt(daily.get('us2y'), 2, '%')} / 2-10 {_fmt(daily.get('spread_2_10'), 2, '%p')}"
    )
    lines.append(
        f"- DXY {_fmt(daily.get('dxy'), 2)} / USDKRW {_fmt(daily.get('usdkrw'), 2)} / VIX {_fmt(daily.get('vix'), 1)}"
    )
    lines.append("")

    lines.append("[Monthly Macro]")
    lines.append(f"- Unemployment {_fmt(monthly.get('unemployment_rate'), 2, '%')}")
    lines.append(
        f"- CPI YoY {_fmt(monthly.get('cpi_yoy'), 2, '%')} / Core CPI YoY {_fmt(monthly.get('core_cpi_yoy'), 2, '%')} / PCE YoY {_fmt(monthly.get('pce_yoy'), 2, '%')}"
    )
    lines.append(f"- PMI {_fmt(monthly.get('pmi'), 1)}")
    lines.append(
        f"- Wage level {_fmt(monthly.get('wage_level'), 2)} / Wage YoY {_fmt(monthly.get('wage_yoy'), 2, '%')}"
    )
    lines.append("")

    lines.append("[Quarterly Macro]")
    lines.append(f"- Real GDP {_fmt(quarterly.get('real_gdp'), 2)}")
    lines.append(f"- GDP QoQ ann. {_fmt(quarterly.get('gdp_qoq_annualized'), 2, '%')}")
    lines.append("")

    lines.append("[Structural]")
    lines.append(f"- Fed Funds {_fmt(structural.get('fed_funds_rate'), 2, '%')}")
    lines.append(f"- Real rate {_fmt(structural.get('real_rate'), 2, '%')}")
    lines.append("")

    if committee:
        lines.append("[Committee]")
        consensus = committee.get("consensus")
        if consensus:
            lines.append(f"- Consensus: {consensus}")
        key_points = committee.get("key_points") or []
        for kp in key_points[:3]:
            point = kp.get("point")
            if point:
                lines.append(f"- {point}")
        lines.append("")

    if report_text.strip():
        lines.append("-----")
        lines.append("[상세 리포트]")
        lines.append(report_text.strip())

    return "\n".join(lines)


if __name__ == "__main__":
    main()
