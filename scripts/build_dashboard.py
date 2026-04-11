from __future__ import annotations

import json
import sqlite3
from datetime import date
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]

try:
    from committee.core.database import init_db
except ModuleNotFoundError:
    import sys
    sys.path.insert(0, str(ROOT_DIR))
    from committee.core.database import init_db
DB_PATH = ROOT_DIR / "data" / "investment.db"
RUNS_DIR = ROOT_DIR / "runs"
OUTPUT_PATH = ROOT_DIR / "docs" / "dashboard.html"
TEMPLATE_PATH = ROOT_DIR / "docs" / "dashboard_template.html"

AGENT_OWNER_LABELS = {
    "macro": "매크로 담당자",
    "flow": "수급 담당자",
    "sector": "섹터 담당자",
    "risk": "리스크 담당자",
    "earnings": "이익모멘텀 담당자",
    "breadth": "브레드스 담당자",
    "liquidity": "유동성 담당자",
}

AGENT_SPEAKING_ORDER = ["risk", "macro", "flow", "earnings", "liquidity", "sector", "breadth"]
AGENT_SPEAKING_ORDER_INDEX = {name: idx for idx, name in enumerate(AGENT_SPEAKING_ORDER)}


def map_agent_owner(agent_name: str) -> str:
    return AGENT_OWNER_LABELS.get(agent_name, f"{agent_name} 담당자")


def fetch_rows(conn: sqlite3.Connection, query: str) -> list[dict[str, object]]:
    conn.row_factory = sqlite3.Row
    return [dict(row) for row in conn.execute(query).fetchall()]


def list_run_paths() -> list[Path]:
    return sorted(
        path for path in RUNS_DIR.glob("*.json")
        if path.is_file() and path.stem[:4].isdigit()
    )


def load_run_payload(path: Path) -> dict[str, object] | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def normalize_minute(minute: dict[str, object]) -> dict[str, object]:
    speaker = str(minute.get("speaker", ""))
    return {
        "speaker": speaker,
        "speaker_label": minute.get("speaker_label") or map_agent_owner(speaker),
        "summary": minute.get("summary", ""),
        "references": minute.get("references", []),
    }


def sort_minutes(minutes: list[dict[str, object]]) -> list[dict[str, object]]:
    return sorted(
        minutes,
        key=lambda item: (
            AGENT_SPEAKING_ORDER_INDEX.get(str(item.get("speaker", "")), len(AGENT_SPEAKING_ORDER)),
            str(item.get("speaker_label", "")),
        ),
    )


def load_committee_history() -> list[dict[str, object]]:
    history: list[dict[str, object]] = []
    for path in list_run_paths():
        payload = load_run_payload(path)
        if not payload:
            continue

        committee = payload.get("committee_result", {})
        guidance = committee.get("ops_guidance", [])
        ok_text = next((item.get("text", "") for item in guidance if item.get("level") == "OK"), "")
        caution_text = next((item.get("text", "") for item in guidance if item.get("level") == "CAUTION"), "")
        avoid_text = next((item.get("text", "") for item in guidance if item.get("level") == "AVOID"), "")
        history.append(
            {
                "market_date": payload.get("market_date", path.stem),
                "consensus": committee.get("consensus", ""),
                "ok_count": sum(1 for item in guidance if item.get("level") == "OK"),
                "caution_count": sum(1 for item in guidance if item.get("level") == "CAUTION"),
                "avoid_count": sum(1 for item in guidance if item.get("level") == "AVOID"),
                "ok_text": ok_text,
                "caution_text": caution_text,
                "avoid_text": avoid_text,
            }
        )
    return history



def load_latest_stances() -> dict[str, object]:
    latest_path = max(list_run_paths(), default=None)
    if latest_path is None:
        return {"market_date": "-", "stances": []}

    payload = load_run_payload(latest_path)
    if not payload:
        return {"market_date": latest_path.stem, "stances": []}

    stances = []
    for stance in payload.get("stances", []):
        stances.append(
            {
                "agent_name": stance.get("agent_name", "-"),
                "agent_owner": map_agent_owner(stance.get("agent_name", "")),
                "confidence": stance.get("confidence", "-"),
                "korean_comment": stance.get("korean_comment", ""),
                "core_claims": stance.get("core_claims", []),
            }
        )

    stances.sort(key=lambda item: AGENT_SPEAKING_ORDER_INDEX.get(item["agent_name"], len(AGENT_SPEAKING_ORDER)))
    return {
        "market_date": payload.get("market_date", latest_path.stem),
        "stances": stances,
    }



