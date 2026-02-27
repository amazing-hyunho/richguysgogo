from __future__ import annotations

"""Backfill newly added macro indicators for existing daily_macro dates.

Targets
- vix3m
- vix_term_spread
- hy_oas
- ig_oas
- fed_balance_sheet

Notes
- Uses best-effort fetch and writes NULL when source unavailable.
- Updates only target columns (does NOT overwrite existing daily_macro fields).
"""

import argparse
import os
import sqlite3
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

import requests

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from committee.core.database import init_db


def _import_yfinance():
    try:
        import yfinance as yf  # type: ignore

        return yf
    except Exception as exc:  # noqa: BLE001
        print(f"backfill_yfinance_import_failed: {exc}")
        return None


def _fetch_yahoo_close_on_or_before(symbol: str, asof: date, lookback_days: int = 7) -> float | None:
    yf = _import_yfinance()
    if yf is None:
        return None
    try:
        start = (asof - timedelta(days=lookback_days)).isoformat()
        end = (asof + timedelta(days=1)).isoformat()
        hist = yf.Ticker(symbol).history(start=start, end=end)
        if hist is None or getattr(hist, "empty", True):
            return None
        close_series = hist.get("Close")
        if close_series is None or len(close_series) < 1:
            return None
        # history is already <= end; pick last available close
        value = float(close_series.iloc[-1])
        if value <= 0:
            return None
        return value
    except Exception as exc:  # noqa: BLE001
        print(f"backfill_yahoo_fetch_failed[{symbol}][{asof.isoformat()}]: {exc}")
        return None


def _fred_key() -> str | None:
    raw = os.getenv("FRED_API_KEY")
    if not raw:
        return None
    return raw.strip().strip('"').strip("'").strip()


def _fetch_fred_on_or_before(series_id: str, asof: date) -> float | None:
    key = _fred_key()
    if not key:
        return None
    try:
        resp = requests.get(
            "https://api.stlouisfed.org/fred/series/observations",
            params={
                "series_id": series_id,
                "api_key": key,
                "file_type": "json",
                "sort_order": "desc",
                "observation_end": asof.isoformat(),
                "limit": 5,
            },
            timeout=10,
        )
        if resp.status_code != 200:
            return None
        obs = (resp.json() or {}).get("observations", [])
        for item in obs:
            raw = item.get("value")
            if raw in (None, "", "."):
                continue
            try:
                return float(raw)
            except Exception:
                continue
        return None
    except Exception as exc:  # noqa: BLE001
        print(f"backfill_fred_fetch_failed[{series_id}][{asof.isoformat()}]: {exc}")
        return None


def _fetch_row_values(asof: date) -> dict[str, float | None]:
    vix = _fetch_yahoo_close_on_or_before("^VIX", asof)
    vix3m = _fetch_yahoo_close_on_or_before("^VIX3M", asof)
    return {
        "vix3m": vix3m,
        "vix_term_spread": (vix3m - vix) if (vix3m is not None and vix is not None) else None,
        "hy_oas": _fetch_fred_on_or_before("BAMLH0A0HYM2", asof),
        "ig_oas": _fetch_fred_on_or_before("BAMLC0A0CM", asof),
        "fed_balance_sheet": _fetch_fred_on_or_before("WALCL", asof),
    }


DB_PATH = ROOT_DIR / "data" / "investment.db"

def main() -> None:
    parser = argparse.ArgumentParser(description="Backfill new macro indicator columns in daily_macro.")
    parser.add_argument("--dry-run", action="store_true", help="Do not write DB updates; only print what would change.")
    parser.add_argument("--limit", type=int, default=0, help="Max rows to process (0 means all).")
    args = parser.parse_args()

    init_db(DB_PATH)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute(
            """
            SELECT date
            FROM daily_macro
            WHERE vix3m IS NULL
               OR vix_term_spread IS NULL
               OR hy_oas IS NULL
               OR ig_oas IS NULL
               OR fed_balance_sheet IS NULL
            ORDER BY date
            """
        ).fetchall()

        if args.limit and args.limit > 0:
            rows = rows[: args.limit]

        print(f"backfill_targets={len(rows)} dry_run={args.dry_run}")
        for row in rows:
            d = date.fromisoformat(str(row["date"]))
            values = _fetch_row_values(d)
            print(f"{d.isoformat()} -> {values}")
            if args.dry_run:
                continue
            conn.execute(
                """
                UPDATE daily_macro
                SET vix3m = :vix3m,
                    vix_term_spread = :vix_term_spread,
                    hy_oas = :hy_oas,
                    ig_oas = :ig_oas,
                    fed_balance_sheet = :fed_balance_sheet,
                    created_at = :created_at
                WHERE date = :date
                """,
                {
                    "date": d.isoformat(),
                    "vix3m": values["vix3m"],
                    "vix_term_spread": values["vix_term_spread"],
                    "hy_oas": values["hy_oas"],
                    "ig_oas": values["ig_oas"],
                    "fed_balance_sheet": values["fed_balance_sheet"],
                    "created_at": datetime.utcnow().isoformat() + "Z",
                },
            )
        if not args.dry_run:
            conn.commit()
            print("backfill_complete=1")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
