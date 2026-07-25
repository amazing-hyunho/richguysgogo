from __future__ import annotations

"""Phase 5 (kickoff, price-only scope): threshold sensitivity analysis CLI
for the Phase 1-B PRICE-ONLY signal's `state_thresholds`.

Runs the baseline `industry_cycle_price_model.json` config AND one or more
named threshold variants over the same historical window, each persisted
under its own `model_version` (never overwriting the baseline or any other
variant -- see `committee/industry_cycle/price_walkforward.run_threshold_sensitivity`),
then prints a side-by-side win-rate / avg-excess-return comparison so a
human can judge whether the current default thresholds are meaningfully
better/worse than nearby alternatives.

Variants can be supplied via `--variants-file path/to/variants.json`
(shape: `{"variant_name": {"threshold_key": value, ...}, ...}`) or, if
omitted, three illustrative built-in variants are used (tighter/looser
recovery relative-strength band, tighter overheat threshold) purely as a
starting point -- NOT a claim that these are the "right" alternatives to
test; extending the JSON file is the intended way to explore further.

Dry-run by default; `--execute` performs real DB writes (under the
variants' own model_versions only -- the baseline run must be triggered
separately via `run_industry_price_walkforward.py` if it hasn't been run
yet).
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

_BUILTIN_VARIANTS = {
    # Baseline `recovery_relative_strength_min` is 35.0 (config/industry_cycle_price_model.json)
    # and `overheat_score_min` is 70.0 -- these variants must move meaningfully away from
    # those defaults in BOTH directions to produce a real (non-identical-to-baseline) comparison.
    "tighter_recovery_rs": {"recovery_relative_strength_min": 55.0},
    "looser_recovery_rs": {"recovery_relative_strength_min": 15.0},
    "tighter_overheat": {"overheat_score_min": 80.0},
    "looser_overheat": {"overheat_score_min": 60.0},
}


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Threshold sensitivity analysis for the Phase 1-B price-only signal."
    )
    parser.add_argument("--start", required=True, help="First as_of date to consider (YYYY-MM-DD).")
    parser.add_argument("--end", required=True, help="Last as_of date to consider (YYYY-MM-DD).")
    parser.add_argument("--weekday", type=int, default=4, help="0=Mon .. 6=Sun. Default 4 (Friday).")
    parser.add_argument(
        "--universe", default=str(price_universe.PRICE_UNIVERSE_PATH), help="Path to industry_price_universe.json."
    )
    parser.add_argument(
        "--model-config",
        default=str(price_model_config.PRICE_MODEL_CONFIG_PATH),
        help="Path to the baseline industry_cycle_price_model.json.",
    )
    parser.add_argument(
        "--variants-file",
        default=None,
        help="Path to a JSON file of {variant_name: {threshold_key: value, ...}}. "
        "Defaults to 3 illustrative built-in variants if omitted.",
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Actually run the historical backtest for each variant and write results. "
        "Without this flag, only prints the plan.",
    )
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    universe = price_universe.load_price_universe(Path(args.universe))
    base_model_config = price_model_config.load_price_model_config(Path(args.model_config))
    targets = price_factor_runner.build_targets_from_universe(universe)
    as_of_dates = price_walkforward.generate_weekly_as_of_dates(args.start, args.end, weekday=args.weekday)

    if args.variants_file:
        variants = json.loads(Path(args.variants_file).read_text(encoding="utf-8"))
    else:
        variants = _BUILTIN_VARIANTS

    print(
        f"run_industry_price_threshold_sensitivity_plan targets={len(targets)} weeks={len(as_of_dates)} "
        f"variants={list(variants.keys())} base_model_version={base_model_config['model_version']} "
        f"execute={args.execute}"
    )
    if not as_of_dates:
        print("run_industry_price_threshold_sensitivity_no_weeks_in_range")
        return

    if not args.execute:
        print(
            "run_industry_price_threshold_sensitivity_dry_run_only "
            "(pass --execute to actually run each variant's historical backtest)"
        )
        return

    results = price_walkforward.run_threshold_sensitivity(
        targets,
        as_of_dates=as_of_dates,
        base_model_config=base_model_config,
        variants=variants,
        db_path=DB_PATH,
    )

    baseline_summary = price_walkforward.summarize_by_state(base_model_config["model_version"], db_path=DB_PATH)
    print("baseline_summary_by_state_and_horizon:")
    if not baseline_summary:
        print(
            "  (empty -- run scripts/run_industry_price_walkforward.py --execute for this "
            "model_version/window first to get a baseline to compare against)"
        )
    for state, by_horizon in baseline_summary.items():
        for horizon_label, stats in by_horizon.items():
            print(f"  state={state} horizon={horizon_label} n={stats['n']} win_rate={stats['win_rate']}")

    for name, summary in results.items():
        print(f"variant={name} overrides={variants[name]}")
        if not summary:
            print("  (no actionable signal events under this variant's thresholds)")
        for state, by_horizon in summary.items():
            for horizon_label, stats in by_horizon.items():
                print(
                    f"  state={state} horizon={horizon_label} n={stats['n']} "
                    f"win_rate={stats['win_rate']} avg_excess_return={stats['avg_excess_return']}"
                )

    print(json.dumps({"baseline": baseline_summary, "variants": results}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
