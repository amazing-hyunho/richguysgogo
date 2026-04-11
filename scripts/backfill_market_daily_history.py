from __future__ import annotations

"""Backfill historical rows for market_daily (levels + daily pct).

Targets
- KOSPI, KOSDAQ
- S&P 500, NASDAQ, DOW
- USD/KRW

Behavior
- Fetches historical daily close from Yahoo chart API.
- Computes daily pct from consecutive valid closes.
- Upserts into market_daily without overwriting existing non-null values with NULL.
"""

import argparse
from datetime import UTC, date, datetime, timedelta
import sqlite3
import sys
import time
from pathlib import Path
from urllib.parse import quote

import requests

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from committee.core.database import init_db

DB_PATH = ROOT_DIR / "data" / "investment.db"
YAHOO_CHART_BASE = "https://query1.finance.yahoo.com/v8/finance/chart"

SERIES_META = {
    "kospi": {"symbol": "^KS11", "level_col": "kospi", "pct_col": "kospi_pct"},
    "kosdaq": {"symbol": "^KQ11", "level_col": "kosdaq", "pct_col": "kosdaq_pct"},
    "sp500": {"symbol": "^GSPC", "level_col": "sp500", "pct_col": "sp500_pct"},
    "nasdaq": {"symbol": "^IXIC", "level_col": "nasdaq", "pct_col": "nasdaq_pct"},
    "dow": {"symbol": "^DJI", "level_col": "dow", "pct_col": "dow_pct"},
    "usdkrw": {"symbol": "KRW=X", "level_col": "usdkrw", "pct_col": "usdkrw_pct"},
}


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Backfill market_daily history from Yahoo chart API.")
    parser.add_argument("--start-date", default="2020-01-01", help="Inclusive start date (YYYY-MM-DD).")
    parser.add_argument("--end-date", default=date.today().isoformat(), help="Inclusive end date (YYYY-MM-DD).")
    parser.add_argument("--dry-run", action="store_true", help="Print updates without writing to DB.")
    parser.add_argument("--sleep-ms", type=int, default=250, help="Sleep between symbol requests to reduce API pressure.")
    return parser.parse_args()


def _fetch_series(symbol: str, start_d: date, end_d: date) -> dict[str, dict[str, float | None]]:
    start_epoch = int(datetime.combine(start_d - timedelta(days=7), datetime.min.time(), tzinfo=UTC).timestamp())
    end_epoch = int(datetime.combine(end_d + timedelta(days=1), datetime.min.time(), tzinfo=UTC).timestamp())
    encoded = quote(symbol, safe="")
    url = f"{YAHOO_CHART_BASE}/{encoded}"
    response = requests.get(
        url,
        params={"interval": "1d", "period1": start_epoch, "period2": end_epoch},
        timeout=12,
        headers={"User-Agent": "DailyAIInvestmentCommittee/1.0"},
    )
    if response.status_code != 200:
        raise RuntimeError(f"http_status_{response.status_code}")
    payload = response.json()
    result = ((payload.get("chart") or {}).get("result") or [])
    if not result:
        raise RuntimeError("empty_result")
    item = result[0] or {}
    timestamps = item.get("timestamp") or []
    quotes = (((item.get("indicators") or {}).get("quote") or [{}])[0] or {})
    closes = quotes.get("close") or []
    if not timestamps or not closes:
        raise RuntimeError("missing_series_data")

    points: list[tuple[str, float]] = []
    for idx, ts in enumerate(timestamps):
        if idx >= len(closes):
            break
        close = closes[idx]
        if close is None:
            continue
        try:
            close_f = float(close)
        except Exception:
            continue
        if close_f <= 0:
            continue
        d = datetime.fromtimestamp(int(ts), UTC).date().isoformat()
        if d < start_d.isoformat() or d > end_d.isoformat():
            continue
        points.append((d, close_f))

    points.sort(key=lambda x: x[0])
    dedup: dict[str, float] = {}
    for d, c in points:
        dedup[d] = c
    ordered = sorted(dedup.items(), key=lambda x: x[0])

    out: dict[str, dict[str, float | None]] = {}
    prev_close: float | None = None
    for d, c in ordered:
        pct = None
        if prev_close is not None and prev_close != 0:
            pct = ((c - prev_close) / prev_close) * 100.0
        out[d] = {"level": c, "pct": pct}
        prev_close = c
    return out


