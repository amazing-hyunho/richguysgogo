from __future__ import annotations

"""Phase 1-A repository for the common `asset_price_daily` price table.

Kept separate from `committee.industry_cycle.repository` (Phase 0 structural
tables only, by that module's own docstring) so the Phase 0 / Phase 1
boundary stays explicit as the design doc's phased rollout intends.

Conventions (matching `committee/core/database.py` and
`committee.industry_cycle.repository`):
- NULL (never 0.0) for missing/unavailable values.
- `init_db()` is called before every write so this module works standalone
  against a fresh DB (tests use a temp `db_path`).
- Re-collecting the same (asset_id, trade_date) never duplicates a row —
  enforced by the `UNIQUE(asset_id, trade_date)` constraint plus an
  upsert-on-conflict statement.
- All point-in-time reads (`get_prices_as_of`) gate on both
  `trade_date <= as_of` and `available_at <= as_of` so no query can look
  into the future (design doc 5.1).

Point-in-time contract (`available_at` vs. `collected_at`)
------------------------------------------------------------
`available_at` is when a price became available in the market — a
deterministic function of `trade_date` (see `YahooChartPriceProvider`'s
availability policy), independent of when we happened to run the backfill.
`collected_at` is our own fetch wall-clock and is audit/freshness-only; it
is never read by `get_prices_as_of`.

This distinction exists because an earlier version stored a single
`known_at` set to fetch-time `now()`. Backfilling 2015 prices in 2026
stamped every 2015 row with `known_at=2026-...`, so any as-of query before
2026 excluded all of 2015 — and re-collecting the same day made this worse
by overwriting `known_at` with an even later time, permanently erasing
point-in-time queryability. `_UPSERT_SQL` below fixes this by omitting
`available_at` from its `ON CONFLICT ... DO UPDATE SET` clause: once a row
exists, its `available_at` is immutable across re-collection, while
`collected_at` (and the OHLC values themselves, which can legitimately
change with new corporate actions) continue to refresh normally.
"""

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Union

from committee.core.database import connect, init_db
from committee.industry_cycle.price_models import AssetPriceRecord
from committee.industry_cycle.time_contract import is_known_by

RecordLike = Union[AssetPriceRecord, Dict[str, Any]]


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _as_dict(record: RecordLike) -> Dict[str, Any]:
    if isinstance(record, AssetPriceRecord):
        return {
            "asset_id": record.asset_id,
            "market": record.market,
            "currency": record.currency,
            "trade_date": record.trade_date,
            "open_price": record.open_price,
            "high_price": record.high_price,
            "low_price": record.low_price,
            "close_price": record.close_price,
            "adj_close_price": record.adj_close_price,
            "volume": record.volume,
            "adjustment_status": record.adjustment_status,
            "source": record.source,
            "source_ref": record.source_ref,
            "available_at": record.available_at,
            "collected_at": record.collected_at,
        }
    return dict(record)


# NOTE: `available_at` is intentionally absent from the `DO UPDATE SET`
# clause below. Once a row exists, re-collecting the same
# (asset_id, trade_date) must never move its available_at forward to "now"
# (that was the original bug); only `collected_at` (and the OHLC values,
# which can legitimately change with a later corporate action) refresh. The
# first INSERT for a given key still sets available_at normally.
_UPSERT_SQL = """
    INSERT INTO asset_price_daily (
        asset_id, market, currency, trade_date,
        open_price, high_price, low_price, close_price, adj_close_price,
        volume, adjustment_status, source, source_ref,
        available_at, collected_at, created_at
    ) VALUES (
        :asset_id, :market, :currency, :trade_date,
        :open_price, :high_price, :low_price, :close_price, :adj_close_price,
        :volume, :adjustment_status, :source, :source_ref,
        :available_at, :collected_at, :created_at
    )
    ON CONFLICT(asset_id, trade_date) DO UPDATE SET
        market=excluded.market,
        currency=excluded.currency,
        open_price=excluded.open_price,
        high_price=excluded.high_price,
        low_price=excluded.low_price,
        close_price=excluded.close_price,
        adj_close_price=excluded.adj_close_price,
        volume=excluded.volume,
        adjustment_status=excluded.adjustment_status,
        source=excluded.source,
        source_ref=excluded.source_ref,
        collected_at=excluded.collected_at;
"""


