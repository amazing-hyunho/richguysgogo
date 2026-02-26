from __future__ import annotations

# Morning sender for latest report markdown.

import argparse
import json
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
        help="브리프 뒤에 runs/.../report.md를 텔레그램 친화 형태로 덧붙입니다.",
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


def _fmt_signed(value, digits: int = 2, suffix: str = "") -> str:
    """Format signed numbers with explicit +/- prefix."""
    if value is None:
        return "n/a"
    try:
        return f"{float(value):+.{digits}f}{suffix}"
    except Exception:
        return "n/a"


def _build_morning_brief(snapshot: dict, stances: list, committee: dict | None, report_text: str) -> str:
    """Build a user-friendly morning brief for Telegram reading."""
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
    lines.append("📌 오늘의 데일리 브리프")
    lines.append(f"- 시장 요약: {snapshot.get('market_summary', {}).get('note', 'n/a')}")
    lines.append(f"- 상세 리포트: {'포함됨' if report_text.strip() else '미포함'}")
    lines.append("")

    lines.append("🧭 위원회 결론")
    if committee and committee.get("consensus"):
        lines.append(f"- 합의: {committee.get('consensus')}")
        key_points = committee.get("key_points") or []
        for kp in key_points[:3]:
            point = kp.get("point")
            if point:
                lines.append(f"- 핵심: {point}")
    else:
        lines.append("- 합의 결과 없음")
    lines.append("")

    lines.append("🌍 시장 체크")
    lines.append(f"- 국내: KOSPI {_fmt_signed(kr.get('kospi_pct'), 2, '%')} / KOSDAQ {_fmt_signed(kr.get('kosdaq_pct'), 2, '%')}")
    lines.append(
        f"- 미국: S&P500 {_fmt_signed(us.get('sp500_pct'), 2, '%')} / NASDAQ {_fmt_signed(us.get('nasdaq_pct'), 2, '%')} / DOW {_fmt_signed(us.get('dow_pct'), 2, '%')}"
    )
    lines.append(f"- 환율: USD/KRW {_fmt(fx.get('usdkrw'), 2)} (일변화 {_fmt_signed(fx.get('usdkrw_pct'), 2, '%')})")
    lines.append(f"- 변동성: VIX {_fmt(vol.get('vix'), 1)}")
    lines.append("")

    lines.append("🏦 매크로 체크")
    lines.append(
        f"- 금리: 미10년 {_fmt(daily.get('us10y'), 2, '%')} / 미2년 {_fmt(daily.get('us2y'), 2, '%')} / 2-10 {_fmt(daily.get('spread_2_10'), 2, '%p')}"
    )
    lines.append(f"- 달러/변동성: DXY {_fmt(daily.get('dxy'), 2)} / VIX {_fmt(daily.get('vix'), 1)}")
    lines.append(
        f"- 물가/경기: 실업률 {_fmt(monthly.get('unemployment_rate'), 2, '%')} / CPI {_fmt(monthly.get('cpi_yoy'), 2, '%')} / PMI {_fmt(monthly.get('pmi'), 1)}"
    )
    lines.append(f"- 성장: GDP QoQ 연율 {_fmt(quarterly.get('gdp_qoq_annualized'), 2, '%')}")
    lines.append(f"- 정책: 기준금리 {_fmt(structural.get('fed_funds_rate'), 2, '%')} / 실질금리 {_fmt(structural.get('real_rate'), 2, '%')}")
    lines.append("")

    if stances:
        lines.append("🤖 AI 에이전트 한줄 코멘트")
        has_comment = False
        for stance in stances:
            agent = _agent_label(stance.get("agent_name"))
            comment = stance.get("korean_comment")
            if agent and comment:
                lines.append(f"- {agent}: {comment}")
                has_comment = True
        if not has_comment:
            lines.append("- 코멘트 없음")
        lines.append("")

    if report_text.strip():
        lines.extend(_format_report_for_telegram(report_text))

    return "\n".join(lines)


def _format_report_for_telegram(report_text: str) -> list[str]:
    """Reformat report.md to a Telegram-friendly compact view."""
    lines = ["📝 상세 리포트 (가독성 모드)", "- report.md를 핵심 섹션 중심으로 재정렬해 제공합니다."]

    section_map = _parse_markdown_sections(report_text)
    preferred_groups = [
        ("한눈에 보기", ["1) 한눈에 보기", "합의 결과"]),
        ("운영 가이드", ["2) 운영 가이드", "운영 가이드"]),
        ("위원회 핵심 포인트", ["4) 위원회 핵심 포인트", "핵심 포인트"]),
        ("AI 에이전트 의견", ["5) AI 에이전트 의견", "AI 한줄 의견", "AI 핵심 주장"]),
        ("이견 사항", ["6) 이견 사항", "이견"]),
    ]

    for display_name, candidates in preferred_groups:
        matched_contents = [section_map[name] for name in candidates if name in section_map]
        if not matched_contents:
            continue

        merged: list[str] = []
        for content in matched_contents:
            merged.extend(content)

        lines.append("")
        lines.append(f"[{display_name}]")
        cleaned = _cleanup_section_lines(merged)
        if display_name == "AI 에이전트 의견":
            cleaned = _compress_agent_section(cleaned)
        lines.extend(cleaned[:40])

    lines.append("")
    lines.append("- 참고: 원문 전체는 runs/YYYY-MM-DD/report.md 파일에서 확인할 수 있습니다.")
    return lines


def _parse_markdown_sections(report_text: str) -> dict[str, list[str]]:
    """Parse markdown '## section' blocks into dictionary."""
    sections: dict[str, list[str]] = {}
    current = ""
    for raw in report_text.splitlines():
        line = raw.rstrip()
        if line.startswith("## "):
            current = line.replace("## ", "", 1).strip()
            sections[current] = []
            continue
        if current:
            sections[current].append(line)
    return sections


def _cleanup_section_lines(lines: list[str]) -> list[str]:
    """Remove noisy markdown markers while preserving readability."""
    cleaned: list[str] = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("```"):
            continue
        cleaned.append(stripped)
    return cleaned


def _compress_agent_section(lines: list[str]) -> list[str]:
    """Keep AI agent section compact for Telegram consumption."""
    compressed: list[str] = []
    claim_count = 0
    for line in lines:
        if line.startswith("### "):
            claim_count = 0
            compressed.append(line)
            continue
        if line.startswith("- 핵심 주장:"):
            claim_count += 1
            if claim_count > 2:
                continue
        compressed.append(line)
    return compressed


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
