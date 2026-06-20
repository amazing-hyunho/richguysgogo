from __future__ import annotations

"""Import an Investment Thesis JSON draft into SQLite.

Usage:
    python scripts/import_thesis.py path/to/thesis.json
"""

import argparse
import json
from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from committee.core.database import connect, init_db


DB_PATH = ROOT_DIR / "data" / "investment.db"


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Import a Thesis Monitor JSON draft.")
    parser.add_argument("json_path", help="Path to thesis JSON file exported from dashboard.")
    return parser.parse_args()


def _json_text(value: object) -> str | None:
    if value is None:
        return None
    if isinstance(value, str):
        value = [v.strip() for v in value.split(",") if v.strip()]
    return json.dumps(value, ensure_ascii=False)


def main() -> None:
    args = _parse_args()
    path = Path(args.json_path)
    payload = json.loads(path.read_text(encoding="utf-8"))
    init_db(DB_PATH)
    with connect(DB_PATH) as conn:
        cur = conn.execute(
            """
            INSERT INTO investment_thesis (
                title, raw_study_text, summary, core_claim, thesis_type, horizon, status,
                initial_confidence, current_confidence, user_position_view,
                beneficiaries_json, victims_json, watch_indicators_json, indicator_directions_json,
                catalysts_json, invalidation_conditions_json, news_keywords_json,
                created_at, updated_at
            ) VALUES (
                :title, :raw_study_text, :summary, :core_claim, :thesis_type, :horizon, :status,
                :initial_confidence, :current_confidence, :user_position_view,
                :beneficiaries_json, :victims_json, :watch_indicators_json, :indicator_directions_json,
                :catalysts_json, :invalidation_conditions_json, :news_keywords_json,
                datetime('now'), datetime('now')
            );
            """,
            {
                "title": str(payload.get("title") or "Untitled Thesis"),
                "raw_study_text": str(payload.get("raw_study_text") or ""),
                "summary": payload.get("summary"),
                "core_claim": payload.get("core_claim") or payload.get("summary"),
                "thesis_type": payload.get("thesis_type") or "macro",
                "horizon": payload.get("horizon") or "medium",
                "status": payload.get("status") or "Active",
                "initial_confidence": float(payload.get("initial_confidence") or 50),
                "current_confidence": float(payload.get("current_confidence") or payload.get("initial_confidence") or 50),
                "user_position_view": payload.get("user_position_view") or "watch",
                "beneficiaries_json": _json_text(payload.get("beneficiaries")),
                "victims_json": _json_text(payload.get("victims")),
                "watch_indicators_json": _json_text(payload.get("watch_indicators")),
                "indicator_directions_json": _json_text(payload.get("indicator_directions")),
                "catalysts_json": _json_text(payload.get("catalysts")),
                "invalidation_conditions_json": _json_text(payload.get("invalidation_conditions")),
                "news_keywords_json": _json_text(payload.get("news_keywords")),
            },
        )
        thesis_id = int(cur.lastrowid)
        for item in payload.get("indicators", []) or []:
            if not isinstance(item, dict) or not item.get("indicator_key"):
                continue
            conn.execute(
                """
                INSERT INTO thesis_indicator_map (
                    thesis_id, indicator_key, expected_direction, weight, lookback_days,
                    trigger_type, threshold, description, created_at, updated_at
                ) VALUES (
                    :thesis_id, :indicator_key, :expected_direction, :weight, :lookback_days,
                    :trigger_type, :threshold, :description, datetime('now'), datetime('now')
                );
                """,
                {
                    "thesis_id": thesis_id,
                    "indicator_key": item.get("indicator_key"),
                    "expected_direction": item.get("expected_direction") or "neutral",
                    "weight": float(item.get("weight") or 1.0),
                    "lookback_days": int(item.get("lookback_days") or 20),
                    "trigger_type": item.get("trigger_type"),
                    "threshold": item.get("threshold"),
                    "description": item.get("description"),
                },
            )
        for item in payload.get("assets", []) or []:
            if not isinstance(item, dict):
                continue
            asset_id = str(item.get("asset_id") or item.get("ticker") or "").strip()
            if not asset_id:
                continue
            conn.execute(
                """
                INSERT INTO thesis_asset_map (
                    thesis_id, asset_type, asset_id, ticker, relation_type, sensitivity,
                    confidence, note, created_at, updated_at
                ) VALUES (
                    :thesis_id, :asset_type, :asset_id, :ticker, :relation_type, :sensitivity,
                    :confidence, :note, datetime('now'), datetime('now')
                );
                """,
                {
                    "thesis_id": thesis_id,
                    "asset_type": item.get("asset_type") or "stock",
                    "asset_id": asset_id,
                    "ticker": str(item.get("ticker") or asset_id).upper(),
                    "relation_type": item.get("relation_type") or "watchlist",
                    "sensitivity": float(item.get("sensitivity") or 1.0),
                    "confidence": float(item.get("confidence") or 50),
                    "note": item.get("note"),
                },
            )
    print(f"thesis_imported id={thesis_id} title={payload.get('title') or 'Untitled Thesis'}")


if __name__ == "__main__":
    main()
