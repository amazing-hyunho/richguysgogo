from __future__ import annotations

"""Phase 4 Telegram weekly digest + urgent alert CLI (dry-run by default).

Reads `industry_cycle_signal` rows already computed by
`run_industry_cycle_weekly.py --execute` for `--as-of` and either:
- prints the composed weekly digest + any urgent alert messages (default;
  no Telegram send, no dispatch-log writes), or
- actually sends them via `committee.adapters.telegram_sender.send_report`
  (console fallback if no `TELEGRAM_BOT_TOKEN`/`TELEGRAM_CHAT_ID` are set)
  and records each in `industry_alert_dispatch_log` so a re-run of this
  exact `(as_of, model_version)` never re-sends the same message, only
  when `--execute` is passed.

Run this AFTER `run_industry_cycle_weekly.py --execute` for the same
`--as-of` -- this CLI only READS `industry_cycle_signal`, it never computes
cycle scores itself.
"""

import argparse
from datetime import date
from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from committee.industry_cycle import cycle_model_config, stock_model_config, telegram_notifier

DB_PATH = ROOT_DIR / "data" / "investment.db"


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compose (and optionally send) this week's Telegram weekly digest + urgent alerts."
    )
    parser.add_argument("--as-of", default=date.today().isoformat(), help="Point-in-time cutoff date (YYYY-MM-DD).")
    parser.add_argument(
        "--cycle-model-config",
        default=str(cycle_model_config.CYCLE_MODEL_CONFIG_PATH),
        help="Path to industry_cycle_model.json.",
    )
    parser.add_argument(
        "--candidate-model-version",
        default=stock_model_config.load_stock_model_config()["model_version"],
        help="model_version to read ETF/stock candidates from (for the weekly digest's candidate summary).",
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Actually send via Telegram (or console fallback) and record dispatch-log rows. Without this flag, only prints what would be sent.",
    )
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    cfg = cycle_model_config.load_cycle_model_config(Path(args.cycle_model_config))
    model_version = cfg["model_version"]
    weeks_required_recovery = cfg["confirmation"]["weeks_required_recovery"]

    print(f"send_industry_cycle_alerts_plan as_of={args.as_of} model_version={model_version} execute={args.execute}")

    weekly_message = telegram_notifier.send_weekly_digest(
        args.as_of, model_version, weeks_required_recovery=weeks_required_recovery,
        candidate_model_version=args.candidate_model_version, db_path=DB_PATH, dry_run=not args.execute,
    )
    if weekly_message is None:
        print("weekly_digest: no_signals_for_this_week")
    else:
        print("weekly_digest:")
        print(weekly_message)

    urgent_messages = telegram_notifier.send_urgent_alerts(
        args.as_of, model_version, db_path=DB_PATH, dry_run=not args.execute
    )
    if not urgent_messages:
        print("urgent_alerts: none")
    else:
        for msg in urgent_messages:
            print("urgent_alert:")
            print(msg)

    if not args.execute:
        print("send_industry_cycle_alerts_dry_run_only (pass --execute to actually send)")
    else:
        print("send_industry_cycle_alerts_done")


if __name__ == "__main__":
    main()
