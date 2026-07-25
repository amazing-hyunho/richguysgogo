from __future__ import annotations

"""Phase 4 virtual-portfolio (paper trading ledger) weekly CLI (dry-run by default).

Reads `industry_cycle_signal` rows already computed by
`run_industry_cycle_weekly.py --execute` for `--as-of` and either:
- prints what would open/close (default; no DB writes to
  `industry_virtual_position`), or
- actually applies `committee.industry_cycle.virtual_portfolio` open/close
  rules and writes to the ledger, only when `--execute` is passed.

This CLI NEVER places a real order -- it only maintains a paper-trading
ledger row per industry (design doc section 14: "법적·투자 위험 | 의사결정
보조 및 모의 운용, 자동 주문 제외"). Run this AFTER
`run_industry_cycle_weekly.py --execute` for the same `--as-of` -- this CLI
only READS `industry_cycle_signal`, it never computes cycle scores itself.
"""

import argparse
from datetime import date
from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from committee.industry_cycle import cycle_model_config, cycle_repository, virtual_portfolio

DB_PATH = ROOT_DIR / "data" / "investment.db"


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Apply this week's industry_cycle_signal rows to the virtual portfolio ledger."
    )
    parser.add_argument("--as-of", default=date.today().isoformat(), help="Point-in-time cutoff date (YYYY-MM-DD).")
    parser.add_argument(
        "--cycle-model-config",
        default=str(cycle_model_config.CYCLE_MODEL_CONFIG_PATH),
        help="Path to industry_cycle_model.json.",
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Actually write industry_virtual_position rows. Without this flag, only prints the plan.",
    )
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    cfg = cycle_model_config.load_cycle_model_config(Path(args.cycle_model_config))
    model_version = cfg["model_version"]

    signals = cycle_repository.list_cycle_signals(as_of=args.as_of, model_version=model_version, db_path=DB_PATH)

    print(
        f"run_industry_virtual_portfolio_plan signals={len(signals)} as_of={args.as_of} "
        f"model_version={model_version} execute={args.execute}"
    )
    for signal in signals:
        would_open = virtual_portfolio.should_open_position(signal)
        would_close = virtual_portfolio.should_close_position(signal)
        print(
            f"  target industry_id={signal['industry_id']} confirmed_state={signal.get('confirmed_state')} "
            f"confirmation_status={signal.get('confirmation_status')} would_open={would_open} would_close={would_close}"
        )

    if not args.execute:
        print("run_industry_virtual_portfolio_dry_run_only (pass --execute to actually update the ledger)")
        return

    results = virtual_portfolio.run_virtual_portfolio_batch(signals, real_as_of=args.as_of, db_path=DB_PATH)
    opened = sum(1 for r in results if r.get("action") == "opened")
    closed = sum(1 for r in results if r.get("action") == "closed")
    errored = sum(1 for r in results if r.get("action") == "error")
    for r in results:
        if r.get("action") == "error":
            print(f"result industry_id={r.get('industry_id')} action=error error={r.get('error')}")
        else:
            print(
                f"result industry_id={r.get('industry_id')} action={r.get('action')} "
                f"asset_id={r.get('asset_id')} exit_reason={r.get('exit_reason')}"
            )

    print(f"run_industry_virtual_portfolio_done opened={opened} closed={closed} errored={errored} total={len(signals)}")


if __name__ == "__main__":
    main()
