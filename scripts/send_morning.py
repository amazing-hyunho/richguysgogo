from __future__ import annotations

# Morning sender for latest report markdown.

import argparse
import json
import re
import sqlite3
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

    db_metrics = _load_latest_db_metrics(ROOT_DIR / "data" / "investment.db")

    # snapshot은 있으면 사용, 없어도 DB만으로 전송 가능
    snapshot: dict = {}
    stances: list = []
    committee = None
    report_text = ""

    runs_dir = ROOT_DIR / "runs"
    latest_dir = _latest_run_dir(runs_dir)
    if latest_dir is not None:
        sp = latest_dir / "snapshot.json"
        if sp.exists():
            snapshot = json.loads(sp.read_text(encoding="utf-8"))
        sp2 = latest_dir / "stances.json"
        if sp2.exists():
            stances = json.loads(sp2.read_text(encoding="utf-8"))
        cp = latest_dir / "committee_result.json"
        if cp.exists():
            committee = json.loads(cp.read_text(encoding="utf-8"))
        rp = latest_dir / "report.md"
        if args.include_report and rp.exists():
            report_text = rp.read_text(encoding="utf-8")

    news_digest = _load_latest_news_digest(ROOT_DIR / "runs" / "news" / "latest_news_digest.json")
    text = _build_morning_brief(
        snapshot=snapshot,
        stances=stances,
        committee=committee,
        report_text=report_text,
        db_metrics=db_metrics,
        news_digest=news_digest,
    )
    send_report(text)


def _latest_run_dir(runs_dir: Path) -> Path | None:
    if not runs_dir.exists():
        return None
    date_dir_pattern = re.compile(r"^\d{4}-\d{2}-\d{2}$")
    dirs = [
        path
        for path in runs_dir.iterdir()
        if path.is_dir()
        and date_dir_pattern.match(path.name)
        and (path / "snapshot.json").exists()
    ]
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


def _build_morning_brief(
    snapshot: dict,
    stances: list,
    committee: dict | None,
    report_text: str,
    db_metrics: dict | None,
    news_digest: dict | None,
) -> str:
    """간결한 아침 브리프: 시장 지수 + 수급 + 대시보드 링크만."""
    from datetime import date as _date

    markets = snapshot.get("markets", {}) or {}
    kr = (markets.get("kr") or {}) if isinstance(markets, dict) else {}
    us = (markets.get("us") or {}) if isinstance(markets, dict) else {}
    fx = (markets.get("fx") or {}) if isinstance(markets, dict) else {}

    if db_metrics:
        kr = _merge_kr_with_fallback(kr, db_metrics.get("kr", {}))
        us = _merge_non_null(us, db_metrics.get("us", {}))
        fx = _merge_non_null(fx, db_metrics.get("fx", {}))

    # 수급 데이터는 DB에서 직접
    flow = _load_latest_flow(ROOT_DIR / "data" / "investment.db")

    today = _date.today().strftime("%Y-%m-%d")
    lines: list[str] = []

    lines.append(f"📊 {today} 시장 브리프")
    lines.append("")

    # ── 시장 지수 ────────────────────────────────
    lines.append("🌍 시장")
    lines.append(f"  KOSPI   {_fmt_signed(kr.get('kospi_pct'), 2, '%')}")
    lines.append(f"  KOSDAQ  {_fmt_signed(kr.get('kosdaq_pct'), 2, '%')}")
    lines.append(f"  S&P500  {_fmt_signed(us.get('sp500_pct'), 2, '%')}")
    lines.append(f"  NASDAQ  {_fmt_signed(us.get('nasdaq_pct'), 2, '%')}")
    lines.append(f"  USD/KRW {_fmt(fx.get('usdkrw'), 1)}")
    lines.append("")

    # ── 수급 ─────────────────────────────────────
    lines.append("💰 수급 (억원)")
    if flow:
        def _flow_str(v) -> str:
            if v is None:
                return "n/a"
            try:
                return f"{float(v):+,.0f}"
            except Exception:
                return "n/a"
        lines.append(f"  외국인  {_flow_str(flow.get('foreign_net'))}")
        lines.append(f"  기관    {_flow_str(flow.get('institution_net'))}")
        lines.append(f"  개인    {_flow_str(flow.get('retail_net'))}")
    else:
        lines.append("  수급 데이터 없음")
    lines.append("")

    # ── 대시보드 링크 ─────────────────────────────
    lines.append("🔗 대시보드")
    lines.append("  https://amazing-hyunho.github.io/richguysgogo/")

    return "\n".join(lines)


def _load_latest_flow(db_path: Path) -> dict | None:
    """DB에서 최신 수급 데이터 1행 반환."""
    if not db_path.exists():
        return None
    try:
        import sqlite3
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        try:
            row = conn.execute(
                """
                SELECT foreign_net, institution_net, retail_net, date
                FROM market_flow_daily
                WHERE foreign_net IS NOT NULL
                ORDER BY date DESC
                LIMIT 1
                """
            ).fetchone()
            return dict(row) if row else None
        finally:
            conn.close()
    except Exception:
        return None


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


