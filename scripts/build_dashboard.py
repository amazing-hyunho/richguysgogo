from __future__ import annotations

import json
import sqlite3
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


def fetch_rows(conn: sqlite3.Connection, query: str) -> list[dict[str, object]]:
    conn.row_factory = sqlite3.Row
    return [dict(row) for row in conn.execute(query).fetchall()]


def load_committee_history() -> list[dict[str, object]]:
    history: list[dict[str, object]] = []
    for path in sorted(RUNS_DIR.glob("*.json")):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
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
    latest_path = max(RUNS_DIR.glob("*.json"), default=None)
    if latest_path is None:
        return {"market_date": "-", "stances": []}

    try:
        payload = json.loads(latest_path.read_text(encoding="utf-8"))
    except Exception:
        return {"market_date": latest_path.stem, "stances": []}

    stances = []
    for stance in payload.get("stances", []):
        stances.append(
            {
                "agent_name": stance.get("agent_name", "-"),
                "regime_tag": stance.get("regime_tag", "-"),
                "confidence": stance.get("confidence", "-"),
                "korean_comment": stance.get("korean_comment", ""),
                "core_claims": stance.get("core_claims", []),
            }
        )

    return {
        "market_date": payload.get("market_date", latest_path.stem),
        "stances": stances,
    }



def load_latest_committee() -> dict[str, object]:
    latest_path = max(RUNS_DIR.glob("*.json"), default=None)
    if latest_path is None:
        return {"market_date": "-", "consensus": "-", "key_points": [], "ops_guidance": []}

    try:
        payload = json.loads(latest_path.read_text(encoding="utf-8"))
    except Exception:
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
            "total_collected": 0,
            "topic_counts": [],
            "top_articles": [],
        }
    try:
        return json.loads(digest_path.read_text(encoding="utf-8"))
    except Exception:
        return {
            "crawled_at": "-",
            "total_collected": 0,
            "topic_counts": [],
            "top_articles": [],
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
            "market_daily": fetch_rows(conn, "SELECT date, kospi_pct, kosdaq_pct, sp500_pct, nasdaq_pct, dow_pct FROM market_daily ORDER BY date"),
            "market_flow_daily": fetch_rows(
                conn,
                "SELECT date, foreign_net, institution_net, retail_net, foreign_20d, foreign_60d FROM market_flow_daily ORDER BY date",
            ),
            "daily_macro": fetch_rows(conn, "SELECT date, us10y, us2y, spread_2_10, vix, dxy, usdkrw, vix3m, vix_term_spread, hy_oas, ig_oas, fed_balance_sheet FROM daily_macro ORDER BY date"),
            "monthly_macro": fetch_rows(conn, "SELECT date, unemployment_rate, cpi_yoy, core_cpi_yoy, pce_yoy, pmi, wage_yoy FROM monthly_macro ORDER BY date"),
            "quarterly_macro": fetch_rows(conn, "SELECT date, real_gdp, gdp_qoq_annualized FROM quarterly_macro ORDER BY date"),
            "committee_history": load_committee_history(),
            "latest_stances": load_latest_stances(),
            "latest_committee": load_latest_committee(),
            "latest_news_digest": load_latest_news_digest(),
        }
    finally:
        conn.close()

    OUTPUT_PATH.write_text(build_dashboard_html(dashboard_data), encoding="utf-8")
    print(f"Dashboard generated: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
