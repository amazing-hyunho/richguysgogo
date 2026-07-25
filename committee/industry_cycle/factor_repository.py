from __future__ import annotations

"""Phase 1-B repository for `industry_factor_weekly`, `industry_price_state_weekly`,
and `industry_price_signal_performance`.

Kept separate from `committee.industry_cycle.price_repository` (Phase 1-A,
`asset_price_daily` only) and from `committee.industry_cycle.repository`
(Phase 0 structural tables only), matching the established Phase boundary
convention in this package.

Conventions (matching `price_repository.py`):
- NULL (never 0.0) for missing/unavailable values.
- `init_db()` is called before every write so this module works standalone
  against a fresh DB (tests use a temp `db_path`).
- `model_version` is part of every UNIQUE key here, so re-running under a
  new model_version never overwrites an older version's row (design doc
  section 9: "model_version별 결과 재현"), while re-running the exact same
  (industry_id, asset_id, as_of/signal_at, model_version[, horizon_label])
  key is an idempotent upsert-in-place.
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from committee.core.database import connect, init_db


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _f(value: Any) -> Optional[float]:
    return None if value is None else float(value)


# --- industry_factor_weekly ---------------------------------------------------


_FACTOR_UPSERT_SQL = """
    INSERT INTO industry_factor_weekly (
        industry_id, market, asset_id, benchmark_asset_id, as_of, price_trade_date,
        model_version, data_cutoff_at, data_completeness, price_field_used,
        return_1m, return_3m, return_6m, return_12m,
        rel_return_3m, rel_return_6m, rel_return_12m,
        ma20, ma60, ma120, ma200,
        drawdown_from_52w_high, vol_20d, vol_60d, volume_change,
        relative_strength_score, trend_score, overheat_score, price_risk_score,
        score_breakdown_json, created_at
    ) VALUES (
        :industry_id, :market, :asset_id, :benchmark_asset_id, :as_of, :price_trade_date,
        :model_version, :data_cutoff_at, :data_completeness, :price_field_used,
        :return_1m, :return_3m, :return_6m, :return_12m,
        :rel_return_3m, :rel_return_6m, :rel_return_12m,
        :ma20, :ma60, :ma120, :ma200,
        :drawdown_from_52w_high, :vol_20d, :vol_60d, :volume_change,
        :relative_strength_score, :trend_score, :overheat_score, :price_risk_score,
        :score_breakdown_json, :created_at
    )
    ON CONFLICT(industry_id, asset_id, as_of, model_version) DO UPDATE SET
        market=excluded.market,
        benchmark_asset_id=excluded.benchmark_asset_id,
        price_trade_date=excluded.price_trade_date,
        data_cutoff_at=excluded.data_cutoff_at,
        data_completeness=excluded.data_completeness,
        price_field_used=excluded.price_field_used,
        return_1m=excluded.return_1m,
        return_3m=excluded.return_3m,
        return_6m=excluded.return_6m,
        return_12m=excluded.return_12m,
        rel_return_3m=excluded.rel_return_3m,
        rel_return_6m=excluded.rel_return_6m,
        rel_return_12m=excluded.rel_return_12m,
        ma20=excluded.ma20,
        ma60=excluded.ma60,
        ma120=excluded.ma120,
        ma200=excluded.ma200,
        drawdown_from_52w_high=excluded.drawdown_from_52w_high,
        vol_20d=excluded.vol_20d,
        vol_60d=excluded.vol_60d,
        volume_change=excluded.volume_change,
        relative_strength_score=excluded.relative_strength_score,
        trend_score=excluded.trend_score,
        overheat_score=excluded.overheat_score,
        price_risk_score=excluded.price_risk_score,
        score_breakdown_json=excluded.score_breakdown_json;
