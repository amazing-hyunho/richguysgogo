from __future__ import annotations

import argparse
from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from committee.core.database import upsert_daily_price
from committee.tools.krx_client import fetch_daily_prices


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Sync KRX daily prices into daily_price_kr.")
    parser.add_argument("trade_date", help="Trade date in YYYY-MM-DD or YYYYMMDD format.")
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    rows = fetch_daily_prices(args.trade_date)
    total = len(rows)
    success = 0
    failed = 0

    print(f"sync_daily_prices_fetched={total} trade_date={args.trade_date}")
    for row in rows:
        try:
            upsert_daily_price(row)
            success += 1
        except Exception as exc:  # noqa: BLE001
            failed += 1
            ticker = row.get("ticker")
            print(f"sync_daily_prices_upsert_failed[{ticker}][{args.trade_date}]: {exc}")

    print(f"sync_daily_prices_done total={total} success={success} failed={failed} trade_date={args.trade_date}")


if __name__ == "__main__":
    main()