def _upsert_rows(conn: sqlite3.Connection, by_date: dict[str, dict[str, float | None]], dry_run: bool) -> tuple[int, int]:
    inserted_or_updated = 0
    skipped = 0
    now_iso = datetime.now(UTC).isoformat().replace("+00:00", "Z")
    sql = """
        INSERT INTO market_daily (
            date, kospi_pct, kosdaq_pct, sp500_pct, nasdaq_pct, dow_pct,
            kospi, kosdaq, sp500, nasdaq, dow,
            usdkrw, usdkrw_pct, created_at
        ) VALUES (
            :date, :kospi_pct, :kosdaq_pct, :sp500_pct, :nasdaq_pct, :dow_pct,
            :kospi, :kosdaq, :sp500, :nasdaq, :dow,
            :usdkrw, :usdkrw_pct, :created_at
        )
        ON CONFLICT(date) DO UPDATE SET
            kospi_pct=COALESCE(excluded.kospi_pct, market_daily.kospi_pct),
            kosdaq_pct=COALESCE(excluded.kosdaq_pct, market_daily.kosdaq_pct),
            sp500_pct=COALESCE(excluded.sp500_pct, market_daily.sp500_pct),
            nasdaq_pct=COALESCE(excluded.nasdaq_pct, market_daily.nasdaq_pct),
            dow_pct=COALESCE(excluded.dow_pct, market_daily.dow_pct),
            kospi=COALESCE(excluded.kospi, market_daily.kospi),
            kosdaq=COALESCE(excluded.kosdaq, market_daily.kosdaq),
            sp500=COALESCE(excluded.sp500, market_daily.sp500),
            nasdaq=COALESCE(excluded.nasdaq, market_daily.nasdaq),
            dow=COALESCE(excluded.dow, market_daily.dow),
            usdkrw=COALESCE(excluded.usdkrw, market_daily.usdkrw),
            usdkrw_pct=COALESCE(excluded.usdkrw_pct, market_daily.usdkrw_pct),
            created_at=excluded.created_at
    """
    for d in sorted(by_date.keys()):
        row = by_date[d]
        has_any = any(
            row.get(k) is not None
            for k in (
                "kospi", "kospi_pct", "kosdaq", "kosdaq_pct",
                "sp500", "sp500_pct", "nasdaq", "nasdaq_pct",
                "dow", "dow_pct", "usdkrw", "usdkrw_pct",
            )
        )
        if not has_any:
            skipped += 1
            continue
        params = {"date": d, "created_at": now_iso, **row}
        if not dry_run:
            conn.execute(sql, params)
        inserted_or_updated += 1
    return inserted_or_updated, skipped


def main() -> None:
    args = _parse_args()
    start_d = date.fromisoformat(str(args.start_date))
    end_d = date.fromisoformat(str(args.end_date))
    if end_d < start_d:
        raise ValueError("end-date must be >= start-date")

    init_db(DB_PATH)
    merged: dict[str, dict[str, float | None]] = {}
    for key, meta in SERIES_META.items():
        symbol = str(meta["symbol"])
        try:
            series = _fetch_series(symbol=symbol, start_d=start_d, end_d=end_d)
            print(f"series_loaded[{key}] rows={len(series)}")
            for d, v in series.items():
                row = merged.setdefault(
                    d,
                    {
                        "kospi": None, "kospi_pct": None,
                        "kosdaq": None, "kosdaq_pct": None,
                        "sp500": None, "sp500_pct": None,
                        "nasdaq": None, "nasdaq_pct": None,
                        "dow": None, "dow_pct": None,
                        "usdkrw": None, "usdkrw_pct": None,
                    },
                )
                row[str(meta["level_col"])] = v.get("level")
                row[str(meta["pct_col"])] = v.get("pct")
        except Exception as exc:  # noqa: BLE001
            print(f"series_load_failed[{key}]: {exc}")
        time.sleep(max(0, int(args.sleep_ms)) / 1000.0)

    conn = sqlite3.connect(DB_PATH)
    try:
        changed, skipped = _upsert_rows(conn, merged, dry_run=bool(args.dry_run))
        if not args.dry_run:
            conn.commit()
        print(
            f"backfill_market_daily_done changed={changed} skipped={skipped} "
            f"range={start_d.isoformat()}..{end_d.isoformat()} dry_run={args.dry_run}"
        )
    finally:
        conn.close()


if __name__ == "__main__":
    main()

