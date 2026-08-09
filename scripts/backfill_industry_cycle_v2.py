from __future__ import annotations

"""Backfill only the objective v2 layer from already-persisted weekly inputs."""

import argparse
from datetime import date
from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from committee.industry_cycle import (
    cycle_v2,
    cycle_v2_model_config,
    fundamentals_model_config,
    repository,
    price_model_config,
    stock_model_config,
)
from scripts.backfill_industry_cycle_history import generate_recent_weekly_dates


DB_PATH = ROOT_DIR / "data" / "investment.db"


def main() -> None:
    parser = argparse.ArgumentParser(description="Backfill objective industry cycle v2 only.")
    parser.add_argument("--weeks", type=int, default=54)
    parser.add_argument("--end-date", default=date.today().isoformat())
    parser.add_argument("--weekday", type=int, default=4)
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()

    dates = generate_recent_weekly_dates(args.end_date, args.weeks, weekday=args.weekday)
    industries = sorted(
        str(row["industry_id"])
        for row in repository.list_industries(active_only=True, db_path=DB_PATH)
    )
    config = cycle_v2_model_config.load_cycle_v2_model_config()
    fundamentals_version = fundamentals_model_config.load_fundamentals_model_config()["model_version"]
    candidate_version = stock_model_config.load_stock_model_config()["model_version"]
    price_version = price_model_config.load_price_model_config()["model_version"]
    print(
        f"backfill_industry_cycle_v2_plan weeks={len(dates)} range={dates[0]}..{dates[-1]} "
        f"industries={len(industries)} execute={args.execute}"
    )
    if not args.execute:
        return
    total = 0
    predicted = 0
    for index, as_of in enumerate(dates, start=1):
        rows = cycle_v2.compute_cycle_v2_batch(
            industries,
            as_of=as_of,
            config=config,
            fundamentals_model_version=fundamentals_version,
            candidate_model_version=candidate_version,
            price_model_version=price_version,
            persist=True,
            db_path=DB_PATH,
        )
        total += len(rows)
        predicted += sum(row.get("expected_excess_return_12w") is not None for row in rows)
        print(f"week_done index={index}/{len(dates)} as_of={as_of} rows={len(rows)}")
    print(f"backfill_industry_cycle_v2_done rows={total} predicted_rows={predicted}")


if __name__ == "__main__":
    main()
