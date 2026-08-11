from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from committee.research_radar.runner import analyze_file, write_report_artifacts

_SPEC = importlib.util.spec_from_file_location("build_dashboard", ROOT / "scripts" / "build_dashboard.py")
build_dashboard = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(build_dashboard)  # type: ignore[union-attr]

FIXTURE = ROOT / "config" / "research_radar_transformer.json"


class LoadResearchRadarDashboardDataTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmpdir = tempfile.TemporaryDirectory()
        self.runs_dir = Path(self._tmpdir.name) / "runs"
        self._original_runs_dir = build_dashboard.RUNS_DIR
        build_dashboard.RUNS_DIR = self.runs_dir

    def tearDown(self) -> None:
        build_dashboard.RUNS_DIR = self._original_runs_dir
        self._tmpdir.cleanup()

    def test_empty_runs_directory_returns_clean_empty_state(self) -> None:
        data = build_dashboard.load_research_radar_dashboard_data()
        self.assertIsNone(data["as_of"])
        self.assertEqual(data["theme_count"], 0)
        self.assertEqual(data["themes"], [])

    def test_latest_report_per_theme_is_loaded(self) -> None:
        old_report = analyze_file(FIXTURE, as_of_override="2018-12-31")
        new_report = analyze_file(FIXTURE)
        write_report_artifacts(old_report, output_root=self.runs_dir)
        write_report_artifacts(new_report, output_root=self.runs_dir)

        data = build_dashboard.load_research_radar_dashboard_data()
        self.assertEqual(data["as_of"], "2024-12-20")
        self.assertEqual(data["theme_count"], 1)
        self.assertEqual(len(data["themes"]), 1)
        self.assertEqual(data["themes"][0]["status"], "earnings_confirmed")

    def test_invalid_and_unrelated_json_are_ignored(self) -> None:
        target = self.runs_dir / "2024-01-01" / "research_radar"
        target.mkdir(parents=True)
        (target / "broken.json").write_text("{", encoding="utf-8")
        (target / "other.json").write_text('{"schema_version":"something-else"}', encoding="utf-8")
        self.assertEqual(build_dashboard.load_research_radar_dashboard_data()["themes"], [])

    def test_template_contains_research_radar_tab_and_renderer(self) -> None:
        template = build_dashboard.TEMPLATE_PATH.read_text(encoding="utf-8")
        self.assertIn('data-tab="research-radar"', template)
        self.assertIn('id="tab-research-radar"', template)
        self.assertIn("renderResearchRadarTab();", template)

    def test_embedded_json_cannot_close_inline_script(self) -> None:
        payload = {"research_radar": {"themes": [{"theme": {"name": "</script><script>alert(1)</script>"}}]}}
        html = build_dashboard.build_dashboard_html(payload)
        self.assertNotIn("</script><script>alert(1)</script>", html)
        self.assertIn("\\u003c/script>\\u003cscript>alert(1)\\u003c/script>", html)


if __name__ == "__main__":
    unittest.main()
