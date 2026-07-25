from __future__ import annotations

from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from committee.industry_cycle import (
    cycle_repository,
    monthly_report,
    repository as industry_repository,
    virtual_portfolio_repository,
)

MODEL_VERSION = "cycle_v1"


def _signal(**overrides):
    base = {
        "industry_id": "semiconductors", "as_of": "2026-07-10", "model_version": MODEL_VERSION,
        "data_cutoff_at": "2026-07-10", "cycle_score": 60.0, "raw_state": "CYCLE_RECOVERY_EARLY",
        "confirmed_state": "CYCLE_RECOVERY_EARLY", "confirmation_status": "confirmed",
        "previous_confirmed_state": None,
    }
    base.update(overrides)
    return base


class ComputeStateChangeEventsTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmpdir = tempfile.TemporaryDirectory()
        self.db_path = Path(self._tmpdir.name) / "test.db"

    def tearDown(self) -> None:
        self._tmpdir.cleanup()

    def test_newly_confirmed_event_detected_within_period(self) -> None:
        cycle_repository.upsert_industry_cycle_signal(_signal(), db_path=self.db_path)
        events = monthly_report.compute_state_change_events(
            MODEL_VERSION, period_start="2026-07-01", period_end="2026-07-31", db_path=self.db_path
        )
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["event"], "newly_confirmed")
        self.assertEqual(events[0]["state"], "CYCLE_RECOVERY_EARLY")

    def test_event_outside_period_excluded(self) -> None:
        cycle_repository.upsert_industry_cycle_signal(_signal(as_of="2026-06-15"), db_path=self.db_path)
        events = monthly_report.compute_state_change_events(
            MODEL_VERSION, period_start="2026-07-01", period_end="2026-07-31", db_path=self.db_path
        )
        self.assertEqual(events, [])

    def test_released_event_detected(self) -> None:
        cycle_repository.upsert_industry_cycle_signal(
            _signal(
                as_of="2026-07-20", confirmed_state=None, confirmation_status="held",
                previous_confirmed_state="CYCLE_RECOVERY_EARLY",
            ),
            db_path=self.db_path,
        )
        events = monthly_report.compute_state_change_events(
            MODEL_VERSION, period_start="2026-07-01", period_end="2026-07-31", db_path=self.db_path
        )
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["event"], "released")

    def test_unconfirmed_first_observation_is_not_an_event(self) -> None:
        cycle_repository.upsert_industry_cycle_signal(
            _signal(confirmation_status="first_observation", confirmed_state=None), db_path=self.db_path
        )
        events = monthly_report.compute_state_change_events(
            MODEL_VERSION, period_start="2026-07-01", period_end="2026-07-31", db_path=self.db_path
        )
        self.assertEqual(events, [])


class BuildMonthlyReportTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmpdir = tempfile.TemporaryDirectory()
        self.db_path = Path(self._tmpdir.name) / "test.db"

    def tearDown(self) -> None:
        self._tmpdir.cleanup()

    def test_empty_database_renders_clean_empty_report(self) -> None:
        report = monthly_report.build_monthly_report(
            MODEL_VERSION, period_start="2026-07-01", period_end="2026-07-31", db_path=self.db_path
        )
        self.assertEqual(report["state_change_events"], [])
        self.assertEqual(report["performance"]["positions"], [])
        self.assertIsNone(report["best_industry"])
        self.assertIsNone(report["worst_industry"])
        self.assertEqual(report["data_quality_events"], [])
        self.assertIn("모델 변경을 제안하지 않습니다", report["model_change_notes"])

    def test_state_change_events_include_industry_name(self) -> None:
        industry_repository.upsert_industry_master(
            industry_id="semiconductors", name_kr="반도체", db_path=self.db_path
        )
        cycle_repository.upsert_industry_cycle_signal(_signal(), db_path=self.db_path)
        report = monthly_report.build_monthly_report(
            MODEL_VERSION, period_start="2026-07-01", period_end="2026-07-31", db_path=self.db_path
        )
        self.assertEqual(len(report["state_change_events"]), 1)
        self.assertEqual(report["state_change_events"][0]["industry_name"], "반도체")

    def test_data_quality_events_filtered_to_period(self) -> None:
        industry_repository.record_data_quality_event(
            event_type="provider_timeout", target="semiconductors", severity="medium",
            message="fred timeout", detected_at="2026-07-15T00:00:00+00:00", db_path=self.db_path,
        )
        industry_repository.record_data_quality_event(
            event_type="provider_timeout", target="banks", severity="low",
            message="outside period", detected_at="2026-06-01T00:00:00+00:00", db_path=self.db_path,
        )
        report = monthly_report.build_monthly_report(
            MODEL_VERSION, period_start="2026-07-01", period_end="2026-07-31", db_path=self.db_path
        )
        self.assertEqual(len(report["data_quality_events"]), 1)
        self.assertEqual(report["data_quality_events"][0]["target"], "semiconductors")

    def test_best_and_worst_industry_from_ledger_with_elapsed_returns(self) -> None:
        from committee.industry_cycle import price_repository
        from committee.industry_cycle.price_models import AssetPriceRecord

        def price(asset_id, trade_date, close, market="US", currency="USD"):
            return AssetPriceRecord(
                asset_id=asset_id, market=market, currency=currency, trade_date=trade_date,
                close_price=close, adj_close_price=close, adjustment_status="adjusted",
                available_at=f"{trade_date}T23:59:59+00:00",
            )

        price_repository.bulk_upsert_asset_price_daily(
            [
                price("SOXX", "2026-01-01", 100.0), price("SP500", "2026-01-01", 5000.0),
                price("KBE", "2026-01-01", 50.0, market="US"), price("SP500", "2026-01-01", 5000.0),
                price("SOXX", "2026-02-05", 130.0), price("SP500", "2026-02-05", 5050.0),
                price("KBE", "2026-02-05", 45.0), price("SP500", "2026-02-05", 5050.0),
            ],
            db_path=self.db_path,
        )
        virtual_portfolio_repository.open_position(
            {
                "industry_id": "semiconductors", "model_version": MODEL_VERSION, "entry_as_of": "2026-01-01",
                "entry_trade_date": "2026-01-01", "asset_id": "SOXX", "asset_market": "US", "entry_price": 100.0,
                "benchmark_asset_id": "SP500", "benchmark_entry_price": 5000.0,
            },
            db_path=self.db_path,
        )
        virtual_portfolio_repository.open_position(
            {
                "industry_id": "banks", "model_version": MODEL_VERSION, "entry_as_of": "2026-01-01",
                "entry_trade_date": "2026-01-01", "asset_id": "KBE", "asset_market": "US", "entry_price": 50.0,
                "benchmark_asset_id": "SP500", "benchmark_entry_price": 5000.0,
            },
            db_path=self.db_path,
        )
        report = monthly_report.build_monthly_report(
            MODEL_VERSION, period_start="2026-02-01", period_end="2026-02-28", db_path=self.db_path
        )
        self.assertIsNotNone(report["best_industry"])
        self.assertIsNotNone(report["worst_industry"])
        self.assertEqual(report["best_industry"]["position"]["industry_id"], "semiconductors")
        self.assertEqual(report["worst_industry"]["position"]["industry_id"], "banks")
        self.assertGreater(len(report["worst_industry_top_reasons"]), -1)  # doesn't raise; may be empty


class RenderMonthlyReportHtmlTests(unittest.TestCase):
    def test_render_empty_report_produces_valid_html_with_all_sections(self) -> None:
        report = {
            "model_version": "cycle_v1", "period_start": "2026-07-01", "period_end": "2026-07-31",
            "state_change_events": [], "performance": {"positions": [], "open_count": 0, "closed_count": 0, "six_month_sample_size": 0, "hit_rate_6m": None},
            "best_industry": None, "worst_industry": None, "worst_industry_top_reasons": [],
            "data_quality_events": [], "model_change_notes": "표본 부족",
        }
        html_out = monthly_report.render_monthly_report_html(report)
        self.assertIn("<html", html_out)
        self.assertIn("2026-07-01", html_out)
        self.assertIn("2026-07-31", html_out)
        self.assertIn("표본 부족", html_out)
        self.assertIn("아직 판단할 데이터가 없습니다", html_out)


if __name__ == "__main__":
    unittest.main()
