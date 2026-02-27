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
    """Send a readable morning brief via Telegram or console."""
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

    text = _build_morning_brief(snapshot=snapshot, stances=stances, committee=committee, report_text=report_text)
    send_report(text)


def _latest_run_dir(runs_dir: Path) -> Path | None:
    if not runs_dir.exists():
        return None
    dirs = [path for path in runs_dir.iterdir() if path.is_dir()]
    if not dirs:
        return None
    return sorted(dirs, key=lambda path: path.name)[-1]


def _fmt(value, digits: int = 2, suffix: str = "") -> str:
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
    """Build a compact and readable morning brief for Telegram."""
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
    headlines = snapshot.get("news_headlines") or []

    lines: list[str] = []
    market_summary = snapshot.get("market_summary", {}) or {}
    lines.append("📌 오늘의 데일리 브리프")
    lines.append(f"- 시장 요약: {market_summary.get('note', 'n/a')}")
    lines.append(f"- 상세 리포트: {'포함됨' if report_text.strip() else '미포함'}")
    lines.append("")

    lines.append("🧭 의장 결정")
    if committee and committee.get("consensus"):
        lines.append(f"- 최종 결론: {_translate_sentence(committee.get('consensus'))}")
        majority_tag = _extract_majority_tag(committee)
        if majority_tag:
            lines.append(f"- 시장 국면 판단: {majority_tag} ({_regime_kr(majority_tag)})")
        for g in (committee.get("ops_guidance") or [])[:3]:
            lvl = g.get("level", "")
            txt = _translate_sentence(g.get("text", ""))
            lines.append(f"- 실행 원칙 [{_level_kr(lvl)}]: {txt}")

        key_points = [kp.get("point", "") for kp in (committee.get("key_points") or []) if kp.get("point")]
        translated_points = [_translate_key_point(point) for point in key_points[:2]]
        if translated_points:
            lines.append(f"- 근거 요약: {' / '.join(translated_points)}")
    else:
        lines.append("- 합의 결과 없음")
    lines.append("")

    lines.append("🗳️ 에이전트 투표 현황")
    vote = _vote_summary(stances)
    lines.append(f"- 전체: RISK_ON={vote['RISK_ON']}, NEUTRAL={vote['NEUTRAL']}, RISK_OFF={vote['RISK_OFF']}")
    lines.append("- 태그 설명: RISK_ON=위험자산 비중 확대, NEUTRAL=중립/선별 대응, RISK_OFF=방어적 운용")
    for stance in stances:
        agent = _agent_label(stance.get("agent_name"))
        tag = stance.get("regime_tag", "N/A")
        conf = stance.get("confidence", "N/A")
        lines.append(f"- {agent}: {tag} ({_regime_kr(tag)}), 신뢰도 {conf}")
    lines.append("")

    lines.append("🌍 시장 체크")
    lines.append(f"- 국내: KOSPI {_fmt_signed(kr.get('kospi_pct'), 2, '%')} / KOSDAQ {_fmt_signed(kr.get('kosdaq_pct'), 2, '%')}")
    lines.append(f"- 미국: S&P500 {_fmt_signed(us.get('sp500_pct'), 2, '%')} / NASDAQ {_fmt_signed(us.get('nasdaq_pct'), 2, '%')} / DOW {_fmt_signed(us.get('dow_pct'), 2, '%')}")
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

    lines.append("📰 헤드라인 기사")
    top_headlines = _top_headlines(headlines, limit=3)
    if top_headlines:
        for idx, headline in enumerate(top_headlines, start=1):
            lines.append(f"- {idx}. {headline}")
    else:
        lines.append("- 헤드라인 없음")
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


def _vote_summary(stances: list[dict]) -> dict[str, int]:
    counts = {"RISK_ON": 0, "NEUTRAL": 0, "RISK_OFF": 0}
    for stance in stances:
        tag = stance.get("regime_tag")
        if tag in counts:
            counts[tag] += 1
    return counts


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
    if not lines:
        return []

    cleaned: list[str] = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("```"):
            continue
        cleaned.append(stripped)
    return cleaned


