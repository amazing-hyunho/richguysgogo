from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "build_industry_monthly_report.py"
DB_PATH = ROOT / "data" / "investment.db"
OUTPUT_DIR = ROOT / "docs" / "industry_monthly_reports"


class BuildIndustryMonthlyReportCliDryRunTests(unittest.TestCase):
    """Exercises the real CLI entrypoint in dry-run mode only (no --execute),
    so this test can never write report files or touch the real DB."""

    def test_default_invocation_is_dry_run_and_writes_no_files(self) -> None:
        before_exists = DB_PATH.exists()
        before_mtime = DB_PATH.stat().st_mtime if before_exists else None
        before_report_files = sorted(OUTPUT_DIR.glob("*.html")) if OUTPUT_DIR.exists() else []

        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--period-start", "2026-07-01", "--period-end", "2026-07-31"],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=60,
        )

        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn("build_industry_monthly_report_dry_run_only", result.stdout)
        self.assertIn("execute=False", result.stdout)

        after_report_files = sorted(OUTPUT_DIR.glob("*.html")) if OUTPUT_DIR.exists() else []
        self.assertEqual(before_report_files, after_report_files)
        if before_mtime is not None:
            self.assertEqual(before_mtime, DB_PATH.stat().st_mtime)

    def test_execute_flag_present_in_help(self) -> None:
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--help"], cwd=str(ROOT), capture_output=True, text=True, timeout=30,
        )
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn("--execute", result.stdout)
        self.assertIn("--period-start", result.stdout)
        self.assertIn("--period-end", result.stdout)


if __name__ == "__main__":
    unittest.main()
