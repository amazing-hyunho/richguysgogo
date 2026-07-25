from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from committee.industry_cycle import factor_repository, price_factor_runner, price_model_config, price_repository, price_walkforward
from committee.industry_cycle.price_models import AssetPriceRecord
from committee.industry_cycle.price_state_machine import ACTION_RECOVERY_CONFIRMED

SAMPLE_UNIVERSE = {
    "benchmarks": [
        {"asset_id": "KOSPI", "market": "KR", "currency": "KRW", "provider": "yahoo_chart", "symbol": "^KS11"},
    ],
    "assets": [
        {
            "asset_id": "091160.KS",
            "market": "KR",
            "currency": "KRW",
            "provider": "yahoo_chart",
            "symbol": "091160.KS",
            "asset_type": "ETF",
            "industry_id": "semiconductors",
        },
    ],
}


def _seed_prices(db_path: Path, asset_id: str, market: str, currency: str, prices, *, start_date="2019-01-01") -> None:
    d0 = date.fromisoformat(start_date)
    for i, price in enumerate(prices):
        trade_date = (d0 + timedelta(days=i)).isoformat()
        price_repository.upsert_asset_price_daily(
            AssetPriceRecord(
                asset_id=asset_id,
                market=market,
                currency=currency,
                trade_date=trade_date,
                close_price=float(price),
                adj_close_price=float(price),
                adjustment_status="adjusted",
                available_at=f"{trade_date}T23:59:59+00:00",
            ),
            db_path=db_path,
        )


class WeeklyDatesTests(unittest.TestCase):
    def test_generates_every_friday_inclusive(self) -> None:
        dates = price_walkforward.generate_weekly_as_of_dates("2023-01-01", "2023-01-31")
        for d in dates:
            self.assertEqual(date.fromisoformat(d).weekday(), 4)
        self.assertEqual(dates, sorted(dates))
        self.assertGreaterEqual(len(dates), 4)

    def test_custom_weekday(self) -> None:
        dates = price_walkforward.generate_weekly_as_of_dates("2023-01-01", "2023-01-31", weekday=0)
        for d in dates:
            self.assertEqual(date.fromisoformat(d).weekday(), 0)

    def test_end_before_start_is_empty(self) -> None:
        self.assertEqual(price_walkforward.generate_weekly_as_of_dates("2023-02-01", "2023-01-01"), [])


class RunWalkforwardTests(unittest.TestCase):
    def test_persists_one_state_row_per_as_of_and_is_idempotent(self) -> None:
        targets = price_factor_runner.build_targets_from_universe(SAMPLE_UNIVERSE)
        model_config = price_model_config.load_price_model_config()
        with tempfile.TemporaryDirectory() as td:
            db_path = Path(td) / "investment.db"
            _seed_prices(db_path, "KOSPI", "KR", "KRW", [2500.0 + i * 0.3 for i in range(700)])
            _seed_prices(db_path, "091160.KS", "KR", "KRW", [10000.0 + i * 8 for i in range(700)])

            as_of_dates = price_walkforward.generate_weekly_as_of_dates("2020-08-01", "2020-11-01")
            self.assertGreater(len(as_of_dates), 5)

            tally = price_walkforward.run_walkforward(
                targets, as_of_dates=as_of_dates, model_config=model_config, db_path=db_path
            )
            self.assertEqual(set(tally.keys()), set(as_of_dates))
            self.assertTrue(all(v == 1 for v in tally.values()))

            state_rows = factor_repository.list_price_state_weekly("091160.KS", db_path=db_path)
            self.assertEqual(len(state_rows), len(as_of_dates))

            # Re-running the exact same historical window must not duplicate rows.
            price_walkforward.run_walkforward(
                targets, as_of_dates=as_of_dates, model_config=model_config, db_path=db_path
            )
            state_rows_after_rerun = factor_repository.list_price_state_weekly("091160.KS", db_path=db_path)
            self.assertEqual(len(state_rows_after_rerun), len(as_of_dates))

    def test_runs_in_ascending_order_regardless_of_input_order(self) -> None:
        """Confirmation streaks depend on chronological order; passing dates
        out of order must not change the persisted result."""
        targets = price_factor_runner.build_targets_from_universe(SAMPLE_UNIVERSE)
        model_config = price_model_config.load_price_model_config()
        as_of_dates = price_walkforward.generate_weekly_as_of_dates("2020-08-01", "2020-10-01")

        results_forward = {}
        with tempfile.TemporaryDirectory() as td:
            db_path = Path(td) / "investment.db"
            _seed_prices(db_path, "KOSPI", "KR", "KRW", [2500.0 + i * 0.3 for i in range(700)])
            _seed_prices(db_path, "091160.KS", "KR", "KRW", [10000.0 + i * 8 for i in range(700)])
            price_walkforward.run_walkforward(
                targets, as_of_dates=as_of_dates, model_config=model_config, db_path=db_path
            )
            for row in factor_repository.list_price_state_weekly("091160.KS", db_path=db_path):
                results_forward[row["as_of"]] = row["price_only_state"]

        results_shuffled = {}
        with tempfile.TemporaryDirectory() as td:
            db_path = Path(td) / "investment.db"
            _seed_prices(db_path, "KOSPI", "KR", "KRW", [2500.0 + i * 0.3 for i in range(700)])
            _seed_prices(db_path, "091160.KS", "KR", "KRW", [10000.0 + i * 8 for i in range(700)])
            price_walkforward.run_walkforward(
                targets, as_of_dates=list(reversed(as_of_dates)), model_config=model_config, db_path=db_path
            )
            for row in factor_repository.list_price_state_weekly("091160.KS", db_path=db_path):
                results_shuffled[row["as_of"]] = row["price_only_state"]

        self.assertEqual(results_forward, results_shuffled)


