from __future__ import annotations

from datetime import date
import importlib.util
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "backfill_industry_cycle_history.py"

SPEC = importlib.util.spec_from_file_location("backfill_industry_cycle_history", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class WeeklyDateTests(unittest.TestCase):
    def test_generates_exactly_54_fridays(self) -> None:
        dates = MODULE.generate_recent_weekly_dates("2026-07-24", 54)
        self.assertEqual(len(dates), 54)
        self.assertEqual(dates[0], "2025-07-18")
        self.assertEqual(dates[-1], "2026-07-24")
        self.assertTrue(all(date.fromisoformat(item).weekday() == 4 for item in dates))

    def test_aligns_end_date_back_to_selected_weekday(self) -> None:
        self.assertEqual(
            MODULE.generate_recent_weekly_dates("2026-07-30", 2),
            ["2026-07-17", "2026-07-24"],
        )

    def test_invalid_arguments_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            MODULE.generate_recent_weekly_dates("2026-07-24", 0)
        with self.assertRaises(ValueError):
            MODULE.generate_recent_weekly_dates("2026-07-24", 1, weekday=7)


class BackfillIndustryCycleHistoryCliTests(unittest.TestCase):
    def test_dry_run_reports_54_week_plan_without_writing(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--weeks",
                "54",
                "--end-date",
                "2026-07-24",
            ],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=60,
        )
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn("weeks=54 range=2025-07-18..2026-07-24", result.stdout)
        self.assertIn("execute=False", result.stdout)
        self.assertIn("backfill_industry_cycle_history_dry_run_only", result.stdout)
        self.assertIn("news:excluded", result.stdout)


if __name__ == "__main__":
    unittest.main()
