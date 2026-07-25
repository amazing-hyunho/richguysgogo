from __future__ import annotations

import math
from datetime import date, timedelta
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from committee.industry_cycle import price_features, price_model_config, price_repository
from committee.industry_cycle.price_models import AssetPriceRecord


def _rows(prices, *, start_date="2020-01-01", volumes=None, use_adj=True):
    """Build plain asset_price_daily-shaped rows, one per calendar day starting `start_date`."""
    d0 = date.fromisoformat(start_date)
    rows = []
    for i, price in enumerate(prices):
        trade_date = (d0 + timedelta(days=i)).isoformat()
        row = {
            "trade_date": trade_date,
            "close_price": float(price),
            "adj_close_price": float(price) if use_adj else None,
            "volume": None if volumes is None else float(volumes[i]),
        }
        rows.append(row)
    return rows


class BuildPriceSeriesTests(unittest.TestCase):
    def test_prefers_adjusted_close(self) -> None:
        rows = [{"trade_date": "2020-01-01", "close_price": 100.0, "adj_close_price": 90.0}]
        series = price_features.build_price_series(rows)
        self.assertEqual(series[0].price, 90.0)
        self.assertEqual(series[0].field_used, "adjusted")

    def test_falls_back_to_raw_close_when_adjusted_missing(self) -> None:
        rows = [{"trade_date": "2020-01-01", "close_price": 100.0, "adj_close_price": None}]
        series = price_features.build_price_series(rows)
        self.assertEqual(series[0].price, 100.0)
        self.assertEqual(series[0].field_used, "raw_close_fallback")

    def test_row_with_no_usable_price_is_skipped(self) -> None:
        rows = [
            {"trade_date": "2020-01-01", "close_price": None, "adj_close_price": None},
            {"trade_date": "2020-01-02", "close_price": 101.0, "adj_close_price": None},
        ]
        series = price_features.build_price_series(rows)
        self.assertEqual(len(series), 1)
        self.assertEqual(series[0].trade_date, "2020-01-02")

    def test_summarize_price_field_used(self) -> None:
        all_adjusted = price_features.build_price_series(_rows([100, 101], use_adj=True))
        self.assertEqual(price_features.summarize_price_field_used(all_adjusted), "adjusted")

        mixed = price_features.build_price_series(
            [
                {"trade_date": "2020-01-01", "close_price": 100.0, "adj_close_price": 100.0},
                {"trade_date": "2020-01-02", "close_price": 101.0, "adj_close_price": None},
            ]
        )
        self.assertEqual(price_features.summarize_price_field_used(mixed), "raw_close_fallback")
        self.assertIsNone(price_features.summarize_price_field_used([]))


class ReturnsAndRelativeReturnsTests(unittest.TestCase):
    def test_return_over_window_exact_value(self) -> None:
        prices = [100.0] * 20 + [110.0]  # 21 points; 20-day-ago price is 100.0
        series = price_features.build_price_series(_rows(prices))
        ret = price_features._return_over_window(series, 20)
        self.assertAlmostEqual(ret, 0.10)

    def test_return_none_when_series_too_short(self) -> None:
        series = price_features.build_price_series(_rows([100.0] * 5))
        self.assertIsNone(price_features._return_over_window(series, 20))

    def test_compute_returns_multiple_windows(self) -> None:
        prices = [100.0] * 63 + [126.0]
        series = price_features.build_price_series(_rows(prices))
        windows = {"1m": 21, "3m": 63}
        out = price_features.compute_returns(series, windows)
        self.assertAlmostEqual(out["3m"], 0.26)
        # price 21 days before the last point is also 100.0 (still in the flat run) -> +26% too
        self.assertAlmostEqual(out["1m"], 0.26)

    def test_relative_return_is_asset_minus_benchmark(self) -> None:
        asset_returns = {"3m": 0.10, "6m": None, "12m": 0.20}
        benchmark_returns = {"3m": 0.04, "6m": 0.05, "12m": 0.15}
        rel = price_features.compute_relative_returns(asset_returns, benchmark_returns, labels=("3m", "6m", "12m"))
        self.assertAlmostEqual(rel["rel_return_3m"], 0.06)
        self.assertIsNone(rel["rel_return_6m"])  # asset leg missing -> None, never 0
        self.assertAlmostEqual(rel["rel_return_12m"], 0.05)