def load_latest_debate_minutes() -> dict[str, object]:
    today_path = RUNS_DIR / f"{date.today().isoformat()}.json"
    if not today_path.exists():
        return {"market_date": "-", "enabled": False, "facilitator_note": "", "round_conclusion": "", "minutes": []}

    payload = load_run_payload(today_path)
    if not payload:
        return {"market_date": today_path.stem, "enabled": False, "facilitator_note": "", "round_conclusion": "", "minutes": []}

    debate = payload.get("debate_round") or {}
    minutes = sort_minutes([normalize_minute(minute) for minute in debate.get("minutes", [])])
    return {
        "market_date": payload.get("market_date", today_path.stem),
        "enabled": bool(debate),
        "round_index": debate.get("round_index"),
        "facilitator_note": debate.get("facilitator_note", ""),
        "round_conclusion": debate.get("round_conclusion", ""),
        "minutes": minutes,
    }



def load_recent_meeting_timeline(limit: int = 7) -> list[dict[str, object]]:
    timeline: list[dict[str, object]] = []
    for path in reversed(list_run_paths()):
        payload = load_run_payload(path)
        if not payload:
            continue

        debate = payload.get("debate_round") or {}
        committee = payload.get("committee_result") or {}
        key_points = [item.get("point", "") for item in committee.get("key_points", []) if isinstance(item, dict) and item.get("point")]
        ops_guidance = [
            {"level": item.get("level", ""), "text": item.get("text", "")}
            for item in committee.get("ops_guidance", [])
            if isinstance(item, dict)
        ]
        timeline.append(
            {
                "market_date": payload.get("market_date", path.stem),
                "facilitator_note": debate.get("facilitator_note", ""),
                "round_conclusion": debate.get("round_conclusion", ""),
                "consensus": committee.get("consensus", ""),
                "key_points": key_points[:3],
                "ops_guidance": ops_guidance[:3],
                "minutes": sort_minutes([normalize_minute(minute) for minute in debate.get("minutes", [])]),
            }
        )
        if len(timeline) >= limit:
            break
    return timeline



def load_handoff_context() -> dict[str, object]:
    timeline = load_recent_meeting_timeline(limit=2)
    current_session = timeline[0] if timeline else None
    previous_session = timeline[1] if len(timeline) > 1 else None
    return {
        "current_session": current_session,
        "previous_session": previous_session,
        "agent_speaking_order": AGENT_SPEAKING_ORDER,
        "handoff_message": (
            "전일 결론과 오늘 근거를 같은 화면에서 비교해 다음 회의가 전일 판단을 이어서 업데이트할 수 있게 구성했습니다."
        ),
    }



def load_latest_committee() -> dict[str, object]:
    latest_path = max(list_run_paths(), default=None)
    if latest_path is None:
        return {"market_date": "-", "consensus": "-", "key_points": [], "ops_guidance": []}

    payload = load_run_payload(latest_path)
    if not payload:
        return {"market_date": latest_path.stem, "consensus": "-", "key_points": [], "ops_guidance": []}

    committee = payload.get("committee_result", {}) or {}
    key_points = [item.get("point", "") for item in committee.get("key_points", []) if item.get("point")]
    ops_guidance = [
        {
            "level": item.get("level", ""),
            "text": item.get("text", ""),
        }
        for item in committee.get("ops_guidance", [])
        if isinstance(item, dict)
    ]
    return {
        "market_date": payload.get("market_date", latest_path.stem),
        "consensus": committee.get("consensus", ""),
        "key_points": key_points[:3],
        "ops_guidance": ops_guidance[:3],
    }



def load_latest_news_digest() -> dict[str, object]:
    digest_path = RUNS_DIR / "news" / "latest_news_digest.json"
    if not digest_path.exists():
        return {
            "crawled_at": "-",
            "news_date": "-",
            "total_collected": 0,
            "topic_counts": [],
            "top_articles": [],
            "sector_hot_topics": [],
        }
    try:
        return json.loads(digest_path.read_text(encoding="utf-8"))
    except Exception:
        return {
            "crawled_at": "-",
            "news_date": "-",
            "total_collected": 0,
            "topic_counts": [],
            "top_articles": [],
            "sector_hot_topics": [],
        }


def load_latest_korean_market_flow_breakdown() -> dict[str, object]:
    """Load latest KOSPI/KOSDAQ investor flow breakdown from run snapshot."""
    latest_path = max(list_run_paths(), default=None)
    if latest_path is None:
        return {"market_date": "-", "market": {}}
    payload = load_run_payload(latest_path) or {}
    snapshot = payload.get("snapshot") or {}
    flow = snapshot.get("korean_market_flow") or {}
    market = flow.get("market") if isinstance(flow, dict) else {}
    return {
        "market_date": payload.get("market_date", latest_path.stem),
        "market": market if isinstance(market, dict) else {},
    }