def _to_params(record: RecordLike, *, default_now: str) -> Dict[str, Any]:
    d = _as_dict(record)
    asset_id = str(d.get("asset_id", "")).strip()
    market = d.get("market")
    currency = d.get("currency")
    trade_date = d.get("trade_date")
    if not asset_id:
        raise ValueError("asset_id is required")
    if not trade_date:
        raise ValueError("trade_date is required")
    if not market:
        raise ValueError("market is required")
    if not currency:
        raise ValueError("currency is required")

    def _f(key: str) -> float | None:
        v = d.get(key)
        return None if v is None else float(v)

    available_at = d.get("available_at")
    if not available_at:
        # Conservative fallback so a caller that forgets to pass
        # `available_at` never ends up with a permanently-unqueryable row
        # (a NULL `available_at` fails `is_known_by` for every `as_of`).
        # End-of-day UTC on `trade_date` matches the conservative Yahoo
        # daily-bar policy documented in `YahooChartPriceProvider`.
        available_at = f"{trade_date}T23:59:59+00:00"

    return {
        "asset_id": asset_id,
        "market": market,
        "currency": currency,
        "trade_date": trade_date,
        "open_price": _f("open_price"),
        "high_price": _f("high_price"),
        "low_price": _f("low_price"),
        "close_price": _f("close_price"),
        "adj_close_price": _f("adj_close_price"),
        "volume": _f("volume"),
        "adjustment_status": d.get("adjustment_status") or "unknown",
        "source": d.get("source"),
        "source_ref": d.get("source_ref"),
        "available_at": available_at,
        "collected_at": d.get("collected_at") or default_now,
        "created_at": default_now,
    }


def upsert_asset_price_daily(record: RecordLike, db_path: Path | None = None) -> None:
    """Insert/update one row into `asset_price_daily`.

    Re-collecting the same `(asset_id, trade_date)` overwrites the existing
    row in place rather than inserting a duplicate (design doc constraint:
    "같은 가격 데이터를 재수집해도 중복되지 않아야 함").
    """
    now = _now_iso()
    init_db(db_path)
    with connect(db_path) as conn:
        conn.execute(_UPSERT_SQL, _to_params(record, default_now=now))


def bulk_upsert_asset_price_daily(
    records: Iterable[RecordLike], db_path: Path | None = None
) -> int:
    """Upsert many rows in a single transaction. Returns the number processed."""
    now = _now_iso()
    params = [_to_params(r, default_now=now) for r in records]
    if not params:
        return 0
    init_db(db_path)
    with connect(db_path) as conn:
        conn.executemany(_UPSERT_SQL, params)
    return len(params)


def get_prices(
    asset_id: str,
    *,
    start: str | None = None,
    end: str | None = None,
    db_path: Path | None = None,
) -> List[Dict[str, Any]]:
    """Return all stored rows for `asset_id` (no point-in-time gating).

    Intended for admin/debugging/data-quality use, not for
    backtest/signal code — use `get_prices_as_of` there instead.
    """
    init_db(db_path)
    query = "SELECT * FROM asset_price_daily WHERE asset_id = :asset_id"
    params: Dict[str, Any] = {"asset_id": asset_id}
    if start:
        query += " AND trade_date >= :start"
        params["start"] = start
    if end:
        query += " AND trade_date <= :end"
        params["end"] = end
    query += " ORDER BY trade_date;"
    with connect(db_path) as conn:
        rows = conn.execute(query, params).fetchall()
        return [dict(r) for r in rows]


def get_prices_as_of(
    asset_id: str,
    as_of: str,
    *,
    start: str | None = None,
    end: str | None = None,
    db_path: Path | None = None,
) -> List[Dict[str, Any]]:
    """Return rows for `asset_id` that were available as of `as_of` (leakage-safe).

    Two independent guards prevent future reference (design doc constraint
    "모든 시점 조회는 미래참조를 막아야 함"):
    - `trade_date <= as_of`: never return a price for a day after `as_of`.
    - `available_at <= as_of` (via `time_contract.is_known_by`): never
      return a row that was not yet available in the market as of `as_of`,
      even if its `trade_date` itself is in the past.

    Deliberately does NOT gate on `collected_at` — when we happened to run
    the backfill is audit/freshness metadata, not a point-in-time fact, so
    a 2015 price backfilled in 2026 is still visible to a 2020 `as_of` query
    as long as its `available_at` (computed from `trade_date`) is <= 2020.
    """
    rows = get_prices(asset_id, start=start, end=end, db_path=db_path)
    out = []
    for row in rows:
        trade_date = row.get("trade_date")
        if trade_date is None or str(trade_date) > str(as_of):
            continue
        if not is_known_by(row, as_of, known_at_field="available_at"):
            continue
        out.append(row)
    return out


def list_price_assets(db_path: Path | None = None) -> List[str]:
    """Return distinct asset_ids that have price rows stored."""
    init_db(db_path)
    with connect(db_path) as conn:
        rows = conn.execute("SELECT DISTINCT asset_id FROM asset_price_daily ORDER BY asset_id;").fetchall()
        return [r["asset_id"] for r in rows]


def count_prices(asset_id: str | None = None, db_path: Path | None = None) -> int:
    """Return the number of stored rows, optionally filtered to one asset."""
    init_db(db_path)
    with connect(db_path) as conn:
        if asset_id:
            row = conn.execute(
                "SELECT COUNT(*) AS cnt FROM asset_price_daily WHERE asset_id = :asset_id;",
                {"asset_id": asset_id},
            ).fetchone()
        else:
            row = conn.execute("SELECT COUNT(*) AS cnt FROM asset_price_daily;").fetchone()
        return int(row["cnt"]) if row else 0