def _translate_sentence(text: str) -> str:
    mapping = {
        "Committee agrees on a neutral stance with selective monitoring.": "위원회는 선별적 모니터링 하에 중립적 스탠스를 유지합니다.",
        "Committee maintains a neutral posture with selective positioning.": "위원회는 선별적 포지셔닝을 전제로 중립적 입장을 유지합니다.",
        "Committee adopts a defensive posture and reduces risk exposure.": "위원회는 방어적 입장을 채택하고 위험 노출을 줄입니다.",
        "Committee supports risk-on positioning with disciplined risk controls.": "위원회는 엄격한 리스크 통제를 전제로 위험자산 비중 확대를 지지합니다.",
        "Maintain balanced exposure.": "노출을 균형 있게 유지합니다.",
        "Keep risk limits tight.": "리스크 한도를 엄격히 유지합니다.",
        "Avoid aggressive leverage.": "과도한 레버리지는 피합니다.",
        "Lean into confirmed momentum leaders.": "확인된 모멘텀 주도주 중심으로 대응합니다.",
        "Size positions with volatility limits.": "변동성 한도를 기준으로 포지션 규모를 조절합니다.",
        "Avoid chasing overstretched breakouts.": "과열된 돌파 구간 추격 매수는 피합니다.",
        "Keep watchlist tight and avoid overexposure.": "관심 종목을 좁게 유지하고 과도한 노출을 피합니다.",
        "Keep position sizes moderate.": "포지션 규모를 보수적으로 유지합니다.",
    }
    return mapping.get(text, text)


def _level_kr(level: str) -> str:
    return {"OK": "유지", "CAUTION": "주의", "AVOID": "회피"}.get(level, level)


def _regime_kr(tag: str) -> str:
    return {
        "RISK_ON": "위험선호(비중 확대)",
        "NEUTRAL": "중립(선별 대응)",
        "RISK_OFF": "위험회피(방어적 운용)",
    }.get(tag, tag)
    return {"RISK_ON": "위험선호", "NEUTRAL": "중립", "RISK_OFF": "위험회피"}.get(tag, tag)


def _translate_key_point(text: str) -> str:
    mapping = {
        "Majority regime tag": "다수 국면",
        "Shared evidence focus": "공통 근거",
    }
    for key, value in mapping.items():
        if text.startswith(key):
            return text.replace(key, value, 1)
    return text.rstrip(".")


def _extract_majority_tag(committee: dict) -> str:
    for kp in committee.get("key_points") or []:
        point = kp.get("point", "")
        if point.startswith("Majority regime tag:"):
            return point.split(":", 1)[1].strip().rstrip(".")
    return ""


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
    mapping = {
        "macro": "매크로",
        "flow": "수급",
        "sector": "섹터",
        "risk": "리스크",
        "earnings": "이익모멘텀",
        "breadth": "브레드스",
        "liquidity": "유동성",
    }
    return mapping.get(agent_name or "", agent_name or "")


def _top_headlines(items: list, limit: int = 3) -> list[str]:
    """Extract top N headline strings with balanced global/domestic mix."""
    domestic: list[str] = []
    global_: list[str] = []

    for item in items:
        text = _headline_text(item)
        if not text:
            continue

        if _is_domestic_headline(text):
            domestic.append(text)
        else:
            global_.append(text)

    if limit <= 0:
        return []

    domestic_target = limit // 2
    global_target = limit // 2
    if limit % 2 == 1:
        # 홀수일 때는 국내 1개를 우선 배정해 균형을 최대한 맞춘다.
        domestic_target += 1

    selected = domestic[:domestic_target] + global_[:global_target]

    if len(selected) < limit:
        leftovers = domestic[domestic_target:] + global_[global_target:]
        selected.extend(leftovers[: limit - len(selected)])

    return selected


def _headline_text(item: object) -> str:
    if isinstance(item, str):
        return item.strip()
    if isinstance(item, dict):
        return str(item.get("title") or item.get("headline") or "").strip()
    return ""


def _is_domestic_headline(text: str) -> bool:
    lowered = text.lower()
    domestic_keywords = [
        "코스피",
        "코스닥",
        "한국",
        "국내",
        "원/달러",
        "원달러",
        "krx",
        "금감원",
        "한은",
        "서울",
        "삼성",
        "sk",
        "현대",
        "네이버",
        "카카오",
        "지디넷코리아",
        "연합뉴스",
        "조선일보",
        "중앙일보",
        "mbc",
        "kbs",
        "sbs",
        "jtbc",
    ]
    return any(keyword in lowered for keyword in domestic_keywords)


if __name__ == "__main__":
    main()
