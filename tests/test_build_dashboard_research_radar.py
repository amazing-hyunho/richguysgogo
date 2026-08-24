from __future__ import annotations

import importlib.util
import json
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
        future = build_dashboard.load_future_economy_dashboard_data()
        self.assertEqual(future["source_mode"], "research_radar_fallback")
        self.assertEqual(future["paper_signals"]["theme_count"], 1)

    def test_latest_future_economy_report_and_agenda_are_loaded(self) -> None:
        target = self.runs_dir / "2026-08-24" / "future_economy"
        target.mkdir(parents=True)
        (target / "weekly_report.json").write_text(
            json.dumps({
                "schema_version": "future-economy-weekly-report-v1",
                "as_of": "2026-08-24",
                "summary": {"active": 1, "new": 1},
                "research_tasks": [{"research_id": "future-ai", "status": "initial_watch"}],
                "methodology": {"committee_review_min_types": 3},
            }),
            encoding="utf-8",
        )
        (target / "committee_agenda.json").write_text(
            json.dumps({
                "schema_version": "future-economy-committee-agenda-v1",
                "as_of": "2026-08-24",
                "item_count": 0,
                "items": [],
            }),
            encoding="utf-8",
        )
        data = build_dashboard.load_future_economy_dashboard_data()
        self.assertEqual(data["source_mode"], "future_economy_weekly")
        self.assertEqual(data["as_of"], "2026-08-24")
        self.assertEqual(data["research_tasks"][0]["research_id"], "future-ai")
        self.assertEqual(data["committee_agenda"]["item_count"], 0)

    def test_invalid_and_unrelated_json_are_ignored(self) -> None:
        target = self.runs_dir / "2024-01-01" / "research_radar"
        target.mkdir(parents=True)
        (target / "broken.json").write_text("{", encoding="utf-8")
        (target / "other.json").write_text('{"schema_version":"something-else"}', encoding="utf-8")
        self.assertEqual(build_dashboard.load_research_radar_dashboard_data()["themes"], [])

    def test_research_radar_is_merged_into_future_economy_tab(self) -> None:
        template = build_dashboard.TEMPLATE_PATH.read_text(encoding="utf-8")
        self.assertIn('data-tab="future-economy"', template)
        self.assertIn('id="tab-future-economy"', template)
        self.assertNotIn('data-tab="research-radar"', template)
        self.assertNotIn('id="tab-research-radar"', template)
        self.assertIn("renderFutureEconomyTab();", template)
        self.assertIn("AI 투자위원회 검토 안건", template)
        self.assertIn("신규 논문·기술 신호", template)
        self.assertIn("과거 사례 비교", template)
        self.assertIn("약화·종료된 연구", template)
        self.assertIn("['greed-pot', 'research-radar']", template)

    def test_embedded_json_cannot_close_inline_script(self) -> None:
        payload = {"research_radar": {"themes": [{"theme": {"name": "</script><script>alert(1)</script>"}}]}}
        html = build_dashboard.build_dashboard_html(payload)
        self.assertNotIn("</script><script>alert(1)</script>", html)
        self.assertIn("\\u003c/script>\\u003cscript>alert(1)\\u003c/script>", html)


if __name__ == "__main__":
    unittest.main()
