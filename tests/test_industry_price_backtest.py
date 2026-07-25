from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from committee.industry_cycle import price_backtest, price_features


def _series(prices, *, start_date="2020-01-01"):
    d0 = date.fromisoformat(start_date)
    rows = []
    for i, price in enumerate(prices):
        trade_date = (d0 + timedelta(days=i)).isoformat()
        rows.append({"trade_date": trade_date, "close_price": float(price), "adj_close_price": float(price)})
    return price_features.build_price_series(rows)


class ForwardReturnTests(unittest.TestCase):
    def test_forward_return_at_each_horizon(self) -> None:
        # 300 days: constant 100 up to day 100 (signal), then +1 per day afterward.
        prices = [100.0] * 101 + [100.0 + i for i in range(1, 200)]
        series = _series(prices)
        signal_at = series[100].trade_date
        results = price_backtest.compute_forward_returns(series, None, signal_at=signal_at, horizons={"1m": 21})
        self.assertEqual(len(results), 1)
        r = results[0]
        expected_price = 100.0 + 21
        self.assertAlmostEqual(r.asset_return, expected_price / 100.0 - 1.0)
        self.assertIsNone(r.benchmark_return)
        self.assertIsNone(r.excess_return)

    def test_horizon_beyond_available_history_is_none_not_fabricated(self) -> None:
        series = _series([100.0] * 30)
        signal_at = series[10].trade_date
        results = price_backtest.compute_forward_returns(series, None, signal_at=signal_at, horizons={"12m": 252})
        self.assertIsNone(results[0].asset_return)
        self.assertIsNone(results[0].forward_price)

    def test_unknown_signal_date_returns_empty_list(self) -> None:
        series = _series([100.0] * 30)
        results = price_backtest.compute_forward_returns(series, None, signal_at="1999-01-01", horizons={"1m": 21})
        self.assertEqual(results, [])

    def test_excess_return_uses_benchmark_own_offset_index(self) -> None:
        asset_prices = [100.0] * 30 + [110.0]  # +10% after 30 days
        benchmark_prices = [50.0] * 30 + [52.0]  # +4% after 30 days
        asset_series = _series(asset_prices, start_date="2020-01-01")
        benchmark_series = _series(benchmark_prices, start_date="2020-06-01")  # different calendar on purpose
        signal_at = asset_series[10].trade_date
        # Align signal indices manually since the two series use different calendars;
        # compute_forward_returns matches trade_date only within each own series (see docstring),
        # so we pass signal_at as-is for the asset and rely on positional offset for the benchmark.
        results = price_backtest.compute_forward_returns(
            asset_series, benchmark_series, signal_at=signal_at, horizons={"h": 20}
        )
        # Because signal_at only matches the asset's own series, and the benchmark's signal
        # index is found by matching the SAME trade_date string, this benchmark (different
        # calendar) will not find a matching index and excess_return is None -- documenting the
        # calendar-alignment limitation explicitly rather than silently producing a wrong number.
        self.assertIsNone(results[0].benchmark_return)
        self.assertIsNone(results[0].excess_return)

        # Using a shared calendar, the excess return is asset_return - benchmark_return.
        benchmark_series_shared = _series(benchmark_prices, start_date="2020-01-01")
        results_shared = price_backtest.compute_forward_returns(
            asset_series, benchmark_series_shared, signal_at=signal_at, horizons={"h": 20}
        )
        self.assertAlmostEqual(results_shared[0].asset_return, 0.10)
        self.assertAlmostEqual(results_shared[0].benchmark_return, 0.04)
        self.assertAlmostEqual(results_shared[0].excess_return, 0.06)


class MfeMaeTests(unittest.TestCase):
    def test_mfe_and_mae_over_window(self) -> None:
        # signal price 100 at idx 5; afterwards: up to 130 then down to 80.
        prices = [100.0] * 6 + [110.0, 120.0, 130.0, 110.0, 90.0, 80.0, 95.0]
        series = _series(prices)
        signal_at = series[5].trade_date
        result = price_backtest.compute_mfe_mae(series, signal_at=signal_at, max_horizon_trading_days=10)
        self.assertAlmostEqual(result["mfe"], 0.30)
        self.assertAlmostEqual(result["mae"], -0.20)

    def test_mfe_mae_none_when_no_post_signal_history(self) -> None:
        series = _series([100.0] * 5)
        signal_at = series[-1].trade_date
        result = price_backtest.compute_mfe_mae(series, signal_at=signal_at, max_horizon_trading_days=10)
        self.assertIsNone(result["mfe"])
        self.assertIsNone(result["mae"])

    def test_mfe_mae_none_when_signal_date_unknown(self) -> None:
        series = _series([100.0] * 30)
        result = price_backtest.compute_mfe_mae(series, signal_at="1999-01-01", max_horizon_trading_days=10)
        self.assertIsNone(result["mfe"])
        self.assertIsNone(result["mae"])


class SummarizePerformanceTests(unittest.TestCase):
    def test_win_rate_average_and_median(self) -> None:
        events = [
            {"horizon_label": "6m", "excess_return": 0.10},
            {"horizon_label": "6m", "excess_return": -0.05},
            {"horizon_label": "6m", "excess_return": 0.20},
            {"horizon_label": "6m", "excess_return": None},  # excluded, not counted as a loss
            {"horizon_label": "1m", "excess_return": 0.50},  # different horizon, excluded
        ]
        summary = price_backtest.summarize_performance(events, horizon_label="6m")
        self.assertEqual(summary["n"], 3)
        self.assertAlmostEqual(summary["win_rate"], 2 / 3)
        self.assertAlmostEqual(summary["avg_excess_return"], (0.10 - 0.05 + 0.20) / 3)
        self.assertAlmostEqual(summary["median_excess_return"], 0.10)

    def test_empty_events_yields_none_not_zero(self) -> None:
        summary = price_backtest.summarize_performance([], horizon_label="6m")
        self.assertIsNone(summary["win_rate"])
        self.assertIsNone(summary["avg_excess_return"])
        self.assertIsNone(summary["median_excess_return"])
        self.assertEqual(summary["n"], 0)


if __name__ == "__main__":
    unittest.main()
