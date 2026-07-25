from __future__ import annotations

"""Phase 1-B weekly price-factor CLI (dry-run by default).

Loads `config/industry_price_universe.json` (Phase 1-A) and
`config/industry_cycle_price_model.json` (Phase 1-B), builds one
`FactorTarget` per industry ETF declared in the price universe, and either:
- prints the plan (default; no DB access at all), or
- computes+persists `industry_factor_weekly` / `industry_price_state_weekly`
  rows, only when `--execute` is passed.

`--as-of` lets a past week be reproduced deterministically (point-in-time
gated via `price_repository.get_prices_as_of`) -- it defaults to today.

Not wired into `scripts/run_nightly.py` (task constraint: "기존
run_nightly.py에는 아직 연결하지 말 것").
"""

import argparse
from datetime import date
from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from committee.industry_cycle import price_factor_runner, price_model_config, price_universe

DB_PATH = ROOT_DIR / "data" / "investment.db"


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compute (and optionally persist) Phase 1-B weekly price-only factors/state."
    )
    parser.add_argument("--as-of", default=date.today().isoformat(), help="Point-in-time cutoff date (YYYY-MM-DD).")
    parser.add_argument(
        "--universe",
        default=str(price_universe.PRICE_UNIVERSE_PATH),
        help="Path to industry_price_universe.json.",
    )
    parser.add_argument(
        "--model-config",
        default=str(price_model_config.PRICE_MODEL_CONFIG_PATH),
        help="Path to industry_cycle_price_model.json.",
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Actually write industry_factor_weekly/industry_price_state_weekly rows. Without this flag, only prints the plan (dry-run; no DB access).",
    )
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    universe = price_universe.load_price_universe(Path(args.universe))
    model_config = price_model_config.load_price_model_config(Path(args.model_config))
    targets = price_factor_runner.build_targets_from_universe(universe)

    print(
        f"run_industry_price_factors_plan targets={len(targets)} as_of={args.as_of} "
        f"model_version={model_config['model_version']} execute={args.execute}"
    )
    for target in targets:
        print(
            f"  target asset_id={target.asset_id} industry_id={target.industry_id} "
            f"market={target.market} benchmark_asset_id={target.benchmark_asset_id}"
        )

    if not args.execute:
        print("run_industry_price_factors_dry_run_only (pass --execute to actually compute and write)")
        return

    results = price_factor_runner.run_factor_batch(
        targets,
        as_of=args.as_of,
        model_config=model_config,
        dry_run=False,
        db_path=DB_PATH,
    )
    for result in results:
        print(
            f"result asset_id={result.asset_id} status={result.status} "
            f"price_only_state={result.price_only_state} confirmation_status={result.confirmation_status} "
            f"action_signal={result.action_signal} error={result.error}"
        )
    ok = sum(1 for r in results if r.status == "ok")
    failed = sum(1 for r in results if r.status == "failed")
    print(f"run_industry_price_factors_done ok={ok} failed={failed} total={len(results)}")


if __name__ == "__main__":
    main()
