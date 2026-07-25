from __future__ import annotations

"""Phase 3 repository for `industry_earnings_breadth_weekly` and `industry_candidate`.

Same conventions as `fundamentals_repository.py`: NULL for missing values,
`init_db()` before every write, `model_version` part of the UNIQUE key so a
model-version bump never overwrites an older version's row while re-running
the SAME key is an idempotent upsert-in-place.
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


# --- industry_earnings_breadth_weekly ---------------------------------------

_EARNINGS_BREADTH_UPSERT_SQL = """
    INSERT INTO industry_earnings_breadth_weekly (
        industry_id, as_of, model_version, data_cutoff_at,
        earnings_revision_score, earnings_revision_weighted_sum, earnings_revision_reason,
        earnings_revision_data_completeness, earnings_revision_evidence_json,
        breadth_score, breadth_weighted_sum, breadth_reason,
        breadth_data_completeness, breadth_evidence_json,
        n_tickers_considered, created_at
    ) VALUES (
        :industry_id, :as_of, :model_version, :data_cutoff_at,
        :earnings_revision_score, :earnings_revision_weighted_sum, :earnings_revision_reason,
        :earnings_revision_data_completeness, :earnings_revision_evidence_json,
        :breadth_score, :breadth_weighted_sum, :breadth_reason,
        :breadth_data_completeness, :breadth_evidence_json,
        :n_tickers_considered, :created_at
    )
    ON CONFLICT(industry_id, as_of, model_version) DO UPDATE SET
        data_cutoff_at=excluded.data_cutoff_at,
        earnings_revision_score=excluded.earnings_revision_score,
        earnings_revision_weighted_sum=excluded.earnings_revision_weighted_sum,
        earnings_revision_reason=excluded.earnings_revision_reason,
        earnings_revision_data_completeness=excluded.earnings_revision_data_completeness,
        earnings_revision_evidence_json=excluded.earnings_revision_evidence_json,
        breadth_score=excluded.breadth_score,
        breadth_weighted_sum=excluded.breadth_weighted_sum,
        breadth_reason=excluded.breadth_reason,
        breadth_data_completeness=excluded.breadth_data_completeness,
        breadth_evidence_json=excluded.breadth_evidence_json,
        n_tickers_considered=excluded.n_tickers_considered;