class MovingAverageAndVolatilityTests(unittest.TestCase):
    def test_moving_average_exact_value(self) -> None:
        series = price_features.build_price_series(_rows([10.0, 20.0, 30.0, 40.0]))
        self.assertAlmostEqual(price_features.moving_average(series, 4), 25.0)
        self.assertAlmostEqual(price_features.moving_average(series, 2), 35.0)

    def test_moving_average_none_when_too_short(self) -> None:
        series = price_features.build_price_series(_rows([10.0, 20.0]))
        self.assertIsNone(price_features.moving_average(series, 5))

    def test_volatility_matches_manual_population_stdev(self) -> None:
        # Daily returns: +10%, -10%/1.1, ... use a simple case: prices with a fixed pct swing.
        prices = [100.0, 110.0, 100.0, 110.0, 100.0]
        series = price_features.build_price_series(_rows(prices))
        rets = price_features.daily_returns(series)
        mean = sum(rets) / len(rets)
        expected = math.sqrt(sum((r - mean) ** 2 for r in rets) / len(rets))
        self.assertAlmostEqual(price_features.volatility(series, 4), expected)

    def test_volatility_none_when_too_short(self) -> None:
        series = price_features.build_price_series(_rows([100.0, 101.0]))
        self.assertIsNone(price_features.volatility(series, 20))

    def test_drawdown_from_high_exact_value(self) -> None:
        prices = [100.0, 120.0, 90.0]
        series = price_features.build_price_series(_rows(prices))
        dd = price_features.drawdown_from_high(series, 3)
        self.assertAlmostEqual(dd, 90.0 / 120.0 - 1.0)

    def test_drawdown_none_when_too_short(self) -> None:
        series = price_features.build_price_series(_rows([100.0, 101.0]))
        self.assertIsNone(price_features.drawdown_from_high(series, 10))


class VolumeChangeTests(unittest.TestCase):
    def test_volume_change_exact_value(self) -> None:
        prior = [1000.0] * 60
        recent = [2000.0] * 20
        rows = _rows([100.0] * 80, volumes=prior + recent)
        series = price_features.build_price_series(rows)
        change = price_features.compute_volume_change(series, recent_window=20, prior_window=60)
        self.assertAlmostEqual(change, 1.0)  # doubled

    def test_volume_change_none_when_insufficient_history(self) -> None:
        rows = _rows([100.0] * 10, volumes=[1000.0] * 10)
        series = price_features.build_price_series(rows)
        self.assertIsNone(price_features.compute_volume_change(series, recent_window=20, prior_window=60))

    def test_volume_change_none_when_volume_entirely_missing(self) -> None:
        rows = _rows([100.0] * 80, volumes=None)
        series = price_features.build_price_series(rows)
        self.assertIsNone(price_features.compute_volume_change(series, recent_window=20, prior_window=60))


class BelowMaRatioTests(unittest.TestCase):
    def test_below_ma_ratio_zero_is_distinct_from_none(self) -> None:
        # price above every available MA -> ratio 0.0 (a real number, not "missing")
        ratio = price_features.compute_below_ma_ratio(110.0, {20: 100.0, 60: 105.0})
        self.assertEqual(ratio, 0.0)
        self.assertIsNotNone(ratio)

    def test_below_ma_ratio_none_when_no_mas_available(self) -> None:
        self.assertIsNone(price_features.compute_below_ma_ratio(110.0, {20: None, 60: None}))

    def test_below_ma_ratio_none_when_price_missing(self) -> None:
        self.assertIsNone(price_features.compute_below_ma_ratio(None, {20: 100.0}))


class BuildWeeklyFeaturesTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = price_model_config.load_price_model_config()

    def test_insufficient_history_yields_none_features_and_low_completeness(self) -> None:
        asset_rows = _rows([100.0] * 5)
        features = price_features.build_weekly_features(
            asset_rows, [], asset_id="X", market="US", benchmark_asset_id=None, as_of="2020-01-06", config=self.config
        )
        self.assertIsNone(features.return_12m)
        self.assertIsNone(features.ma200)
        self.assertLess(features.data_completeness, 0.5)

    def test_empty_asset_series_yields_all_none(self) -> None:
        features = price_features.build_weekly_features(
            [], [], asset_id="X", market="US", benchmark_asset_id=None, as_of="2020-01-01", config=self.config
        )
        self.assertIsNone(features.current_price)
        self.assertEqual(features.n_observations, 0)
        self.assertEqual(features.data_completeness, 0.0)

    def test_full_history_produces_all_features(self) -> None:
        asset_rows = _rows([100.0 + i * 0.1 for i in range(400)], volumes=[1000.0 + (i % 7) for i in range(400)])
        benchmark_rows = _rows([100.0 + i * 0.05 for i in range(400)])
        features = price_features.build_weekly_features(
            asset_rows,
            benchmark_rows,
            asset_id="X",
            market="US",
            benchmark_asset_id="SP500",
            as_of="2021-02-01",
            config=self.config,
        )
        self.assertIsNotNone(features.return_12m)
        self.assertIsNotNone(features.rel_return_12m)
        self.assertIsNotNone(features.ma200)
        self.assertIsNotNone(features.vol_60d)
        self.assertEqual(features.data_completeness, 1.0)
        self.assertEqual(features.price_field_used, "adjusted")


class NoLookaheadIntegrationTests(unittest.TestCase):
    """Confirms feature computation only ever sees data gated by get_prices_as_of."""

    def test_future_rows_never_affect_a_past_as_of_computation(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            db_path = Path(td) / "investment.db"
            d0 = date.fromisoformat("2019-01-01")
            for i in range(300):
                trade_date = (d0 + timedelta(days=i)).isoformat()
                price_repository.upsert_asset_price_daily(
                    AssetPriceRecord(
                        asset_id="SOXX",
                        market="US",
                        currency="USD",
                        trade_date=trade_date,
                        close_price=100.0 + i,
                        adj_close_price=100.0 + i,
                        adjustment_status="adjusted",
                        available_at=f"{trade_date}T23:59:59+00:00",
                    ),
                    db_path=db_path,
                )
            as_of = (d0 + timedelta(days=250)).isoformat()
            rows_before = price_repository.get_prices_as_of("SOXX", as_of, db_path=db_path)
            config = price_model_config.load_price_model_config()
            features_before = price_features.build_weekly_features(
                rows_before, [], asset_id="SOXX", market="US", benchmark_asset_id=None, as_of=as_of, config=config
            )

            # Backfill 3 more months of "future" (relative to as_of) prices.
            for i in range(300, 390):
                trade_date = (d0 + timedelta(days=i)).isoformat()
                price_repository.upsert_asset_price_daily(
                    AssetPriceRecord(
                        asset_id="SOXX",
                        market="US",
                        currency="USD",
                        trade_date=trade_date,
                        close_price=100.0 + i,
                        adj_close_price=100.0 + i,
                        adjustment_status="adjusted",
                        available_at=f"{trade_date}T23:59:59+00:00",
                    ),
                    db_path=db_path,
                )

            rows_after = price_repository.get_prices_as_of("SOXX", as_of, db_path=db_path)
            features_after = price_features.build_weekly_features(
                rows_after, [], asset_id="SOXX", market="US", benchmark_asset_id=None, as_of=as_of, config=config
            )

            self.assertEqual(features_before.to_dict(), features_after.to_dict())
            self.assertEqual(features_after.n_observations, 251)  # days 0..250 inclusive


if __name__ == "__main__":
    unittest.main()