class EvaluateSignalEventsTests(unittest.TestCase):
    SIGNAL_INDEX = 300
    HORIZON_DAYS = 21

    def _seed_actionable_signal(self, db_path: Path, *, model_version: str):
        """Seeds one deterministic price series plus one hand-crafted
        actionable `industry_price_state_weekly` row (bypassing the state
        machine entirely) so forward-return arithmetic can be checked exactly.

        Every calendar day (no weekend gaps) becomes one series point, so
        list index == trading-day offset, matching `test_industry_price_backtest.py`'s
        own `_series` helper convention."""
        prices = [100.0] * 300 + [100.0 + i for i in range(1, 300)]
        _seed_prices(db_path, "TESTASSET", "KR", "KRW", prices, start_date="2019-01-01")
        _seed_prices(db_path, "KOSPI", "KR", "KRW", [2500.0] * 600, start_date="2019-01-01")

        signal_price = prices[self.SIGNAL_INDEX]
        forward_price = prices[self.SIGNAL_INDEX + self.HORIZON_DAYS]
        signal_trade_date = (date.fromisoformat("2019-01-01") + timedelta(days=self.SIGNAL_INDEX)).isoformat()
        factor_repository.upsert_industry_factor_weekly(
            {
                "industry_id": "semiconductors",
                "market": "KR",
                "asset_id": "TESTASSET",
                "benchmark_asset_id": "KOSPI",
                "as_of": signal_trade_date,
                "price_trade_date": signal_trade_date,
                "model_version": model_version,
                "data_cutoff_at": signal_trade_date,
            },
            db_path=db_path,
        )
        factor_repository.upsert_price_state_weekly(
            {
                "industry_id": "semiconductors",
                "market": "KR",
                "asset_id": "TESTASSET",
                "as_of": signal_trade_date,
                "model_version": model_version,
                "price_only_state": "PRICE_ONLY_RECOVERY_CANDIDATE",
                "action_signal": ACTION_RECOVERY_CONFIRMED,
            },
            db_path=db_path,
        )
        # A non-actionable row (no action_signal) in the same batch must be skipped.
        factor_repository.upsert_price_state_weekly(
            {
                "industry_id": "semiconductors",
                "market": "KR",
                "asset_id": "TESTASSET",
                "as_of": (date.fromisoformat(signal_trade_date) + timedelta(days=7)).isoformat(),
                "model_version": model_version,
                "price_only_state": "PRICE_ONLY_EXPANSION",
                "action_signal": None,
            },
            db_path=db_path,
        )
        return signal_trade_date, signal_price, forward_price

    def test_computes_and_persists_forward_returns_for_actionable_signal_only(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            db_path = Path(td) / "investment.db"
            model_version = "price_only_walkforward_test"
            signal_trade_date, signal_price, forward_price = self._seed_actionable_signal(
                db_path, model_version=model_version
            )

            events = price_walkforward.evaluate_signal_events(
                model_version, horizons={"1m": self.HORIZON_DAYS}, db_path=db_path
            )
            self.assertEqual(len(events), 1)
            event = events[0]
            self.assertEqual(event["signal_state"], "recovery_confirmed")
            self.assertEqual(event["signal_at"], signal_trade_date)
            self.assertAlmostEqual(event["asset_return"], forward_price / signal_price - 1.0)
            self.assertEqual(event["benchmark_return"], 0.0)  # flat KOSPI
            self.assertAlmostEqual(event["excess_return"], event["asset_return"])

            persisted = factor_repository.list_price_signal_performance("TESTASSET", db_path=db_path)
            self.assertEqual(len(persisted), 1)
            self.assertEqual(persisted[0]["horizon_label"], "1m")

    def test_rerunning_evaluate_is_idempotent(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            db_path = Path(td) / "investment.db"
            model_version = "price_only_walkforward_test"
            self._seed_actionable_signal(db_path, model_version=model_version)

            price_walkforward.evaluate_signal_events(model_version, horizons={"1m": self.HORIZON_DAYS}, db_path=db_path)
            price_walkforward.evaluate_signal_events(model_version, horizons={"1m": self.HORIZON_DAYS}, db_path=db_path)

            persisted = factor_repository.list_price_signal_performance("TESTASSET", db_path=db_path)
            self.assertEqual(len(persisted), 1)

    def test_missing_factor_row_is_skipped_not_raised(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            db_path = Path(td) / "investment.db"
            model_version = "price_only_walkforward_test"
            _seed_prices(db_path, "ORPHAN", "KR", "KRW", [100.0] * 300, start_date="2019-01-01")
            factor_repository.upsert_price_state_weekly(
                {
                    "industry_id": "semiconductors",
                    "market": "KR",
                    "asset_id": "ORPHAN",
                    "as_of": "2019-06-01",
                    "model_version": model_version,
                    "price_only_state": "PRICE_ONLY_RECOVERY_CANDIDATE",
                    "action_signal": ACTION_RECOVERY_CONFIRMED,
                },
                db_path=db_path,
            )
            # No matching industry_factor_weekly row exists for ORPHAN -- must not raise.
            events = price_walkforward.evaluate_signal_events(model_version, db_path=db_path)
            self.assertEqual(events, [])


class SummarizeByStateTests(unittest.TestCase):
    def test_groups_by_state_and_horizon(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            db_path = Path(td) / "investment.db"
            model_version = "price_only_walkforward_test"
            factor_repository.upsert_price_signal_performance(
                {
                    "industry_id": "semiconductors",
                    "market": "KR",
                    "asset_id": "A",
                    "signal_at": "2020-01-01",
                    "signal_state": "recovery_confirmed",
                    "model_version": model_version,
                    "horizon_label": "1m",
                    "excess_return": 0.05,
                },
                db_path=db_path,
            )
            factor_repository.upsert_price_signal_performance(
                {
                    "industry_id": "semiconductors",
                    "market": "KR",
                    "asset_id": "B",
                    "signal_at": "2020-02-01",
                    "signal_state": "recovery_confirmed",
                    "model_version": model_version,
                    "horizon_label": "1m",
                    "excess_return": -0.02,
                },
                db_path=db_path,
            )

            summary = price_walkforward.summarize_by_state(model_version, db_path=db_path)
            self.assertIn("recovery_confirmed", summary)
            self.assertEqual(summary["recovery_confirmed"]["1m"]["n"], 2)
            self.assertAlmostEqual(summary["recovery_confirmed"]["1m"]["avg_excess_return"], 0.015)


class ThresholdSensitivityTests(unittest.TestCase):
    def test_each_variant_persists_under_its_own_model_version_and_is_summarizable(self) -> None:
        targets = price_factor_runner.build_targets_from_universe(SAMPLE_UNIVERSE)
        base_model_config = price_model_config.load_price_model_config()
        as_of_dates = price_walkforward.generate_weekly_as_of_dates("2020-08-01", "2020-10-01")
        with tempfile.TemporaryDirectory() as td:
            db_path = Path(td) / "investment.db"
            _seed_prices(db_path, "KOSPI", "KR", "KRW", [2500.0 + i * 0.3 for i in range(700)])
            _seed_prices(db_path, "091160.KS", "KR", "KRW", [10000.0 + i * 8 for i in range(700)])

            variants = {
                "tighter_recovery": {"recovery_relative_strength_min": 80.0},
                "looser_recovery": {"recovery_relative_strength_min": 20.0},
            }
            results = price_walkforward.run_threshold_sensitivity(
                targets,
                as_of_dates=as_of_dates,
                base_model_config=base_model_config,
                variants=variants,
                db_path=db_path,
            )
            self.assertEqual(set(results.keys()), set(variants.keys()))

            tighter_version = f"{base_model_config['model_version']}__sensitivity_tighter_recovery"
            looser_version = f"{base_model_config['model_version']}__sensitivity_looser_recovery"
            self.assertGreater(len(factor_repository.list_factor_weekly("091160.KS", db_path=db_path)), 0)
            versions_seen = {
                r["model_version"] for r in factor_repository.list_factor_weekly("091160.KS", db_path=db_path)
            }
            self.assertIn(tighter_version, versions_seen)
            self.assertIn(looser_version, versions_seen)
            # Baseline model_version must remain untouched by the sensitivity run.
            self.assertNotIn(base_model_config["model_version"], versions_seen)

    def test_invalid_variant_override_raises_before_any_db_write(self) -> None:
        targets = price_factor_runner.build_targets_from_universe(SAMPLE_UNIVERSE)
        base_model_config = price_model_config.load_price_model_config()
        with tempfile.TemporaryDirectory() as td:
            db_path = Path(td) / "does_not_exist_yet" / "investment.db"
            with self.assertRaises(ValueError):
                price_walkforward.run_threshold_sensitivity(
                    targets,
                    as_of_dates=["2020-08-07"],
                    base_model_config=base_model_config,
                    variants={"bad": {"recovery_relative_strength_min": "not_a_number"}},
                    db_path=db_path,
                )
            self.assertFalse(db_path.exists())


if __name__ == "__main__":
    unittest.main()
