from __future__ import annotations

"""Phase 2 repository for `industry_fundamentals_weekly`.

Kept separate from `committee.industry_cycle.factor_repository` (Phase 1-B,
price-only, asset-level) since this table is industry-level and stores a
different score. Same conventions: NULL for missing values, `init_db()`
called before every write, `model_version` part of the UNIQUE key so
re-running under a new version never overwrites an older version's row while
re-running the same key is an idempotent upsert-in-place.
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from committee.core.database import connect, init_db


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _f(value: Any) -> Optional[float]:
    return None if value is None else float(value)


_UPSERT_SQL = """
    INSERT INTO industry_fundamentals_weekly (
        industry_id, as_of, model_version, data_cutoff_at, data_completeness,
        fundamentals_score, weighted_sum, reason, indicators_used_json, created_at
    ) VALUES (
        :industry_id, :as_of, :model_version, :data_cutoff_at, :data_completeness,
        :fundamentals_score, :weighted_sum, :reason, :indicators_used_json, :created_at
    )
    ON CONFLICT(industry_id, as_of, model_version) DO UPDATE SET
        data_cutoff_at=excluded.data_cutoff_at,
        data_completeness=excluded.data_completeness,
        fundamentals_score=excluded.fundamentals_score,
        weighted_sum=excluded.weighted_sum,
        reason=excluded.reason,
        indicators_used_json=excluded.indicators_used_json;
"""


def upsert_industry_fundamentals_weekly(record: Dict[str, Any], db_path: Path | None = None) -> None:
    """Insert/update one row into `industry_fundamentals_weekly` (idempotent upsert).

    `record` must include `industry_id`, `as_of`, `model_version`, `data_cutoff_at`.
    `indicators_used` (a list of plain dicts, e.g. from
    `FundamentalsScoreBundle.to_dict()["evidence"]`) is JSON-encoded into
    `indicators_used_json` if provided; a pre-encoded `indicators_used_json`
    string takes precedence when both are given.
    """
    now = _now_iso()
    for required in ("industry_id", "as_of", "model_version", "data_cutoff_at"):
        if not record.get(required):
            raise ValueError(f"industry_fundamentals_weekly record missing required field '{required}'")

    indicators_used_json = record.get("indicators_used_json")
    if indicators_used_json is None and record.get("indicators_used") is not None:
        indicators_used_json = json.dumps(record["indicators_used"], ensure_ascii=True)

    params = {
        "industry_id": record["industry_id"],
        "as_of": record["as_of"],
        "model_version": record["model_version"],
        "data_cutoff_at": record["data_cutoff_at"],
        "data_completeness": _f(record.get("data_completeness")),
        "fundamentals_score": _f(record.get("fundamentals_score")),
        "weighted_sum": _f(record.get("weighted_sum")),
        "reason": record.get("reason"),
        "indicators_used_json": indicators_used_json,
        "created_at": now,
    }
    init_db(db_path)
    with connect(db_path) as conn:
        conn.execute(_UPSERT_SQL, params)


def _row_to_dict(row: Any) -> Dict[str, Any]:
    d = dict(row)
    if d.get("indicators_used_json"):
        try:
            d["indicators_used"] = json.loads(d["indicators_used_json"])
        except (TypeError, ValueError):
            d["indicators_used"] = None
    else:
        d["indicators_used"] = None
    return d


def get_fundamentals_weekly(
    industry_id: str, as_of: str, model_version: str, db_path: Path | None = None
) -> Optional[Dict[str, Any]]:
    init_db(db_path)
    with connect(db_path) as conn:
        row = conn.execute(
            """
            SELECT * FROM industry_fundamentals_weekly
            WHERE industry_id = :industry_id AND as_of = :as_of AND model_version = :model_version;
            """,
            {"industry_id": industry_id, "as_of": as_of, "model_version": model_version},
        ).fetchone()
        return _row_to_dict(row) if row is not None else None


def get_latest_fundamentals_before(
    industry_id: str, before_as_of: str, model_version: str, db_path: Path | None = None
) -> Optional[Dict[str, Any]]:
    """Return the most recent `industry_fundamentals_weekly` row strictly before `before_as_of`."""
    init_db(db_path)
    with connect(db_path) as conn:
        row = conn.execute(
            """
            SELECT * FROM industry_fundamentals_weekly
            WHERE industry_id = :industry_id AND model_version = :model_version AND as_of < :before_as_of
            ORDER BY as_of DESC
            LIMIT 1;
            """,
            {"industry_id": industry_id, "model_version": model_version, "before_as_of": before_as_of},
        ).fetchone()
        return _row_to_dict(row) if row is not None else None


def list_fundamentals_weekly(
    industry_id: str | None = None, db_path: Path | None = None
) -> List[Dict[str, Any]]:
    init_db(db_path)
    with connect(db_path) as conn:
        if industry_id:
            rows = conn.execute(
                "SELECT * FROM industry_fundamentals_weekly WHERE industry_id = :id ORDER BY as_of;",
                {"id": industry_id},
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM industry_fundamentals_weekly ORDER BY industry_id, as_of;"
            ).fetchall()
        return [_row_to_dict(r) for r in rows]