def load_korean_market_flow_compare() -> dict[str, object]:
    """Load current/previous Korean market flow snapshots for day-over-day comparison."""
    run_paths = list_run_paths()
    if not run_paths:
        return {"current_date": "-", "previous_date": "-", "current": {}, "previous": {}}

    snapshots: list[tuple[str, dict[str, object]]] = []
    for path in reversed(run_paths):
        payload = load_run_payload(path) or {}
        snapshot = payload.get("snapshot") or {}
        flow = snapshot.get("korean_market_flow") or {}
        market = flow.get("market") if isinstance(flow, dict) else {}
        if isinstance(market, dict) and market:
            snapshots.append((str(payload.get("market_date", path.stem)), market))
        if len(snapshots) >= 2:
            break

    if not snapshots:
        return {"current_date": "-", "previous_date": "-", "current": {}, "previous": {}}
    if len(snapshots) == 1:
        return {
            "current_date": snapshots[0][0],
            "previous_date": "-",
            "current": snapshots[0][1],
            "previous": {},
        }
    return {
        "current_date": snapshots[0][0],
        "previous_date": snapshots[1][0],
        "current": snapshots[0][1],
        "previous": snapshots[1][1],
    }


def load_latest_policy_rates() -> dict[str, object]:
    """Load overseas/domestic policy rates for dashboard summary."""
    latest_path = max(list_run_paths(), default=None)
    if latest_path is None:
        return {"market_date": "-", "domestic_base_rate": None, "overseas_base_rate": None}

    payload = load_run_payload(latest_path) or {}
    snapshot = payload.get("snapshot") or {}
    macro = snapshot.get("macro") or {}
    structural = macro.get("structural") if isinstance(macro, dict) else {}
    overseas_base_rate = None
    if isinstance(structural, dict):
        fed = structural.get("fed_funds_rate")
        if isinstance(fed, (int, float)):
            overseas_base_rate = float(fed)

    domestic_base_rate = None
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        try:
            row = conn.execute(
                """
                SELECT base_rate
                FROM domestic_policy_rate_daily
                ORDER BY date DESC
                LIMIT 1
                """
            ).fetchone()
            if row and row["base_rate"] is not None:
                domestic_base_rate = float(row["base_rate"])
        finally:
            conn.close()
    except Exception:
        domestic_base_rate = None

    return {
        "market_date": payload.get("market_date", latest_path.stem),
        "domestic_base_rate": domestic_base_rate,
        "overseas_base_rate": overseas_base_rate,
    }


def build_dashboard_html(data: dict[str, object]) -> str:
    data_json = json.dumps(data, ensure_ascii=False)
    template = TEMPLATE_PATH.read_text(encoding="utf-8")
    placeholder = "__DASHBOARD_DATA__"
    if placeholder not in template:
        raise ValueError(f"dashboard_template_missing_placeholder: {placeholder}")
    return template.replace(placeholder, data_json, 1)



def main() -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    init_db(DB_PATH)
    conn = sqlite3.connect(DB_PATH)
    try:
        dashboard_data = {
            "market_daily": fetch_rows(
                conn,
                "SELECT date, kospi, kosdaq, sp500, nasdaq, dow, kospi_pct, kosdaq_pct, sp500_pct, nasdaq_pct, dow_pct, usdkrw, usdkrw_pct FROM market_daily ORDER BY date",
            ),
            "market_flow_daily": fetch_rows(
                conn,
                "SELECT date, foreign_net, institution_net, retail_net, foreign_20d, foreign_60d FROM market_flow_daily ORDER BY date",
            ),
            "daily_macro": fetch_rows(conn, "SELECT date, us10y, us2y, spread_2_10, vix, dxy, usdkrw, vix3m, vix_term_spread, hy_oas, ig_oas, fed_balance_sheet FROM daily_macro ORDER BY date"),
            "monthly_macro": fetch_rows(conn, "SELECT date, unemployment_rate, cpi_yoy, core_cpi_yoy, pce_yoy, pmi, wage_yoy FROM monthly_macro ORDER BY date"),
            "quarterly_macro": fetch_rows(conn, "SELECT date, real_gdp, gdp_qoq_annualized FROM quarterly_macro ORDER BY date"),
            "committee_history": load_committee_history(),
            "latest_stances": load_latest_stances(),
            "latest_debate_minutes": load_latest_debate_minutes(),
            "recent_meeting_timeline": load_recent_meeting_timeline(),
            "meeting_handoff": load_handoff_context(),
            "latest_committee": load_latest_committee(),
            "latest_news_digest": load_latest_news_digest(),
            "latest_korean_market_flow": load_latest_korean_market_flow_breakdown(),
            "korean_market_flow_compare": load_korean_market_flow_compare(),
            "latest_policy_rates": load_latest_policy_rates(),
        }
    finally:
        conn.close()

    OUTPUT_PATH.write_text(build_dashboard_html(dashboard_data), encoding="utf-8")
    print(f"Dashboard generated: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
