from __future__ import annotations

"""Rebuild confirmation fields from persisted raw cycle states, in time order.

Scores and component reasons are left untouched.  This is the narrow repair
for the former expansion-state gap and is safe to re-run.
"""

import argparse
from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from committee.core.database import connect, init_db
from committee.industry_cycle import cycle_model_config, cycle_state_machine


DB_PATH = ROOT_DIR / "data" / "investment.db"


def main() -> None:
    parser = argparse.ArgumentParser(description="Repair historical industry-cycle confirmation fields.")
    parser.add_argument("--execute", action="store_true", help="Persist updates; otherwise report the plan.")
    args = parser.parse_args()
    config = cycle_model_config.load_cycle_model_config()
    model_version = config["model_version"]
    init_db(DB_PATH)
    with connect(DB_PATH) as conn:
        rows = conn.execute(
            """
            SELECT * FROM industry_cycle_signal
            WHERE model_version = :model_version
            ORDER BY industry_id, as_of;
            """,
            {"model_version": model_version},
        ).fetchall()

        updates: list[dict[str, object]] = []
        previous_by_industry: dict[str, dict[str, object]] = {}
        changed = 0
        for raw_row in rows:
            row = dict(raw_row)
            industry_id = str(row["industry_id"])
            previous = previous_by_industry.get(industry_id)
            transition = cycle_state_machine.apply_cycle_confirmation_rule(
                str(row["raw_state"]), previous, confirmation_cfg=config["confirmation"]
            )
            confirmed_state = (
                transition.raw_state
                if transition.confirmation_status in {
                    cycle_state_machine.STATUS_CONFIRMED,
                    cycle_state_machine.STATUS_WARNING,
                }
                else previous.get("confirmed_state") if previous else None
            )
            actionable = (
                transition.confirmation_status in {
                    cycle_state_machine.STATUS_CONFIRMED,
                    cycle_state_machine.STATUS_WARNING,
                }
                and float(row.get("confidence") or 0.0)
                >= float(config["confidence"]["min_confidence_for_action"])
            )
            update = {
                "id": row["id"],
                "confirmed_state": confirmed_state,
                "confirmation_status": transition.confirmation_status,
                "action_signal": transition.action_signal,
                "consecutive_weeks": transition.consecutive_weeks,
                "previous_confirmed_state": previous.get("confirmed_state") if previous else None,
                "is_actionable": 1 if actionable else 0,
            }
            if any(row.get(key) != value for key, value in update.items() if key != "id"):
                changed += 1
            updates.append(update)
            previous_by_industry[industry_id] = {**row, **update}

        print(
            f"repair_cycle_confirmation_history_plan model_version={model_version} "
            f"rows={len(rows)} changed={changed} execute={args.execute}"
        )
        if args.execute and updates:
            conn.executemany(
                """
                UPDATE industry_cycle_signal SET
                    confirmed_state=:confirmed_state,
                    confirmation_status=:confirmation_status,
                    action_signal=:action_signal,
                    consecutive_weeks=:consecutive_weeks,
                    previous_confirmed_state=:previous_confirmed_state,
                    is_actionable=:is_actionable
                WHERE id=:id;
                """,
                updates,
            )
            print(f"repair_cycle_confirmation_history_done updated={len(updates)} changed={changed}")


if __name__ == "__main__":
    main()
