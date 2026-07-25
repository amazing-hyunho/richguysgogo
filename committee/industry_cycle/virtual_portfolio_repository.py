from __future__ import annotations

"""Phase 4 repository for `industry_virtual_position` (paper trading ledger).

Same NULL-not-zero and `init_db()`-before-every-call conventions as every
other Phase repository in this package. A position, once opened, is only
ever transitioned OPEN -> CLOSED in place via `close_position`; nothing here
ever deletes or re-opens a row, so re-running a week's batch is idempotent
and past ledger entries are never overwritten.
"""

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from committee.core.database import connect, init_db


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def open_position(record: Dict[str, Any], db_path: Path | None = None) -> bool:
    """Insert a new OPEN position. Returns True if inserted, False if a row for
    this `(industry_id, model_version, entry_as_of)` already existed (no-op,
    idempotent re-run)."""
    for required in ("industry_id", "model_version", "entry_as_of", "asset_id"):
        if not record.get(required):
            raise ValueError(f"industry_virtual_position record missing required field '{required}'")

    now = _now_iso()
    init_db(db_path)
    with connect(db_path) as conn:
        cursor = conn.execute(
            """
            INSERT INTO industry_virtual_position (
                industry_id, model_version, entry_as_of, entry_trade_date, asset_id, asset_market,
                entry_price, entry_state, benchmark_asset_id, benchmark_entry_price, status,
                created_at, updated_at
            ) VALUES (
                :industry_id, :model_version, :entry_as_of, :entry_trade_date, :asset_id, :asset_market,
                :entry_price, :entry_state, :benchmark_asset_id, :benchmark_entry_price, 'OPEN',
                :created_at, :updated_at
            )
            ON CONFLICT(industry_id, model_version, entry_as_of) DO NOTHING;
            """,
            {
                "industry_id": record["industry_id"],
                "model_version": record["model_version"],
                "entry_as_of": record["entry_as_of"],
                "entry_trade_date": record.get("entry_trade_date"),
                "asset_id": record["asset_id"],
                "asset_market": record.get("asset_market"),
                "entry_price": record.get("entry_price"),
                "entry_state": record.get("entry_state"),
                "benchmark_asset_id": record.get("benchmark_asset_id"),
                "benchmark_entry_price": record.get("benchmark_entry_price"),
                "created_at": now,
                "updated_at": now,
            },
        )
        return cursor.rowcount > 0


def close_position(
    position_id: int,
    *,
    exit_as_of: str,
    exit_trade_date: Optional[str],
    exit_price: Optional[float],
    exit_reason: str,
    benchmark_exit_price: Optional[float],
    db_path: Path | None = None,
) -> bool:
    """Transition one OPEN position to CLOSED. Returns True if a row was
    actually updated (False if `position_id` was already CLOSED or missing,
    i.e. an idempotent no-op on re-run)."""
    init_db(db_path)
    with connect(db_path) as conn:
        cursor = conn.execute(
            """
            UPDATE industry_virtual_position
            SET status = 'CLOSED', exit_as_of = :exit_as_of, exit_trade_date = :exit_trade_date,
                exit_price = :exit_price, exit_reason = :exit_reason,
                benchmark_exit_price = :benchmark_exit_price, updated_at = :updated_at
            WHERE id = :id AND status = 'OPEN';
            """,
            {
                "id": position_id,
                "exit_as_of": exit_as_of,
                "exit_trade_date": exit_trade_date,
                "exit_price": exit_price,
                "exit_reason": exit_reason,
                "benchmark_exit_price": benchmark_exit_price,
                "updated_at": _now_iso(),
            },
        )
        return cursor.rowcount > 0


def get_open_position(
    industry_id: str, model_version: str, db_path: Path | None = None
) -> Optional[Dict[str, Any]]:
    init_db(db_path)
    with connect(db_path) as conn:
        row = conn.execute(
            """
            SELECT * FROM industry_virtual_position
            WHERE industry_id = :industry_id AND model_version = :model_version AND status = 'OPEN'
            ORDER BY entry_as_of DESC LIMIT 1;
            """,
            {"industry_id": industry_id, "model_version": model_version},
        ).fetchone()
        return dict(row) if row is not None else None


def get_position(position_id: int, db_path: Path | None = None) -> Optional[Dict[str, Any]]:
    init_db(db_path)
    with connect(db_path) as conn:
        row = conn.execute(
            "SELECT * FROM industry_virtual_position WHERE id = :id;", {"id": position_id}
        ).fetchone()
        return dict(row) if row is not None else None


def list_positions(
    industry_id: str | None = None,
    model_version: str | None = None,
    status: str | None = None,
    db_path: Path | None = None,
) -> List[Dict[str, Any]]:
    init_db(db_path)
    clauses: List[str] = []
    params: Dict[str, Any] = {}
    if industry_id:
        clauses.append("industry_id = :industry_id")
        params["industry_id"] = industry_id
    if model_version:
        clauses.append("model_version = :model_version")
        params["model_version"] = model_version
    if status:
        clauses.append("status = :status")
        params["status"] = status
    where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
    with connect(db_path) as conn:
        rows = conn.execute(
            f"SELECT * FROM industry_virtual_position {where} ORDER BY entry_as_of, industry_id;", params
        ).fetchall()
        return [dict(r) for r in rows]
