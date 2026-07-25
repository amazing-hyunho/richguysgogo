from __future__ import annotations

"""Phase 5 (kickoff, price-only scope): walk-forward validation CLI for the
Phase 1-B PRICE-ONLY signal.

Scope note: this validates ONLY the price-only signal
(`committee.industry_cycle.price_state_machine`), not the full combined
`industry_cycle_signal` model from Phase 4 -- see
`committee/industry_cycle/price_walkforward.py`'s module docstring for why
(the combined model has too little real history yet for a meaningful
walk-forward test).

Steps (dry-run by default; `--execute` performs real DB writes):
1. Build one weekly `as_of` per `--weekday` between `--start` and `--end`.
2. `run_walkforward`: re-run the real production weekly pipeline
   (`price_factor_runner.run_factor_batch`) once per historical `as_of`,
   persisting `industry_factor_weekly` / `industry_price_state_weekly` rows
   exactly as the live weekly job would have.
3. `evaluate_signal_events`: for every actionable signal persisted in step
   2, compute real forward returns and persist them into
   `industry_price_signal_performance`.
4. `summarize_by_state`: print win-rate / average / median excess return
   per signal state per horizon.

Not wired into `scripts/run_nightly.py` -- this is a standalone research/
validation tool, not part of the live weekly pipeline.
"""

import argparse
import json
from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from committee.industry_cycle import price_factor_runner, price_model_config, price_universe, price_walkforward

DB_PATH = ROOT_DIR / "data" / "investment.db"


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Walk-forward validate the Phase 1-B price-only signal over real historical price data."
    )
    parser.add_argument("--start", required=True, help="First as_of date to consider (YYYY-MM-DD).")
    parser.add_argument("--end", required=True, help="Last as_of date to consider (YYYY-MM-DD).")
    parser.add_argument(
        "--weekday", type=int, default=4, help="0=Mon .. 6=Sun. Default 4 (Friday) -- one signal per calendar week."
    )
    parser.add_argument(
        "--universe", default=str(price_universe.PRICE_UNIVERSE_PATH), help="Path to industry_price_universe.json."
    )
    parser.add_argument(
        "--model-config",
        default=str(price_model_config.PRICE_MODEL_CONFIG_PATH),
        help="Path to industry_cycle_price_model.json.",
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Actually write industry_factor_weekly/industry_price_state_weekly/"
        "industry_price_signal_performance rows. Without this flag, only prints the plan.",
    )
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    universe = price_universe.load_price_universe(Path(args.universe))
    model_config = price_model_config.load_price_model_config(Path(args.model_config))
    targets = price_factor_runner.build_targets_from_universe(universe)
    as_of_dates = price_walkforward.generate_weekly_as_of_dates(args.start, args.end, weekday=args.weekday)

    print(
        f"run_industry_price_walkforward_plan targets={len(targets)} weeks={len(as_of_dates)} "
        f"start={args.start} end={args.end} model_version={model_config['model_version']} execute={args.execute}"
    )
    if not as_of_dates:
        print("run_industry_price_walkforward_no_weeks_in_range")
        return

    if not args.execute:
        print(
            "run_industry_price_walkforward_dry_run_only "
            "(pass --execute to actually run the historical backtest and write results)"
        )
        return

    tally = price_walkforward.run_walkforward(
        targets, as_of_dates=as_of_dates, model_config=model_config, db_path=DB_PATH
    )
    total_ok = sum(tally.values())
    print(f"run_walkforward_done weeks_run={len(tally)} target_weeks_ok={total_ok}")

    events = price_walkforward.evaluate_signal_events(model_config["model_version"], db_path=DB_PATH)
    print(f"evaluate_signal_events_done events_persisted={len(events)}")

    summary = price_walkforward.summarize_by_state(model_config["model_version"], db_path=DB_PATH)
    if not summary:
        print("summary: no actionable signal events were generated in this window (INSUFFICIENT_DATA)")
        return

    print("summary_by_state_and_horizon:")
    for state, by_horizon in summary.items():
        for horizon_label, stats in by_horizon.items():
            print(
                f"  state={state} horizon={horizon_label} n={stats['n']} "
                f"win_rate={stats['win_rate']} avg_excess_return={stats['avg_excess_return']} "
                f"median_excess_return={stats['median_excess_return']}"
            )

    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
