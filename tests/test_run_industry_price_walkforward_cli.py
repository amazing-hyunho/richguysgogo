from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "run_industry_price_walkforward.py"
DB_PATH = ROOT / "data" / "investment.db"


class RunIndustryPriceWalkforwardCliDryRunTests(unittest.TestCase):
    """Exercises the real CLI entrypoint in dry-run mode only (no --execute),
    so this test can never write to the real `data/investment.db`."""

    def test_default_invocation_is_dry_run_and_has_no_side_effects(self) -> None:
        before_exists = DB_PATH.exists()
        before_mtime = DB_PATH.stat().st_mtime if before_exists else None

        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--start", "2023-01-01", "--end", "2023-03-01"],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=60,
        )

        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn("run_industry_price_walkforward_dry_run_only", result.stdout)
        self.assertIn("execute=False", result.stdout)

        after_exists = DB_PATH.exists()
        self.assertEqual(before_exists, after_exists)
        if before_mtime is not None:
            self.assertEqual(before_mtime, DB_PATH.stat().st_mtime)

    def test_empty_range_reports_no_weeks(self) -> None:
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--start", "2023-03-01", "--end", "2023-01-01"],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=60,
        )
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn("run_industry_price_walkforward_no_weeks_in_range", result.stdout)

    def test_execute_flag_present_in_help(self) -> None:
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--help"],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=30,
        )
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn("--execute", result.stdout)
        self.assertIn("--start", result.stdout)
        self.assertIn("--end", result.stdout)


if __name__ == "__main__":
    unittest.main()