def _merge_non_null(base: dict, overlay: dict) -> dict:
    """Merge dicts while keeping only non-None overlay values."""
    result = dict(base or {})
    for key, value in (overlay or {}).items():
        if value is not None:
            result[key] = value
    return result


def _merge_kr_with_fallback(snapshot_kr: dict, db_kr: dict) -> dict:
    """Prefer snapshot KR values; use DB only for missing/zero fallback."""
    result = dict(snapshot_kr or {})
    for key in ("kospi_pct", "kosdaq_pct"):
        snap_v = result.get(key)
        db_v = (db_kr or {}).get(key)
        if snap_v is None and db_v is not None:
            result[key] = db_v
            continue
        try:
            snap_f = float(snap_v)
            if snap_f == 0.0 and db_v is not None and abs(float(db_v)) >= 0.05:
                result[key] = db_v
        except Exception:
            if db_v is not None:
                result[key] = db_v
    return result


def _digest_headlines(news_digest: dict | None, limit: int = 3) -> list[str]:
    if not isinstance(news_digest, dict):
        return []
    top_articles = news_digest.get("top_articles", [])
    if not isinstance(top_articles, list):
        return []
    out: list[str] = []
    for item in top_articles:
        if not isinstance(item, dict):
            continue
        topic = str(item.get("topic", "")).strip()
        title = str(item.get("title", "")).strip()
        if not title:
            continue
        out.append(f"[{topic}] {title}" if topic else title)
        if len(out) >= max(limit, 1):
            break
    return out


def _load_latest_news_digest(path: Path) -> dict | None:
    try:
        if not path.exists():
            return None
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _load_latest_db_metrics(db_path: Path) -> dict | None:
    if not db_path.exists():
        return None
    try:
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        try:
            market = conn.execute(
                """
                SELECT kospi_pct, kosdaq_pct, sp500_pct, nasdaq_pct, dow_pct, usdkrw, usdkrw_pct, vix
                FROM market_daily
                ORDER BY date DESC
                LIMIT 1
                """
            ).fetchone()
            prev_market = conn.execute(
                """
                SELECT kospi_pct, kosdaq_pct
                FROM market_daily
                WHERE kospi_pct IS NOT NULL AND kosdaq_pct IS NOT NULL
                ORDER BY date DESC
                LIMIT 2
                """
            ).fetchall()
            daily = conn.execute(
                """
                SELECT us10y, us2y, spread_2_10, vix, dxy, usdkrw, vix3m, vix_term_spread,
                       hy_oas, ig_oas, fed_funds_rate, real_rate
                FROM daily_macro
                ORDER BY date DESC
                LIMIT 1
                """
            ).fetchone()
            monthly = conn.execute(
                """
                SELECT unemployment_rate, cpi_yoy, core_cpi_yoy, pce_yoy, pmi
                FROM monthly_macro
                ORDER BY date DESC
                LIMIT 1
                """
            ).fetchone()
            quarterly = conn.execute(
                """
                SELECT gdp_qoq_annualized
                FROM quarterly_macro
                ORDER BY date DESC
                LIMIT 1
                """
            ).fetchone()
            latest_kospi = market["kospi_pct"] if market else None
            latest_kosdaq = market["kosdaq_pct"] if market else None
            # If latest KR indices are fallback zeros, use previous non-zero row for briefing.
            if (
                latest_kospi == 0.0
                and latest_kosdaq == 0.0
                and prev_market
                and len(prev_market) >= 2
            ):
                latest_kospi = prev_market[1]["kospi_pct"]
                latest_kosdaq = prev_market[1]["kosdaq_pct"]

            return {
                "kr": {
                    "kospi_pct": latest_kospi,
                    "kosdaq_pct": latest_kosdaq,
                },
                "us": {
                    "sp500_pct": market["sp500_pct"] if market else None,
                    "nasdaq_pct": market["nasdaq_pct"] if market else None,
                    "dow_pct": market["dow_pct"] if market else None,
                },
                "fx": {
                    "usdkrw": market["usdkrw"] if market else None,
                    "usdkrw_pct": market["usdkrw_pct"] if market else None,
                },
                "volatility": {
                    "vix": market["vix"] if market else None,
                },
                "daily": dict(daily) if daily else {},
                "monthly": dict(monthly) if monthly else {},
                "quarterly": dict(quarterly) if quarterly else {},
                "structural": {
                    "hy_oas": daily["hy_oas"] if daily and "hy_oas" in daily.keys() else None,
                    "ig_oas": daily["ig_oas"] if daily and "ig_oas" in daily.keys() else None,
                    "fed_funds_rate": daily["fed_funds_rate"] if daily and "fed_funds_rate" in daily.keys() else None,
                    "real_rate": daily["real_rate"] if daily and "real_rate" in daily.keys() else None,
                },
            }
        finally:
            conn.close()
    except Exception:
        return None


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