"""


def upsert_industry_earnings_breadth_weekly(record: Dict[str, Any], db_path: Path | None = None) -> None:
    """Insert/update one row into `industry_earnings_breadth_weekly` (idempotent upsert).

    `record` must include `industry_id`, `as_of`, `model_version`,
    `data_cutoff_at`. `earnings_revision_evidence`/`breadth_evidence` (lists
    of plain dicts) are JSON-encoded if provided; pre-encoded
    `*_evidence_json` strings take precedence when both are given.
    """
    now = _now_iso()
    for required in ("industry_id", "as_of", "model_version", "data_cutoff_at"):
        if not record.get(required):
            raise ValueError(f"industry_earnings_breadth_weekly record missing required field '{required}'")

    er_evidence_json = record.get("earnings_revision_evidence_json")
    if er_evidence_json is None and record.get("earnings_revision_evidence") is not None:
        er_evidence_json = json.dumps(record["earnings_revision_evidence"], ensure_ascii=True)

    breadth_evidence_json = record.get("breadth_evidence_json")
    if breadth_evidence_json is None and record.get("breadth_evidence") is not None:
        breadth_evidence_json = json.dumps(record["breadth_evidence"], ensure_ascii=True)

    params = {
        "industry_id": record["industry_id"],
        "as_of": record["as_of"],
        "model_version": record["model_version"],
        "data_cutoff_at": record["data_cutoff_at"],
        "earnings_revision_score": _f(record.get("earnings_revision_score")),
        "earnings_revision_weighted_sum": _f(record.get("earnings_revision_weighted_sum")),
        "earnings_revision_reason": record.get("earnings_revision_reason"),
        "earnings_revision_data_completeness": _f(record.get("earnings_revision_data_completeness")),
        "earnings_revision_evidence_json": er_evidence_json,
        "breadth_score": _f(record.get("breadth_score")),
        "breadth_weighted_sum": _f(record.get("breadth_weighted_sum")),
        "breadth_reason": record.get("breadth_reason"),
        "breadth_data_completeness": _f(record.get("breadth_data_completeness")),
        "breadth_evidence_json": breadth_evidence_json,
        "n_tickers_considered": (
            None if record.get("n_tickers_considered") is None else int(record["n_tickers_considered"])
        ),
        "created_at": now,
    }
    init_db(db_path)
    with connect(db_path) as conn:
        conn.execute(_EARNINGS_BREADTH_UPSERT_SQL, params)


def _earnings_breadth_row_to_dict(row: Any) -> Dict[str, Any]:
    d = dict(row)
    for json_field, out_field in (
        ("earnings_revision_evidence_json", "earnings_revision_evidence"),
        ("breadth_evidence_json", "breadth_evidence"),
    ):
        if d.get(json_field):
            try:
                d[out_field] = json.loads(d[json_field])
            except (TypeError, ValueError):
                d[out_field] = None
        else:
            d[out_field] = None
    return d


def get_earnings_breadth_weekly(
    industry_id: str, as_of: str, model_version: str, db_path: Path | None = None
) -> Optional[Dict[str, Any]]:
    init_db(db_path)
    with connect(db_path) as conn:
        row = conn.execute(
            """
            SELECT * FROM industry_earnings_breadth_weekly
            WHERE industry_id = :industry_id AND as_of = :as_of AND model_version = :model_version;
            """,
            {"industry_id": industry_id, "as_of": as_of, "model_version": model_version},
        ).fetchone()
        return _earnings_breadth_row_to_dict(row) if row is not None else None


def list_earnings_breadth_weekly(
    industry_id: str | None = None, db_path: Path | None = None
) -> List[Dict[str, Any]]:
    init_db(db_path)
    with connect(db_path) as conn:
        if industry_id:
            rows = conn.execute(
                "SELECT * FROM industry_earnings_breadth_weekly WHERE industry_id = :id ORDER BY as_of;",
                {"id": industry_id},
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM industry_earnings_breadth_weekly ORDER BY industry_id, as_of;"
            ).fetchall()
        return [_earnings_breadth_row_to_dict(r) for r in rows]


# --- industry_candidate ------------------------------------------------------

_CANDIDATE_UPSERT_SQL = """
    INSERT INTO industry_candidate (
        industry_id, as_of, model_version, data_cutoff_at,
        asset_id, asset_type, market, score, rank, excluded,
        exclusion_reasons_json, unknown_checks_json, sub_scores_json, data_completeness,
        created_at
    ) VALUES (
        :industry_id, :as_of, :model_version, :data_cutoff_at,
        :asset_id, :asset_type, :market, :score, :rank, :excluded,
        :exclusion_reasons_json, :unknown_checks_json, :sub_scores_json, :data_completeness,
        :created_at
    )
    ON CONFLICT(industry_id, as_of, model_version, asset_id) DO UPDATE SET
        data_cutoff_at=excluded.data_cutoff_at,
        asset_type=excluded.asset_type,
        market=excluded.market,
        score=excluded.score,
        rank=excluded.rank,
        excluded=excluded.excluded,
        exclusion_reasons_json=excluded.exclusion_reasons_json,
        unknown_checks_json=excluded.unknown_checks_json,
        sub_scores_json=excluded.sub_scores_json,
        data_completeness=excluded.data_completeness;