"""


def upsert_industry_factor_weekly(record: Dict[str, Any], db_path: Path | None = None) -> None:
    """Insert/update one row into `industry_factor_weekly` (idempotent upsert).

    `record` must include `industry_id`, `market`, `asset_id`, `as_of`,
    `model_version`, `data_cutoff_at`; every other field defaults to NULL.
    `score_breakdown` (a plain dict) is JSON-encoded into
    `score_breakdown_json` if provided; a pre-encoded `score_breakdown_json`
    string takes precedence when both are given.
    """
    now = _now_iso()
    for required in ("industry_id", "market", "asset_id", "as_of", "model_version", "data_cutoff_at"):
        if not record.get(required):
            raise ValueError(f"{required} is required")

    score_breakdown_json = record.get("score_breakdown_json")
    if score_breakdown_json is None and record.get("score_breakdown") is not None:
        score_breakdown_json = json.dumps(record["score_breakdown"])

    params = {
        "industry_id": str(record["industry_id"]).strip(),
        "market": record["market"],
        "asset_id": str(record["asset_id"]).strip(),
        "benchmark_asset_id": record.get("benchmark_asset_id"),
        "as_of": record["as_of"],
        "price_trade_date": record.get("price_trade_date"),
        "model_version": record["model_version"],
        "data_cutoff_at": record["data_cutoff_at"],
        "data_completeness": _f(record.get("data_completeness")),
        "price_field_used": record.get("price_field_used"),
        "return_1m": _f(record.get("return_1m")),
        "return_3m": _f(record.get("return_3m")),
        "return_6m": _f(record.get("return_6m")),
        "return_12m": _f(record.get("return_12m")),
        "rel_return_3m": _f(record.get("rel_return_3m")),
        "rel_return_6m": _f(record.get("rel_return_6m")),
        "rel_return_12m": _f(record.get("rel_return_12m")),
        "ma20": _f(record.get("ma20")),
        "ma60": _f(record.get("ma60")),
        "ma120": _f(record.get("ma120")),
        "ma200": _f(record.get("ma200")),
        "drawdown_from_52w_high": _f(record.get("drawdown_from_52w_high")),
        "vol_20d": _f(record.get("vol_20d")),
        "vol_60d": _f(record.get("vol_60d")),
        "volume_change": _f(record.get("volume_change")),
        "relative_strength_score": _f(record.get("relative_strength_score")),
        "trend_score": _f(record.get("trend_score")),
        "overheat_score": _f(record.get("overheat_score")),
        "price_risk_score": _f(record.get("price_risk_score")),
        "score_breakdown_json": score_breakdown_json,
        "created_at": now,
    }

    init_db(db_path)
    with connect(db_path) as conn:
        conn.execute(_FACTOR_UPSERT_SQL, params)


def get_factor_weekly(
    asset_id: str, as_of: str, model_version: str, db_path: Path | None = None
) -> Optional[Dict[str, Any]]:
    init_db(db_path)
    with connect(db_path) as conn:
        row = conn.execute(
            """
            SELECT * FROM industry_factor_weekly
            WHERE asset_id = :asset_id AND as_of = :as_of AND model_version = :model_version;
            """,
            {"asset_id": asset_id, "as_of": as_of, "model_version": model_version},
        ).fetchone()
        return dict(row) if row else None


def get_latest_factor_before(
    asset_id: str, model_version: str, before_as_of: str, db_path: Path | None = None
) -> Optional[Dict[str, Any]]:
    """Return the most recent `industry_factor_weekly` row strictly before `before_as_of`.

    Used to look up the previous week's `relative_strength_score` for the
    state machine's "is relative strength rising" recovery condition.
    """
    init_db(db_path)
    with connect(db_path) as conn:
        row = conn.execute(
            """
            SELECT * FROM industry_factor_weekly
            WHERE asset_id = :asset_id AND model_version = :model_version AND as_of < :before_as_of
            ORDER BY as_of DESC
            LIMIT 1;
            """,
            {"asset_id": asset_id, "model_version": model_version, "before_as_of": before_as_of},
        ).fetchone()
        return dict(row) if row else None


def list_factor_weekly(asset_id: str | None = None, db_path: Path | None = None) -> List[Dict[str, Any]]:
    init_db(db_path)
    with connect(db_path) as conn:
        if asset_id:
            rows = conn.execute(
                "SELECT * FROM industry_factor_weekly WHERE asset_id = :asset_id ORDER BY as_of;",
                {"asset_id": asset_id},
            ).fetchall()
        else:
            rows = conn.execute("SELECT * FROM industry_factor_weekly ORDER BY asset_id, as_of;").fetchall()
        return [dict(r) for r in rows]


# --- industry_price_state_weekly ----------------------------------------------


_STATE_UPSERT_SQL = """
    INSERT INTO industry_price_state_weekly (
        industry_id, market, asset_id, as_of, model_version,
        price_only_state, confirmation_status, action_signal, consecutive_weeks,
        previous_state, data_completeness, reason, contributing_factors_json, created_at
    ) VALUES (
        :industry_id, :market, :asset_id, :as_of, :model_version,
        :price_only_state, :confirmation_status, :action_signal, :consecutive_weeks,
        :previous_state, :data_completeness, :reason, :contributing_factors_json, :created_at
    )
    ON CONFLICT(industry_id, asset_id, as_of, model_version) DO UPDATE SET
        market=excluded.market,
        price_only_state=excluded.price_only_state,
        confirmation_status=excluded.confirmation_status,
        action_signal=excluded.action_signal,
        consecutive_weeks=excluded.consecutive_weeks,
        previous_state=excluded.previous_state,
        data_completeness=excluded.data_completeness,
        reason=excluded.reason,
        contributing_factors_json=excluded.contributing_factors_json;
