from __future__ import annotations

from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "run_future_economy_weekly.py"


class RunFutureEconomyWeeklyCliTests(unittest.TestCase):
    def test_default_mode_is_dry_run_without_writes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output_root = Path(tmp) / "runs"
            db_path = Path(tmp) / "empty.db"
            result = subprocess.run(
                [sys.executable, str(SCRIPT), "--as-of", "2026-08-24", "--output-root", str(output_root)],
                cwd=str(ROOT),
                capture_output=True,
                text=True,
                timeout=30,
            )
            self.assertEqual(result.returncode, 0, msg=result.stderr)
            self.assertIn("future_economy_weekly_dry_run_only", result.stdout)
            self.assertIn("domains=8", result.stdout)
            self.assertIn("discovery_domains=2", result.stdout)
            self.assertFalse(output_root.exists())

    def test_execute_with_no_radar_reports_writes_valid_empty_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output_root = Path(tmp) / "runs"
            db_path = Path(tmp) / "empty.db"
            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--as-of",
                    "2026-08-24",
                    "--output-root",
                    str(output_root),
                    "--db-path",
                    str(db_path),
                    "--skip-live-policy",
                    "--skip-official-policy-api",
                    "--skip-dart-disclosures",
                    "--execute",
                ],
                cwd=str(ROOT),
                capture_output=True,
                text=True,
                timeout=30,
            )
            self.assertEqual(result.returncode, 0, msg=result.stderr)
            target = output_root / "2026-08-24" / "future_economy"
            self.assertTrue((target / "weekly_report.json").exists())
            self.assertTrue((target / "committee_agenda.json").exists())
            self.assertIn("research=0 agenda=0", result.stdout)


if __name__ == "__main__":
    unittest.main()
