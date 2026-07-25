from __future__ import annotations

from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from committee.industry_cycle import (
    price_repository,
    virtual_portfolio,
    virtual_portfolio_repository as vp_repo,
)
from committee.industry_cycle.price_models import AssetPriceRecord


def _price(asset_id: str, trade_date: str, close: float, market: str = "US", currency: str = "USD") -> AssetPriceRecord:
    return AssetPriceRecord(
        asset_id=asset_id, market=market, currency=currency, trade_date=trade_date,
        close_price=close, adj_close_price=close, adjustment_status="adjusted",
        available_at=f"{trade_date}T23:59:59+00:00",
    )


def _signal(**overrides):
    base = {
        "industry_id": "semiconductors",
        "as_of": "2026-07-25",
        "model_version": "cycle_v1",
        "confirmation_status": "confirmed",
        "confirmed_state": "CYCLE_RECOVERY_EARLY",
        "previous_confirmed_state": None,
        "representative_asset_id": "SOXX",
        "representative_market": "US",
        "urgent_flags": [],
    }
    base.update(overrides)
    return base


class ShouldOpenCloseTests(unittest.TestCase):
    def test_should_open_on_newly_confirmed_recovery(self) -> None:
        self.assertTrue(virtual_portfolio.should_open_position(_signal()))

    def test_should_not_reopen_when_already_confirmed_previously(self) -> None:
        s = _signal(previous_confirmed_state="CYCLE_RECOVERY_EARLY")
        self.assertFalse(virtual_portfolio.should_open_position(s))

    def test_should_not_open_without_representative_asset(self) -> None:
        s = _signal(representative_asset_id=None)
        self.assertFalse(virtual_portfolio.should_open_position(s))

    def test_should_not_open_when_not_confirmed(self) -> None:
        s = _signal(confirmation_status="first_observation")
        self.assertFalse(virtual_portfolio.should_open_position(s))

    def test_should_close_on_confirmed_deterioration(self) -> None:
        s = _signal(confirmed_state="CYCLE_RECESSION")
        reason = virtual_portfolio.should_close_position(s)
        self.assertIsNotNone(reason)
        self.assertIn("CYCLE_RECESSION", reason)

    def test_should_close_on_urgent_flag_regardless_of_state(self) -> None:
        s = _signal(confirmed_state="CYCLE_EXPANSION", urgent_flags=["PRICE_CRASH"])
        reason = virtual_portfolio.should_close_position(s)
        self.assertEqual(reason, "urgent_flag:PRICE_CRASH")

    def test_should_not_close_when_expansion_and_no_flags(self) -> None:
        s = _signal(confirmed_state="CYCLE_EXPANSION")
        self.assertIsNone(virtual_portfolio.should_close_position(s))


class UpdatePortfolioForSignalTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmpdir = tempfile.TemporaryDirectory()
        self.db_path = Path(self._tmpdir.name) / "test.db"
        price_repository.bulk_upsert_asset_price_daily(
            [
                _price("SOXX", "2026-07-24", 100.0),
                _price("SP500", "2026-07-24", 5000.0),
                _price("KOSPI", "2026-07-24", 2500.0, market="KR", currency="KRW"),
            ],
            db_path=self.db_path,
        )

    def tearDown(self) -> None:
        self._tmpdir.cleanup()

    def test_opens_new_position_with_entry_price(self) -> None:
        outcome = virtual_portfolio.update_virtual_portfolio_for_signal(
            _signal(), real_as_of="2026-07-25", db_path=self.db_path
        )
        self.assertIsNotNone(outcome)
        self.assertEqual(outcome["action"], "opened")
        self.assertEqual(outcome["entry_price"], 100.0)
        row = vp_repo.get_open_position("semiconductors", "cycle_v1", db_path=self.db_path)
        self.assertIsNotNone(row)
        self.assertEqual(row["benchmark_asset_id"], "SP500")
        self.assertEqual(row["benchmark_entry_price"], 5000.0)

    def test_no_open_when_price_missing_for_asset(self) -> None:
        outcome = virtual_portfolio.update_virtual_portfolio_for_signal(
            _signal(representative_asset_id="UNKNOWN_TICKER"), real_as_of="2026-07-25", db_path=self.db_path
        )
        self.assertIsNone(outcome)
        self.assertIsNone(vp_repo.get_open_position("semiconductors", "cycle_v1", db_path=self.db_path))

    def test_no_action_when_signal_neither_opens_nor_closes(self) -> None:
        outcome = virtual_portfolio.update_virtual_portfolio_for_signal(
            _signal(confirmation_status="first_observation", confirmed_state=None),
            real_as_of="2026-07-25", db_path=self.db_path,
        )
        self.assertIsNone(outcome)

    def test_closes_open_position_on_deterioration(self) -> None:
        virtual_portfolio.update_virtual_portfolio_for_signal(_signal(), real_as_of="2026-07-25", db_path=self.db_path)
        price_repository.bulk_upsert_asset_price_daily(
            [_price("SOXX", "2026-08-07", 80.0), _price("SP500", "2026-08-07", 5100.0)], db_path=self.db_path,
        )
        outcome = virtual_portfolio.update_virtual_portfolio_for_signal(
            _signal(as_of="2026-08-08", confirmed_state="CYCLE_SLOWING", previous_confirmed_state="CYCLE_RECOVERY_EARLY"),
            real_as_of="2026-08-08", db_path=self.db_path,
        )
        self.assertIsNotNone(outcome)
        self.assertEqual(outcome["action"], "closed")
        row = vp_repo.get_position(outcome["id"], db_path=self.db_path)
        self.assertEqual(row["status"], "CLOSED")
        self.assertEqual(row["exit_price"], 80.0)
        self.assertIsNone(vp_repo.get_open_position("semiconductors", "cycle_v1", db_path=self.db_path))

    def test_does_not_open_second_position_while_one_is_open(self) -> None:
        virtual_portfolio.update_virtual_portfolio_for_signal(_signal(), real_as_of="2026-07-25", db_path=self.db_path)
        outcome = virtual_portfolio.update_virtual_portfolio_for_signal(
            _signal(as_of="2026-08-01"), real_as_of="2026-08-01", db_path=self.db_path
        )
        self.assertIsNone(outcome)
        self.assertEqual(len(vp_repo.list_positions(db_path=self.db_path)), 1)


class RunBatchTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmpdir = tempfile.TemporaryDirectory()
        self.db_path = Path(self._tmpdir.name) / "test.db"
        price_repository.bulk_upsert_asset_price_daily(
            [_price("SOXX", "2026-07-24", 100.0), _price("SP500", "2026-07-24", 5000.0)], db_path=self.db_path,
        )

    def tearDown(self) -> None:
        self._tmpdir.cleanup()

    def test_batch_isolates_per_industry_errors(self) -> None:
        good = _signal(industry_id="semiconductors")
        bad = {"industry_id": "banks"}  # missing required keys -> should raise internally, isolated
        results = virtual_portfolio.run_virtual_portfolio_batch(
            [good, bad], real_as_of="2026-07-25", db_path=self.db_path
        )
        actions = {r.get("industry_id"): r.get("action") for r in results}
        self.assertEqual(actions.get("semiconductors"), "opened")
        self.assertEqual(actions.get("banks"), "error")


class ForwardPerformanceTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmpdir = tempfile.TemporaryDirectory()
        self.db_path = Path(self._tmpdir.name) / "test.db"

    def tearDown(self) -> None:
        self._tmpdir.cleanup()

    def _closed_position(self):
        return {
            "asset_id": "SOXX",
            "entry_as_of": "2026-01-01",
            "entry_trade_date": "2026-01-01",
            "entry_price": 100.0,
            "benchmark_asset_id": "SP500",
            "benchmark_entry_price": 5000.0,
            "status": "CLOSED",
        }

    def test_future_horizon_relative_to_today_is_insufficient_data(self) -> None:
        perf = virtual_portfolio.compute_forward_performance(
            self._closed_position(), today="2026-01-15", db_path=self.db_path
        )
        for months in virtual_portfolio.FORWARD_RETURN_MONTHS:
            self.assertIsNone(perf[f"return_{months}m"])
            self.assertIsNone(perf[f"excess_return_{months}m"])

    def test_elapsed_horizon_with_price_data_computes_return(self) -> None:
        price_repository.bulk_upsert_asset_price_daily(
            [_price("SOXX", "2026-02-01", 110.0), _price("SP500", "2026-02-01", 5050.0)], db_path=self.db_path,
        )
        perf = virtual_portfolio.compute_forward_performance(
            self._closed_position(), today="2026-02-15", db_path=self.db_path
        )
        self.assertAlmostEqual(perf["return_1m"], 0.10, places=6)
        expected_excess = 0.10 - (5050.0 / 5000.0 - 1.0)
        self.assertAlmostEqual(perf["excess_return_1m"], expected_excess, places=6)
        self.assertIsNone(perf["return_3m"])  # 2026-04-01 hasn't happened yet relative to today

    def test_elapsed_horizon_without_price_data_is_insufficient_data(self) -> None:
        perf = virtual_portfolio.compute_forward_performance(
            self._closed_position(), today="2026-02-15", db_path=self.db_path
        )
        self.assertIsNone(perf["return_1m"])  # target date passed but no price was ever backfilled


class SummarizePortfolioPerformanceTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmpdir = tempfile.TemporaryDirectory()
        self.db_path = Path(self._tmpdir.name) / "test.db"

    def tearDown(self) -> None:
        self._tmpdir.cleanup()

    def test_empty_ledger_returns_zero_counts_not_error(self) -> None:
        summary = virtual_portfolio.summarize_portfolio_performance(
            "cycle_v1", today="2026-07-25", db_path=self.db_path
        )
        self.assertEqual(summary["open_count"], 0)
        self.assertEqual(summary["closed_count"], 0)
        self.assertEqual(summary["positions"], [])
        self.assertIsNone(summary["hit_rate_6m"])

    def test_summary_includes_open_and_closed_positions(self) -> None:
        vp_repo.open_position(
            {
                "industry_id": "semiconductors", "model_version": "cycle_v1", "entry_as_of": "2026-07-25",
                "entry_trade_date": "2026-07-24", "asset_id": "SOXX", "asset_market": "US", "entry_price": 100.0,
            },
            db_path=self.db_path,
        )
        summary = virtual_portfolio.summarize_portfolio_performance(
            "cycle_v1", today="2026-07-25", db_path=self.db_path
        )
        self.assertEqual(summary["open_count"], 1)
        self.assertEqual(len(summary["positions"]), 1)


if __name__ == "__main__":
    unittest.main()