"""


def upsert_price_state_weekly(record: Dict[str, Any], db_path: Path | None = None) -> None:
    """Insert/update one row into `industry_price_state_weekly` (idempotent upsert)."""
    now = _now_iso()
    for required in ("industry_id", "market", "asset_id", "as_of", "model_version", "price_only_state"):
        if not record.get(required):
            raise ValueError(f"{required} is required")

    contributing_factors_json = record.get("contributing_factors_json")
    if contributing_factors_json is None and record.get("contributing_factors") is not None:
        contributing_factors_json = json.dumps(record["contributing_factors"])

    params = {
        "industry_id": str(record["industry_id"]).strip(),
        "market": record["market"],
        "asset_id": str(record["asset_id"]).strip(),
        "as_of": record["as_of"],
        "model_version": record["model_version"],
        "price_only_state": record["price_only_state"],
        "confirmation_status": record.get("confirmation_status"),
        "action_signal": record.get("action_signal"),
        "consecutive_weeks": None if record.get("consecutive_weeks") is None else int(record["consecutive_weeks"]),
        "previous_state": record.get("previous_state"),
        "data_completeness": _f(record.get("data_completeness")),
        "reason": record.get("reason"),
        "contributing_factors_json": contributing_factors_json,
        "created_at": now,
    }

    init_db(db_path)
    with connect(db_path) as conn:
        conn.execute(_STATE_UPSERT_SQL, params)


def get_price_state_weekly(
    asset_id: str, as_of: str, model_version: str, db_path: Path | None = None
) -> Optional[Dict[str, Any]]:
    init_db(db_path)
    with connect(db_path) as conn:
        row = conn.execute(
            """
            SELECT * FROM industry_price_state_weekly
            WHERE asset_id = :asset_id AND as_of = :as_of AND model_version = :model_version;
            """,
            {"asset_id": asset_id, "as_of": as_of, "model_version": model_version},
        ).fetchone()
        return dict(row) if row else None


def get_latest_price_state_before(
    asset_id: str, model_version: str, before_as_of: str, db_path: Path | None = None
) -> Optional[Dict[str, Any]]:
    """Return the most recent `industry_price_state_weekly` row strictly before `before_as_of`.

    Used by `price_state_machine.apply_confirmation_rule` to compute the
    consecutive-weeks streak.
    """
    init_db(db_path)
    with connect(db_path) as conn:
        row = conn.execute(
            """
            SELECT * FROM industry_price_state_weekly
            WHERE asset_id = :asset_id AND model_version = :model_version AND as_of < :before_as_of
            ORDER BY as_of DESC
            LIMIT 1;
            """,
            {"asset_id": asset_id, "model_version": model_version, "before_as_of": before_as_of},
        ).fetchone()
        return dict(row) if row else None


def list_price_state_weekly(asset_id: str | None = None, db_path: Path | None = None) -> List[Dict[str, Any]]:
    init_db(db_path)
    with connect(db_path) as conn:
        if asset_id:
            rows = conn.execute(
                "SELECT * FROM industry_price_state_weekly WHERE asset_id = :asset_id ORDER BY as_of;",
                {"asset_id": asset_id},
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM industry_price_state_weekly ORDER BY asset_id, as_of;"
            ).fetchall()
        return [dict(r) for r in rows]


# --- industry_price_signal_performance -----------------------------------------


_PERFORMANCE_UPSERT_SQL = """
    INSERT INTO industry_price_signal_performance (
        industry_id, market, asset_id, benchmark_asset_id, signal_at, signal_state,
        model_version, horizon_label, horizon_trading_days,
        asset_return, benchmark_return, excess_return, mfe, mae, evaluated_at, created_at
    ) VALUES (
        :industry_id, :market, :asset_id, :benchmark_asset_id, :signal_at, :signal_state,
        :model_version, :horizon_label, :horizon_trading_days,
        :asset_return, :benchmark_return, :excess_return, :mfe, :mae, :evaluated_at, :created_at
    )
    ON CONFLICT(industry_id, asset_id, signal_at, model_version, horizon_label) DO UPDATE SET
        market=excluded.market,
        benchmark_asset_id=excluded.benchmark_asset_id,
        signal_state=excluded.signal_state,
        horizon_trading_days=excluded.horizon_trading_days,
        asset_return=excluded.asset_return,
        benchmark_return=excluded.benchmark_return,
        excess_return=excluded.excess_return,
        mfe=excluded.mfe,
        mae=excluded.mae,
        evaluated_at=excluded.evaluated_at;
