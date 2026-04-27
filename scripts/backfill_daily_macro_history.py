from __future__ import annotations

"""Backfill daily_macro base columns by date range.

Policy
- Fill what can be fetched from Yahoo history.
- If a date has no exact market observation, store NULL (not carry-forward).
"""

import argparse
from datetime import UTC, date, datetime, timedelta
import sqlite3
from pathlib import Path
from urllib.parse import quote
import sys

import requests

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from committee.core.database import init_db


DB_PATH = ROOT_DIR / "data" / "investment.db"
YAHOO_CHART_BASE = "https://query1.finance.yahoo.com/v8/finance/chart"


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Backfill daily_macro base columns from Yahoo history.")
    parser.add_argument("--start-date", required=True, help="Inclusive start date (YYYY-MM-DD).")
    parser.add_argument("--end-date", required=True, help="Inclusive end date (YYYY-MM-DD).")
    parser.add_argument("--dry-run", action="store_true", help="Print updates without writing DB.")
    return parser.parse_args()


def _iter_dates(start_d: date, end_d: date) -> list[date]:
    out: list[date] = []
    cur = start_d
    while cur <= end_d:
        out.append(cur)
        cur += timedelta(days=1)
    return out


def _fetch_series(symbol: str, start_d: date, end_d: date) -> dict[str, float]:
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
    out: dict[str, float] = {}
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
        out[d] = close_f
    return out


def _pick(primary: dict[str, float], secondary: dict[str, float], d: str) -> float | None:
    if d in primary:
        return primary[d]
    if d in secondary:
        return secondary[d]
    return None


def _scale_tnx_like(v: float | None) -> float | None:
    if v is None:
        return None
    return (v / 10.0) if v > 20.0 else v


def main() -> None:
    args = _parse_args()
    start_d = date.fromisoformat(str(args.start_date))
    end_d = date.fromisoformat(str(args.end_date))
    if end_d < start_d:
        raise ValueError("end-date must be >= start-date")

    init_db(DB_PATH)
    days = _iter_dates(start_d, end_d)

    # Primary + fallback symbols
    tnx = _fetch_series("^TNX", start_d, end_d)
    irx = _fetch_series("^IRX", start_d, end_d)
    vix = _fetch_series("^VIX", start_d, end_d)
    dxy1 = _fetch_series("DX-Y.NYB", start_d, end_d)
    dxy2 = _fetch_series("^DXY", start_d, end_d)
    krw1 = _fetch_series("KRW=X", start_d, end_d)
    krw2 = _fetch_series("USDKRW=X", start_d, end_d)
    oil1 = _fetch_series("CL=F", start_d, end_d)
    oil2 = _fetch_series("BZ=F", start_d, end_d)

    conn = sqlite3.connect(DB_PATH)
    try:
        changed = 0
        now_iso = datetime.now(UTC).isoformat().replace("+00:00", "Z")
        for d in days:
            ds = d.isoformat()
            us10y = _scale_tnx_like(tnx.get(ds))
            us2y = _scale_tnx_like(irx.get(ds))
            spread = (us10y - us2y) if (us10y is not None and us2y is not None) else None
            vix_v = vix.get(ds)
            dxy_v = _pick(dxy1, dxy2, ds)
            usdkrw_v = _pick(krw1, krw2, ds)
            oil_v = _pick(oil1, oil2, ds)

            if args.dry_run:
                print(
                    f"{ds} us10y={us10y} us2y={us2y} spread={spread} "
                    f"vix={vix_v} dxy={dxy_v} usdkrw={usdkrw_v} oil={oil_v}"
                )
                continue

            conn.execute(
                """
                INSERT INTO daily_macro (
                    date, us10y, us2y, spread_2_10, vix, dxy, usdkrw, oil_wti, created_at
                ) VALUES (
                    :date, :us10y, :us2y, :spread_2_10, :vix, :dxy, :usdkrw, :oil_wti, :created_at
                )
                ON CONFLICT(date) DO UPDATE SET
                    us10y=excluded.us10y,
                    us2y=excluded.us2y,
                    spread_2_10=excluded.spread_2_10,
                    vix=excluded.vix,
                    dxy=excluded.dxy,
                    usdkrw=excluded.usdkrw,
                    oil_wti=excluded.oil_wti,
                    created_at=excluded.created_at;
                """,
                {
                    "date": ds,
                    "us10y": us10y,
                    "us2y": us2y,
                    "spread_2_10": spread,
                    "vix": vix_v,
                    "dxy": dxy_v,
                    "usdkrw": usdkrw_v,
                    "oil_wti": oil_v,
                    "created_at": now_iso,
                },
            )
            changed += 1
        if not args.dry_run:
            conn.commit()
        print(
            f"backfill_daily_macro_done changed={changed} "
            f"range={start_d.isoformat()}..{end_d.isoformat()} dry_run={args.dry_run}"
        )
    finally:
        conn.close()


if __name__ == "__main__":
    main()
