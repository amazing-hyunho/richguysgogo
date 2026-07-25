from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "run_industry_price_threshold_sensitivity.py"
DB_PATH = ROOT / "data" / "investment.db"


class RunIndustryPriceThresholdSensitivityCliDryRunTests(unittest.TestCase):
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
        self.assertIn("run_industry_price_threshold_sensitivity_dry_run_only", result.stdout)
        self.assertIn("execute=False", result.stdout)
        self.assertIn("tighter_recovery_rs", result.stdout)

        after_exists = DB_PATH.exists()
        self.assertEqual(before_exists, after_exists)
        if before_mtime is not None:
            self.assertEqual(before_mtime, DB_PATH.stat().st_mtime)

    def test_custom_variants_file_is_used(self) -> None:
        import json
        import tempfile

        with tempfile.TemporaryDirectory() as td:
            variants_path = Path(td) / "variants.json"
            variants_path.write_text(json.dumps({"my_variant": {"overheat_score_min": 80.0}}), encoding="utf-8")
            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--start",
                    "2023-01-01",
                    "--end",
                    "2023-03-01",
                    "--variants-file",
                    str(variants_path),
                ],
                cwd=str(ROOT),
                capture_output=True,
                text=True,
                timeout=60,
            )
            self.assertEqual(result.returncode, 0, msg=result.stderr)
            self.assertIn("my_variant", result.stdout)
            self.assertNotIn("tighter_recovery_rs", result.stdout)

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
        self.assertIn("--variants-file", result.stdout)


if __name__ == "__main__":
    unittest.main()
