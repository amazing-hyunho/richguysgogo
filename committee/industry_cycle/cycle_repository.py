from __future__ import annotations

"""Phase 4 repository for `industry_cycle_signal` and `industry_signal_reason`.

Same conventions as every other Phase repository in this package: NULL
(never 0.0) for missing values, `init_db()` called before every write so
this module works standalone against a fresh DB, and `model_version` part
of every UNIQUE key so re-running under a new model_version never overwrites
an older version's row while re-running the exact same key is an idempotent
upsert-in-place.
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


# --- industry_cycle_signal ------------------------------------------------

_SIGNAL_COLUMNS = (
    "industry_id", "as_of", "model_version", "data_cutoff_at",
    "cycle_score", "cycle_weighted_sum", "cycle_score_reason", "data_completeness",
    "representative_asset_id", "representative_market",
    "relative_strength_score", "trend_score", "overheat_score", "risk_score",
    "fundamentals_score", "earnings_revision_score", "breadth_score", "flow_score", "macro_fit_score",
    "raw_state", "confirmed_state", "confirmation_status", "action_signal",
    "consecutive_weeks", "previous_confirmed_state",
    "signal_strength", "history_reliability", "model_agreement", "confidence",
    "is_actionable", "urgent_flags_json", "score_breakdown_json",
)

_FLOAT_FIELDS = (
    "cycle_score", "cycle_weighted_sum", "data_completeness",
    "relative_strength_score", "trend_score", "overheat_score", "risk_score",
    "fundamentals_score", "earnings_revision_score", "breadth_score", "flow_score", "macro_fit_score",
    "signal_strength", "history_reliability", "model_agreement", "confidence",
)

_SIGNAL_UPSERT_SQL = f"""
    INSERT INTO industry_cycle_signal (
        {', '.join(_SIGNAL_COLUMNS)}, created_at
    ) VALUES (
        {', '.join(':' + c for c in _SIGNAL_COLUMNS)}, :created_at
    )
    ON CONFLICT(industry_id, as_of, model_version) DO UPDATE SET
        {', '.join(f'{c}=excluded.{c}' for c in _SIGNAL_COLUMNS if c not in ('industry_id', 'as_of', 'model_version'))};
"""


def upsert_industry_cycle_signal(record: Dict[str, Any], db_path: Path | None = None) -> None:
    """Insert/update one row into `industry_cycle_signal` (idempotent upsert).

    `record` must include `industry_id`, `as_of`, `model_version`,
    `data_cutoff_at`. `urgent_flags` (a list) and `score_breakdown` (a plain
    dict) are JSON-encoded if the pre-encoded `*_json` key isn't already
    given.
    """
    for required in ("industry_id", "as_of", "model_version", "data_cutoff_at"):
        if not record.get(required):
            raise ValueError(f"industry_cycle_signal record missing required field '{required}'")

    urgent_flags_json = record.get("urgent_flags_json")
    if urgent_flags_json is None and record.get("urgent_flags") is not None:
        urgent_flags_json = json.dumps(record["urgent_flags"], ensure_ascii=True)

    score_breakdown_json = record.get("score_breakdown_json")
    if score_breakdown_json is None and record.get("score_breakdown") is not None:
        score_breakdown_json = json.dumps(record["score_breakdown"], ensure_ascii=True)

    params: Dict[str, Any] = {
        "industry_id": str(record["industry_id"]).strip(),
        "as_of": record["as_of"],
        "model_version": record["model_version"],
        "data_cutoff_at": record["data_cutoff_at"],
        "cycle_score_reason": record.get("cycle_score_reason"),
        "representative_asset_id": record.get("representative_asset_id"),
        "representative_market": record.get("representative_market"),
        "raw_state": record.get("raw_state"),
        "confirmed_state": record.get("confirmed_state"),
        "confirmation_status": record.get("confirmation_status"),
        "action_signal": record.get("action_signal"),
        "consecutive_weeks": None if record.get("consecutive_weeks") is None else int(record["consecutive_weeks"]),
        "previous_confirmed_state": record.get("previous_confirmed_state"),
        "is_actionable": 1 if record.get("is_actionable") else 0,
        "urgent_flags_json": urgent_flags_json,
        "score_breakdown_json": score_breakdown_json,
        "created_at": _now_iso(),
    }
    for key in _FLOAT_FIELDS:
        params[key] = _f(record.get(key))

    init_db(db_path)
    with connect(db_path) as conn:
        conn.execute(_SIGNAL_UPSERT_SQL, params)


def _signal_row_to_dict(row: Any) -> Dict[str, Any]:
    d = dict(row)
    d["is_actionable"] = bool(d.get("is_actionable"))
    for json_col, out_key in (("urgent_flags_json", "urgent_flags"), ("score_breakdown_json", "score_breakdown")):
        raw = d.get(json_col)
        if raw:
            try:
                d[out_key] = json.loads(raw)
            except (TypeError, ValueError):
                d[out_key] = None
        else:
            d[out_key] = None
    return d


def get_cycle_signal(
    industry_id: str, as_of: str, model_version: str, db_path: Path | None = None
) -> Optional[Dict[str, Any]]:
    init_db(db_path)
    with connect(db_path) as conn:
        row = conn.execute(
            """
            SELECT * FROM industry_cycle_signal
            WHERE industry_id = :industry_id AND as_of = :as_of AND model_version = :model_version;
            """,
            {"industry_id": industry_id, "as_of": as_of, "model_version": model_version},
        ).fetchone()
        return _signal_row_to_dict(row) if row is not None else None


def get_latest_cycle_signal_before(
    industry_id: str, model_version: str, before_as_of: str, db_path: Path | None = None
) -> Optional[Dict[str, Any]]:
    """Return the most recent `industry_cycle_signal` row strictly before `before_as_of`.

    Used by `cycle_state_machine.apply_cycle_confirmation_rule` to compute
    the consecutive-weeks streak, mirroring `factor_repository.get_latest_price_state_before`.
    """
    init_db(db_path)
    with connect(db_path) as conn:
        row = conn.execute(
            """
            SELECT * FROM industry_cycle_signal
            WHERE industry_id = :industry_id AND model_version = :model_version AND as_of < :before_as_of
            ORDER BY as_of DESC
            LIMIT 1;
            """,
            {"industry_id": industry_id, "model_version": model_version, "before_as_of": before_as_of},
        ).fetchone()
        return _signal_row_to_dict(row) if row is not None else None


def list_cycle_signals(
    industry_id: str | None = None,
    as_of: str | None = None,
    model_version: str | None = None,
    db_path: Path | None = None,
) -> List[Dict[str, Any]]:
    init_db(db_path)
    clauses: List[str] = []
    params: Dict[str, Any] = {}
    if industry_id:
        clauses.append("industry_id = :industry_id")
        params["industry_id"] = industry_id
    if as_of:
        clauses.append("as_of = :as_of")
        params["as_of"] = as_of
    if model_version:
        clauses.append("model_version = :model_version")
        params["model_version"] = model_version
    where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
    with connect(db_path) as conn:
        rows = conn.execute(
            f"SELECT * FROM industry_cycle_signal {where} ORDER BY industry_id, as_of;", params
        ).fetchall()
        return [_signal_row_to_dict(r) for r in rows]


# --- industry_signal_reason ------------------------------------------------

_REASON_UPSERT_SQL = """
    INSERT INTO industry_signal_reason (
        industry_id, as_of, model_version, component_key, raw_value, weight, contribution,
        direction, note, created_at
    ) VALUES (
        :industry_id, :as_of, :model_version, :component_key, :raw_value, :weight, :contribution,
        :direction, :note, :created_at
    )
    ON CONFLICT(industry_id, as_of, model_version, component_key) DO UPDATE SET
        raw_value=excluded.raw_value,
        weight=excluded.weight,
        contribution=excluded.contribution,
        direction=excluded.direction,
        note=excluded.note;
