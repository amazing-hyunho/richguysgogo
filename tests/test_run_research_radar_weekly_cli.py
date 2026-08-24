from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "run_research_radar_weekly.py"


class RunResearchRadarWeeklyCliTests(unittest.TestCase):
    def test_default_mode_is_dry_run_without_writes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output_root = Path(tmp) / "runs"
            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--as-of",
                    "2026-08-11",
                    "--output-root",
                    str(output_root),
                ],
                cwd=str(ROOT),
                capture_output=True,
                text=True,
                timeout=30,
            )
            self.assertEqual(result.returncode, 0, msg=result.stderr)
            self.assertIn("research_radar_weekly_dry_run_only", result.stdout)
            self.assertIn("model=gpt-4.1", result.stdout)
            self.assertFalse(output_root.exists())

    def test_help_documents_execute_and_model_controls(self) -> None:
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--help"],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=30,
        )
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn("--execute", result.stdout)
        self.assertIn("--model", result.stdout)
        self.assertIn("--lookback-days", result.stdout)
        self.assertIn("--theme-id", result.stdout)

    def test_theme_filter_rejects_unknown_topic_before_execute(self) -> None:
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--theme-id", "not-a-topic"],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=30,
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn("unknown_theme_ids=not-a-topic", result.stderr)


if __name__ == "__main__":
    unittest.main()
