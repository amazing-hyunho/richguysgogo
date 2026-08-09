from __future__ import annotations

"""Phase 4 weekly industry cycle-signal CLI (dry-run by default).

For every industry that currently has at least one asset in
`industry_asset_map` (same universe as `run_industry_candidates.py`),
computes the FINAL `cycle_score` + 5-state regime + confidence + urgent
flags (`committee.industry_cycle.cycle_runner.run_cycle_batch`, itself
built on Phase 2/3/1-B's already-computed weekly tables) and either:
- prints the plan + a per-industry summary (default; no DB writes), or
- persists `industry_cycle_signal` + `industry_signal_reason` rows, only
  when `--execute` is passed.

Run this AFTER `run_industry_fundamentals_factors.py`,
`run_industry_candidates.py`, and `run_industry_price_factors.py` for the
same `--as-of` week -- this CLI only READS their output tables, it never
recomputes them. `--as-of` defaults to today; not wired into
`scripts/run_nightly.py` (same constraint as every earlier Phase CLI).
"""

import argparse
from datetime import date
from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from committee.industry_cycle import (
    candidate_ranking,
    cycle_model_config,
    cycle_runner,
    cycle_v2,
    cycle_v2_model_config,
    fundamentals_model_config,
    price_model_config,
    repository,
    stock_model_config,
)

DB_PATH = ROOT_DIR / "data" / "investment.db"


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compute (and optionally persist) this week's industry_cycle_signal per industry."
    )
    parser.add_argument("--as-of", default=date.today().isoformat(), help="Point-in-time cutoff date (YYYY-MM-DD).")
    parser.add_argument(
        "--cycle-model-config",
        default=str(cycle_model_config.CYCLE_MODEL_CONFIG_PATH),
        help="Path to industry_cycle_model.json.",
    )
    parser.add_argument(
        "--fundamentals-model-version",
        default=fundamentals_model_config.load_fundamentals_model_config()["model_version"],
        help="model_version to read from industry_fundamentals_weekly.",
    )
    parser.add_argument(
        "--candidate-model-version",
        default=stock_model_config.load_stock_model_config()["model_version"],
        help="model_version to read from industry_earnings_breadth_weekly.",
    )
    parser.add_argument(
        "--price-model-version",
        default=price_model_config.load_price_model_config()["model_version"],
        help="model_version to read from industry_factor_weekly.",
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Actually write industry_cycle_signal/industry_signal_reason rows. Without this flag, only prints the plan.",
    )
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    cfg = cycle_model_config.load_cycle_model_config(Path(args.cycle_model_config))

    active_ids = {
        str(row["industry_id"])
        for row in repository.list_industries(active_only=True, db_path=DB_PATH)
    }
    all_mappings = [
        mapping
        for mapping in repository.list_industry_assets(db_path=DB_PATH)
        if mapping["industry_id"] in active_ids and candidate_ranking.is_valid_at(mapping, args.as_of)
    ]
    industry_ids = sorted({m["industry_id"] for m in all_mappings})

    print(
        f"run_industry_cycle_weekly_plan industries={len(industry_ids)} as_of={args.as_of} "
        f"model_version={cfg['model_version']} execute={args.execute}"
    )
    for industry_id in industry_ids:
        print(f"  target industry_id={industry_id}")

    if not args.execute:
        print("run_industry_cycle_weekly_dry_run_only (pass --execute to actually compute and write)")
        return

    results = cycle_runner.run_cycle_batch(
        industry_ids,
        as_of=args.as_of,
        cycle_model_config=cfg,
        fundamentals_model_version=args.fundamentals_model_version,
        candidate_model_version=args.candidate_model_version,
        price_model_version=args.price_model_version,
        dry_run=False,
        db_path=DB_PATH,
    )

    v2_cfg = cycle_v2_model_config.load_cycle_v2_model_config()
    v2_results = cycle_v2.compute_cycle_v2_batch(
        industry_ids,
        as_of=args.as_of,
        config=v2_cfg,
        fundamentals_model_version=args.fundamentals_model_version,
        candidate_model_version=args.candidate_model_version,
        price_model_version=args.price_model_version,
        persist=True,
        db_path=DB_PATH,
    )

    ok = 0
    failed = 0
    for r in results:
        if r.status == "ok":
            ok += 1
            flags = ",".join(r.urgent_flags) if r.urgent_flags else "none"
            print(
                f"result industry_id={r.industry_id} status=ok cycle_score={r.cycle_score} "
                f"confirmed_state={r.confirmed_state} confirmation_status={r.confirmation_status} "
                f"confidence={r.confidence} is_actionable={r.is_actionable} urgent_flags={flags}"
            )
        else:
            failed += 1
            repository.record_data_quality_event(
                event_type="cycle_signal_run_failed",
                target=r.industry_id,
                severity="medium",
                message=str(r.error),
                db_path=DB_PATH,
            )
            print(f"result industry_id={r.industry_id} status=failed error={r.error}")

    print(f"run_industry_cycle_weekly_done ok={ok} failed={failed} total={len(industry_ids)}")
    v2_predicted = sum(1 for row in v2_results if row.get("expected_excess_return_12w") is not None)
    print(
        f"run_industry_cycle_v2_weekly_done rows={len(v2_results)} "
        f"predicted={v2_predicted} model_version={v2_cfg['model_version']}"
    )


if __name__ == "__main__":
    main()