"""


def upsert_price_signal_performance(record: Dict[str, Any], db_path: Path | None = None) -> None:
    """Insert/update one row into `industry_price_signal_performance` (idempotent upsert)."""
    now = _now_iso()
    for required in ("industry_id", "market", "asset_id", "signal_at", "model_version", "horizon_label"):
        if not record.get(required):
            raise ValueError(f"{required} is required")

    params = {
        "industry_id": str(record["industry_id"]).strip(),
        "market": record["market"],
        "asset_id": str(record["asset_id"]).strip(),
        "benchmark_asset_id": record.get("benchmark_asset_id"),
        "signal_at": record["signal_at"],
        "signal_state": record.get("signal_state"),
        "model_version": record["model_version"],
        "horizon_label": record["horizon_label"],
        "horizon_trading_days": (
            None if record.get("horizon_trading_days") is None else int(record["horizon_trading_days"])
        ),
        "asset_return": _f(record.get("asset_return")),
        "benchmark_return": _f(record.get("benchmark_return")),
        "excess_return": _f(record.get("excess_return")),
        "mfe": _f(record.get("mfe")),
        "mae": _f(record.get("mae")),
        "evaluated_at": record.get("evaluated_at") or now,
        "created_at": now,
    }

    init_db(db_path)
    with connect(db_path) as conn:
        conn.execute(_PERFORMANCE_UPSERT_SQL, params)


def bulk_upsert_price_signal_performance(records: Iterable[Dict[str, Any]], db_path: Path | None = None) -> int:
    count = 0
    for record in records:
        upsert_price_signal_performance(record, db_path=db_path)
        count += 1
    return count


def list_price_signal_performance(
    asset_id: str | None = None, db_path: Path | None = None
) -> List[Dict[str, Any]]:
    init_db(db_path)
    with connect(db_path) as conn:
        if asset_id:
            rows = conn.execute(
                """
                SELECT * FROM industry_price_signal_performance
                WHERE asset_id = :asset_id ORDER BY signal_at, horizon_label;
                """,
                {"asset_id": asset_id},
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM industry_price_signal_performance ORDER BY asset_id, signal_at, horizon_label;"
            ).fetchall()
        return [dict(r) for r in rows]