"""


def upsert_industry_candidate(record: Dict[str, Any], db_path: Path | None = None) -> None:
    """Insert/update one row into `industry_candidate` (idempotent upsert).

    `record` must include `industry_id`, `as_of`, `model_version`,
    `data_cutoff_at`, `asset_id`, `asset_type`. An excluded candidate should
    pass `excluded=True, rank=None` -- `rank` is never set for an excluded
    asset (see database.py's table comment).
    """
    now = _now_iso()
    for required in ("industry_id", "as_of", "model_version", "data_cutoff_at", "asset_id", "asset_type"):
        if not record.get(required):
            raise ValueError(f"industry_candidate record missing required field '{required}'")

    exclusion_reasons_json = record.get("exclusion_reasons_json")
    if exclusion_reasons_json is None and record.get("exclusion_reasons") is not None:
        exclusion_reasons_json = json.dumps(record["exclusion_reasons"], ensure_ascii=True)

    unknown_checks_json = record.get("unknown_checks_json")
    if unknown_checks_json is None and record.get("unknown_checks") is not None:
        unknown_checks_json = json.dumps(record["unknown_checks"], ensure_ascii=True)

    sub_scores_json = record.get("sub_scores_json")
    if sub_scores_json is None and record.get("sub_scores") is not None:
        sub_scores_json = json.dumps(record["sub_scores"], ensure_ascii=True)

    params = {
        "industry_id": record["industry_id"],
        "as_of": record["as_of"],
        "model_version": record["model_version"],
        "data_cutoff_at": record["data_cutoff_at"],
        "asset_id": record["asset_id"],
        "asset_type": record["asset_type"],
        "market": record.get("market"),
        "score": _f(record.get("score")),
        "rank": None if record.get("rank") is None else int(record["rank"]),
        "excluded": 1 if record.get("excluded") else 0,
        "exclusion_reasons_json": exclusion_reasons_json,
        "unknown_checks_json": unknown_checks_json,
        "sub_scores_json": sub_scores_json,
        "data_completeness": _f(record.get("data_completeness")),
        "created_at": now,
    }
    init_db(db_path)
    with connect(db_path) as conn:
        conn.execute(_CANDIDATE_UPSERT_SQL, params)


def _candidate_row_to_dict(row: Any) -> Dict[str, Any]:
    d = dict(row)
    d["excluded"] = bool(d.get("excluded"))
    for json_field, out_field in (
        ("exclusion_reasons_json", "exclusion_reasons"),
        ("unknown_checks_json", "unknown_checks"),
        ("sub_scores_json", "sub_scores"),
    ):
        if d.get(json_field):
            try:
                d[out_field] = json.loads(d[json_field])
            except (TypeError, ValueError):
                d[out_field] = None
        else:
            d[out_field] = None
    return d


def list_industry_candidates(
    industry_id: str,
    as_of: str,
    model_version: str,
    *,
    asset_type: str | None = None,
    include_excluded: bool = True,
    db_path: Path | None = None,
) -> List[Dict[str, Any]]:
    """Return every candidate row for one `(industry_id, as_of, model_version)`.

    Ordered by `rank` (nulls -- i.e. excluded rows -- last), then `score`
    descending, so callers get a ready-to-display ranked list without extra
    sorting. Set `include_excluded=False` to see only the ranked (passing)
    candidates.
    """
    init_db(db_path)
    query = (
        "SELECT * FROM industry_candidate WHERE industry_id = :industry_id "
        "AND as_of = :as_of AND model_version = :model_version"
    )
    params: Dict[str, Any] = {"industry_id": industry_id, "as_of": as_of, "model_version": model_version}
    if asset_type:
        query += " AND asset_type = :asset_type"
        params["asset_type"] = asset_type
    if not include_excluded:
        query += " AND excluded = 0"
    query += " ORDER BY (rank IS NULL), rank, score DESC;"
    with connect(db_path) as conn:
        rows = conn.execute(query, params).fetchall()
        return [_candidate_row_to_dict(r) for r in rows]


def get_industry_candidate(
    industry_id: str, as_of: str, model_version: str, asset_id: str, db_path: Path | None = None
) -> Optional[Dict[str, Any]]:
    init_db(db_path)
    with connect(db_path) as conn:
        row = conn.execute(
            """
            SELECT * FROM industry_candidate
            WHERE industry_id = :industry_id AND as_of = :as_of
              AND model_version = :model_version AND asset_id = :asset_id;
            """,
            {"industry_id": industry_id, "as_of": as_of, "model_version": model_version, "asset_id": asset_id},
        ).fetchone()
        return _candidate_row_to_dict(row) if row is not None else None
