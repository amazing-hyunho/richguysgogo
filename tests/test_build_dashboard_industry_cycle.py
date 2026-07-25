from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from committee.industry_cycle import (
    candidate_repository,
    cycle_repository,
    repository as industry_repository,
    virtual_portfolio_repository,
)

_SPEC = importlib.util.spec_from_file_location("build_dashboard", ROOT / "scripts" / "build_dashboard.py")
build_dashboard = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(build_dashboard)  # type: ignore[union-attr]


class LoadIndustryCycleDashboardDataTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmpdir = tempfile.TemporaryDirectory()
        self.db_path = Path(self._tmpdir.name) / "test.db"
        self._orig_db_path = build_dashboard.DB_PATH
        build_dashboard.DB_PATH = self.db_path

    def tearDown(self) -> None:
        build_dashboard.DB_PATH = self._orig_db_path
        self._tmpdir.cleanup()

    def test_empty_database_renders_clean_empty_state(self) -> None:
        data = build_dashboard.load_industry_cycle_dashboard_data()
        self.assertIsNotNone(data["model_version"])
        self.assertIsNone(data["as_of"])
        self.assertEqual(data["industries"], [])
        self.assertIsNotNone(data["virtual_portfolio"])
        self.assertEqual(data["virtual_portfolio"]["open_count"], 0)

    def test_industry_with_signal_appears_with_reasons_and_candidates(self) -> None:
        model_version = "cycle_v1"
        industry_repository.upsert_industry_master(
            industry_id="semiconductors", name_kr="반도체", name_en="Semiconductors",
            country_scope=["KR", "US"], db_path=self.db_path,
        )
        cycle_repository.upsert_industry_cycle_signal(
            {
                "industry_id": "semiconductors", "as_of": "2026-07-25", "model_version": model_version,
                "data_cutoff_at": "2026-07-25", "cycle_score": 65.0, "raw_state": "CYCLE_EXPANSION",
                "confirmed_state": "CYCLE_EXPANSION", "confirmation_status": "confirmed",
                "representative_asset_id": "SOXX", "representative_market": "US", "urgent_flags": [],
            },
            db_path=self.db_path,
        )
        cycle_repository.replace_industry_signal_reasons(
            "semiconductors", "2026-07-25", model_version,
            [{"component_key": "fundamentals_score", "raw_value": 70.0, "weight": 0.25, "contribution": 5.0, "direction": "positive"}],
            db_path=self.db_path,
        )
        from committee.industry_cycle import stock_model_config

        candidate_repository.upsert_industry_candidate(
            {
                "industry_id": "semiconductors", "as_of": "2026-07-25",
                "model_version": stock_model_config.load_stock_model_config()["model_version"],
                "data_cutoff_at": "2026-07-25", "asset_id": "SOXX", "asset_type": "ETF",
                "score": 80.0, "rank": 1, "excluded": False,
            },
            db_path=self.db_path,
        )

        data = build_dashboard.load_industry_cycle_dashboard_data()
        self.assertEqual(data["as_of"], "2026-07-25")
        self.assertEqual(len(data["industries"]), 1)
        item = data["industries"][0]
        self.assertEqual(item["industry_id"], "semiconductors")
        self.assertEqual(item["name_kr"], "반도체")
        self.assertEqual(item["latest_signal"]["cycle_score"], 65.0)
        self.assertEqual(len(item["top_reasons"]), 1)
        self.assertEqual(len(item["all_reasons"]), 1)
        self.assertEqual(item["top_reasons"][0]["component_key"], "fundamentals_score")
        self.assertEqual(len(item["history"]), 1)

    def test_industry_without_signal_is_shown_as_data_preparing(self) -> None:
        industry_repository.upsert_industry_master(industry_id="banks", name_kr="은행", db_path=self.db_path)
        data = build_dashboard.load_industry_cycle_dashboard_data()
        self.assertEqual(len(data["industries"]), 1)
        self.assertIsNone(data["industries"][0]["latest_signal"])
        self.assertEqual(data["industries"][0]["coverage"]["readiness"], "NEEDS_DATA")
        self.assertIn("대표 자산", data["industries"][0]["coverage"]["missing"])

    def test_virtual_portfolio_summary_reflects_open_position(self) -> None:
        virtual_portfolio_repository.open_position(
            {
                "industry_id": "semiconductors", "model_version": "cycle_v1", "entry_as_of": "2026-07-25",
                "entry_trade_date": "2026-07-24", "asset_id": "SOXX", "asset_market": "US", "entry_price": 100.0,
            },
            db_path=self.db_path,
        )
        data = build_dashboard.load_industry_cycle_dashboard_data()
        self.assertEqual(data["virtual_portfolio"]["open_count"], 1)


if __name__ == "__main__":
    unittest.main()