"""


def upsert_industry_signal_reason(record: Dict[str, Any], db_path: Path | None = None) -> None:
    """Insert/update one row into `industry_signal_reason` (idempotent upsert)."""
    for required in ("industry_id", "as_of", "model_version", "component_key"):
        if not record.get(required):
            raise ValueError(f"industry_signal_reason record missing required field '{required}'")

    params = {
        "industry_id": str(record["industry_id"]).strip(),
        "as_of": record["as_of"],
        "model_version": record["model_version"],
        "component_key": record["component_key"],
        "raw_value": _f(record.get("raw_value")),
        "weight": _f(record.get("weight")),
        "contribution": _f(record.get("contribution")),
        "direction": record.get("direction"),
        "note": record.get("note"),
        "created_at": _now_iso(),
    }
    init_db(db_path)
    with connect(db_path) as conn:
        conn.execute(_REASON_UPSERT_SQL, params)


def replace_industry_signal_reasons(
    industry_id: str, as_of: str, model_version: str, reasons: List[Dict[str, Any]], db_path: Path | None = None
) -> int:
    """Delete existing reasons for this key then insert the given list (atomic replace).

    Used because the *set* of contributing components can legitimately
    change week to week (e.g. flow_score becomes available later), so a
    plain upsert-by-key would leave stale rows for components no longer
    present this week.
    """
    init_db(db_path)
    with connect(db_path) as conn:
        conn.execute(
            "DELETE FROM industry_signal_reason "
            "WHERE industry_id = :industry_id AND as_of = :as_of AND model_version = :model_version;",
            {"industry_id": industry_id, "as_of": as_of, "model_version": model_version},
        )
    count = 0
    for reason in reasons:
        merged = {**reason, "industry_id": industry_id, "as_of": as_of, "model_version": model_version}
        upsert_industry_signal_reason(merged, db_path=db_path)
        count += 1
    return count


def list_signal_reasons(
    industry_id: str, as_of: str, model_version: str, db_path: Path | None = None
) -> List[Dict[str, Any]]:
    init_db(db_path)
    with connect(db_path) as conn:
        rows = conn.execute(
            """
            SELECT * FROM industry_signal_reason
            WHERE industry_id = :industry_id AND as_of = :as_of AND model_version = :model_version
            ORDER BY ABS(contribution) DESC;
            """,
            {"industry_id": industry_id, "as_of": as_of, "model_version": model_version},
        ).fetchall()
        return [dict(r) for r in rows]
