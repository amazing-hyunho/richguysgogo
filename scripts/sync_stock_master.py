from __future__ import annotations

from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from committee.core.database import upsert_ticker_master
from committee.tools.krx_client import fetch_stock_master


def main() -> None:
    rows = fetch_stock_master()
    total = len(rows)
    success = 0
    failed = 0

    print(f"sync_stock_master_fetched={total}")
    for row in rows:
        try:
            upsert_ticker_master(row)
            success += 1
        except Exception as exc:  # noqa: BLE001
            failed += 1
            ticker = row.get("ticker")
            print(f"sync_stock_master_upsert_failed[{ticker}]: {exc}")

    print(f"sync_stock_master_done total={total} success={success} failed={failed}")


if __name__ == "__main__":
    main()
