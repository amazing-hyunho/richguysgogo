from __future__ import annotations

"""Persistence for the objective two-axis industry-cycle signal."""

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from committee.core.database import connect, init_db


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _float_or_none(value: Any) -> float | None:
    return None if value is None else float(value)


def upsert_cycle_v2_signal(record: dict[str, Any], db_path: Path | None = None) -> None:
    for key in ("industry_id", "as_of", "model_version"):
        if not str(record.get(key) or "").strip():
            raise ValueError(f"industry_cycle_v2_signal missing required field '{key}'")
    params = {
        "industry_id": record["industry_id"],
        "as_of": record["as_of"],
        "model_version": record["model_version"],
        "kpi_cycle_score": _float_or_none(record.get("kpi_cycle_score")),
        "kpi_raw_score": _float_or_none(record.get("kpi_raw_score")),
        "kpi_slope_4w": _float_or_none(record.get("kpi_slope_4w")),
        "cycle_phase": record.get("cycle_phase"),
        "market_confirmation_score": _float_or_none(record.get("market_confirmation_score")),
        "relative_strength_percentile": _float_or_none(record.get("relative_strength_percentile")),
        "breadth_percentile": _float_or_none(record.get("breadth_percentile")),
        "earnings_revision_percentile": _float_or_none(record.get("earnings_revision_percentile")),
        "overheat_percentile": _float_or_none(record.get("overheat_percentile")),
        "expected_excess_return_12w": _float_or_none(record.get("expected_excess_return_12w")),
        "upside_probability_12w": _float_or_none(record.get("upside_probability_12w")),
        "prediction_confidence": record.get("prediction_confidence"),
        "training_sample_count": int(record.get("training_sample_count") or 0),
        "training_week_count": int(record.get("training_week_count") or 0),
        "selected_ridge_lambda": _float_or_none(record.get("selected_ridge_lambda")),
        "data_completeness": _float_or_none(record.get("data_completeness")),
        "entry_signal": record.get("entry_signal"),
        "entry_reason": record.get("entry_reason"),
        "created_at": _now_iso(),
    }
    init_db(db_path)
    with connect(db_path) as conn:
        conn.execute(
            """
            INSERT INTO industry_cycle_v2_signal (
                industry_id, as_of, model_version,
                kpi_cycle_score, kpi_raw_score, kpi_slope_4w, cycle_phase,
                market_confirmation_score, relative_strength_percentile,
                breadth_percentile, earnings_revision_percentile, overheat_percentile,
                expected_excess_return_12w, upside_probability_12w,
                prediction_confidence, training_sample_count, training_week_count,
                selected_ridge_lambda, data_completeness, entry_signal, entry_reason, created_at
            ) VALUES (
                :industry_id, :as_of, :model_version,
                :kpi_cycle_score, :kpi_raw_score, :kpi_slope_4w, :cycle_phase,
                :market_confirmation_score, :relative_strength_percentile,
                :breadth_percentile, :earnings_revision_percentile, :overheat_percentile,
                :expected_excess_return_12w, :upside_probability_12w,
                :prediction_confidence, :training_sample_count, :training_week_count,
                :selected_ridge_lambda, :data_completeness, :entry_signal, :entry_reason, :created_at
            )
            ON CONFLICT(industry_id, as_of, model_version) DO UPDATE SET
                kpi_cycle_score=excluded.kpi_cycle_score,
                kpi_raw_score=excluded.kpi_raw_score,
                kpi_slope_4w=excluded.kpi_slope_4w,
                cycle_phase=excluded.cycle_phase,
                market_confirmation_score=excluded.market_confirmation_score,
                relative_strength_percentile=excluded.relative_strength_percentile,
                breadth_percentile=excluded.breadth_percentile,
                earnings_revision_percentile=excluded.earnings_revision_percentile,
                overheat_percentile=excluded.overheat_percentile,
                expected_excess_return_12w=excluded.expected_excess_return_12w,
                upside_probability_12w=excluded.upside_probability_12w,
                prediction_confidence=excluded.prediction_confidence,
                training_sample_count=excluded.training_sample_count,
                training_week_count=excluded.training_week_count,
                selected_ridge_lambda=excluded.selected_ridge_lambda,
                data_completeness=excluded.data_completeness,
                entry_signal=excluded.entry_signal,
                entry_reason=excluded.entry_reason,
                created_at=excluded.created_at;
            """,
            params,
        )


def list_cycle_v2_signals(
    industry_id: str | None = None,
    *,
    as_of: str | None = None,
    model_version: str | None = None,
    before_as_of: str | None = None,
    db_path: Path | None = None,
) -> list[dict[str, Any]]:
    init_db(db_path)
    clauses: list[str] = []
    params: dict[str, Any] = {}
    for key, value in (("industry_id", industry_id), ("as_of", as_of), ("model_version", model_version)):
        if value:
            clauses.append(f"{key} = :{key}")
            params[key] = value
    if before_as_of:
        clauses.append("as_of < :before_as_of")
        params["before_as_of"] = before_as_of
    where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
    with connect(db_path) as conn:
        rows = conn.execute(
            f"SELECT * FROM industry_cycle_v2_signal {where} ORDER BY as_of, industry_id;", params
        ).fetchall()
        return [dict(row) for row in rows]


def get_latest_cycle_v2_signal(
    industry_id: str, model_version: str, db_path: Path | None = None
) -> dict[str, Any] | None:
    init_db(db_path)
    with connect(db_path) as conn:
        row = conn.execute(
            """
            SELECT * FROM industry_cycle_v2_signal
            WHERE industry_id = :industry_id AND model_version = :model_version
            ORDER BY as_of DESC LIMIT 1;
            """,
            {"industry_id": industry_id, "model_version": model_version},
        ).fetchone()
        return dict(row) if row else None
