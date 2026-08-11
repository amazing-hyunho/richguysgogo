from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "run_research_radar.py"
FIXTURE = ROOT / "config" / "research_radar_transformer.json"


class RunResearchRadarCliTests(unittest.TestCase):
    def test_default_mode_is_dry_run_and_writes_nothing(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            output_root = Path(td) / "out"
            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--input",
                    str(FIXTURE),
                    "--output-root",
                    str(output_root),
                ],
                cwd=str(ROOT),
                capture_output=True,
                text=True,
                timeout=30,
            )
            self.assertEqual(result.returncode, 0, msg=result.stderr)
            self.assertIn("run_research_radar_dry_run_only", result.stdout)
            self.assertIn("execute=False", result.stdout)
            self.assertFalse(output_root.exists())

    def test_execute_writes_deterministic_json_and_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            output_root = Path(td) / "out"
            command = [
                sys.executable,
                str(SCRIPT),
                "--input",
                str(FIXTURE),
                "--output-root",
                str(output_root),
                "--execute",
            ]
            first = subprocess.run(command, cwd=str(ROOT), capture_output=True, text=True, timeout=30)
            self.assertEqual(first.returncode, 0, msg=first.stderr)
            output_dir = output_root / "2024-12-20" / "research_radar"
            json_path = output_dir / "transformer-foundation-models.json"
            markdown_path = output_dir / "transformer-foundation-models.md"
            self.assertTrue(json_path.exists())
            self.assertTrue(markdown_path.exists())
            first_json = json_path.read_bytes()
            first_markdown = markdown_path.read_bytes()

            second = subprocess.run(command, cwd=str(ROOT), capture_output=True, text=True, timeout=30)
            self.assertEqual(second.returncode, 0, msg=second.stderr)
            self.assertEqual(first_json, json_path.read_bytes())
            self.assertEqual(first_markdown, markdown_path.read_bytes())

    def test_help_documents_point_in_time_and_execute_flags(self) -> None:
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--help"],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=30,
        )
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn("--as-of", result.stdout)
        self.assertIn("--execute", result.stdout)
        self.assertIn("--output-root", result.stdout)


if __name__ == "__main__":
    unittest.main()
