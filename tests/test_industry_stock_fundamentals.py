from __future__ import annotations

from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from committee.core.database import upsert_financial_metric, upsert_stock_consensus
from committee.industry_cycle import stock_fundamentals as sf


class TempDbTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self._tmpdir = tempfile.TemporaryDirectory()
        self.db_path = Path(self._tmpdir.name) / "test.db"

    def tearDown(self) -> None:
        self._tmpdir.cleanup()

    def _fm(self, ticker: str, business_year: str, period_type: str, updated_at: str, **kwargs) -> None:
        data = {
            "ticker": ticker,
            "business_year": business_year,
            "report_code": f"{business_year}-{period_type}",
            "period_type": period_type,
            "updated_at": updated_at,
        }
        data.update(kwargs)
        upsert_financial_metric(data, db_path=self.db_path)

    def _consensus(self, ticker: str, d: str, **kwargs) -> None:
        upsert_stock_consensus(ticker=ticker, date=d, db_path=self.db_path, **kwargs)


class PeriodKeyParsingTests(unittest.TestCase):
    def test_bare_year_parses_as_december(self) -> None:
        self.assertEqual(sf._parse_period_key("2025"), (2025, 12))

    def test_year_month_parses(self) -> None:
        self.assertEqual(sf._parse_period_key("2025-06"), (2025, 6))

    def test_garbage_returns_none(self) -> None:
        self.assertIsNone(sf._parse_period_key("not-a-period"))
        self.assertIsNone(sf._parse_period_key(None))


class EarningsQualityTests(TempDbTestCase):
    def test_single_annual_period_gives_roe_only(self) -> None:
        self._fm("TICK", "2025", "annual", "2026-01-01T00:00:00+00:00", revenue=100.0, operating_margin=10.0, roe=12.5)
        result = sf.compute_earnings_quality_inputs("TICK", "2026-07-25", db_path=self.db_path)
        self.assertIsNone(result.revenue_growth_yoy)
        self.assertIsNone(result.operating_margin_trend)
        self.assertAlmostEqual(result.roe, 0.125)

    def test_two_annual_periods_give_full_yoy(self) -> None:
        self._fm("TICK", "2024", "annual", "2025-01-01T00:00:00+00:00", revenue=100.0, operating_margin=10.0, roe=8.0)
        self._fm("TICK", "2025", "annual", "2026-01-01T00:00:00+00:00", revenue=120.0, operating_margin=15.0, roe=12.0)
        result = sf.compute_earnings_quality_inputs("TICK", "2026-07-25", db_path=self.db_path)
        self.assertAlmostEqual(result.revenue_growth_yoy, 0.20)
        self.assertAlmostEqual(result.operating_margin_trend, 0.05)
        self.assertAlmostEqual(result.roe, 0.12)
        self.assertTrue(result.yoy_aligned)

    def test_quarterly_exact_yoy_match_preferred(self) -> None:
        self._fm("TICK", "2025-06", "quarterly", "2025-07-01T00:00:00+00:00", revenue=100.0, operating_margin=10.0)
        self._fm("TICK", "2025-09", "quarterly", "2025-10-01T00:00:00+00:00", revenue=110.0, operating_margin=11.0)
        self._fm("TICK", "2025-12", "quarterly", "2026-01-01T00:00:00+00:00", revenue=120.0, operating_margin=12.0)
        self._fm("TICK", "2026-06", "quarterly", "2026-07-01T00:00:00+00:00", revenue=150.0, operating_margin=13.0)
        result = sf.compute_earnings_quality_inputs("TICK", "2026-07-25", db_path=self.db_path)
        self.assertAlmostEqual(result.revenue_growth_yoy, 0.5)
        self.assertTrue(result.yoy_aligned)
        self.assertEqual(result.current_period, "2026-06")
        self.assertEqual(result.prior_period, "2025-06")

    def test_point_in_time_gate_excludes_future_updated_rows(self) -> None:
        self._fm("TICK", "2024", "annual", "2025-01-01T00:00:00+00:00", revenue=100.0, roe=8.0)
        self._fm("TICK", "2025", "annual", "2027-01-01T00:00:00+00:00", revenue=200.0, roe=20.0)
        result = sf.compute_earnings_quality_inputs("TICK", "2026-07-25", db_path=self.db_path)
        # 2025 row's updated_at (2027) is after as_of, so only the 2024 row is visible.
        self.assertIsNone(result.revenue_growth_yoy)
        self.assertAlmostEqual(result.roe, 0.08)

    def test_no_data_gives_all_none(self) -> None:
        result = sf.compute_earnings_quality_inputs("UNKNOWN", "2026-07-25", db_path=self.db_path)
        self.assertIsNone(result.revenue_growth_yoy)
        self.assertIsNone(result.operating_margin_trend)
        self.assertIsNone(result.roe)


class FinancialHealthTests(TempDbTestCase):
    def test_levels_from_latest_period(self) -> None:
        self._fm(
            "TICK", "2025", "annual", "2026-01-01T00:00:00+00:00",
            debt_ratio=30.0, net_margin=12.0, free_cashflow=50.0, revenue=500.0, total_equity=1000.0,
        )
        result = sf.compute_financial_health_inputs("TICK", "2026-07-25", db_path=self.db_path)
        self.assertAlmostEqual(result.debt_ratio_inverse, -0.30)
        self.assertAlmostEqual(result.net_margin, 0.12)
        self.assertAlmostEqual(result.fcf_margin, 0.10)
        self.assertFalse(result.capital_impaired)

    def test_negative_equity_flags_capital_impairment(self) -> None:
        self._fm("TICK", "2025", "annual", "2026-01-01T00:00:00+00:00", total_equity=-10.0)
        result = sf.compute_financial_health_inputs("TICK", "2026-07-25", db_path=self.db_path)
        self.assertTrue(result.capital_impaired)

    def test_sustained_losses_counted_from_most_recent_backwards(self) -> None:
        self._fm("TICK", "2025-03", "quarterly", "2025-04-01T00:00:00+00:00", net_income=-5.0)
        self._fm("TICK", "2025-06", "quarterly", "2025-07-01T00:00:00+00:00", net_income=-3.0)
        self._fm("TICK", "2025-09", "quarterly", "2025-10-01T00:00:00+00:00", net_income=2.0)
        result = sf.compute_financial_health_inputs("TICK", "2026-07-25", db_path=self.db_path)
        # Most recent quarter (09) is profitable, so the loss streak is 0 (stops counting).
        self.assertEqual(result.sustained_loss_periods, 0)

    def test_sustained_losses_streak_from_latest(self) -> None:
        self._fm("TICK", "2025-03", "quarterly", "2025-04-01T00:00:00+00:00", net_income=2.0)
        self._fm("TICK", "2025-06", "quarterly", "2025-07-01T00:00:00+00:00", net_income=-3.0)
        self._fm("TICK", "2025-09", "quarterly", "2025-10-01T00:00:00+00:00", net_income=-4.0)
        result = sf.compute_financial_health_inputs("TICK", "2026-07-25", db_path=self.db_path)
        self.assertEqual(result.sustained_loss_periods, 2)

    def test_missing_data_gives_none(self) -> None:
        result = sf.compute_financial_health_inputs("UNKNOWN", "2026-07-25", db_path=self.db_path)
        self.assertIsNone(result.debt_ratio_inverse)
        self.assertIsNone(result.net_margin)
        self.assertIsNone(result.fcf_margin)
        self.assertIsNone(result.capital_impaired)
        self.assertEqual(result.sustained_loss_periods, 0)


class EstimateRevisionTests(TempDbTestCase):
    def test_target_price_and_recommendation_change(self) -> None:
        self._consensus("TICK", "2026-05-27", target_mean_price=100.0, recommendation_mean=2.0, num_analysts=10)
        self._consensus("TICK", "2026-07-25", target_mean_price=130.0, recommendation_mean=1.5, num_analysts=12)
        result = sf.compute_estimate_revision_inputs("TICK", "2026-07-25", lookback_days=60, db_path=self.db_path)
        self.assertAlmostEqual(result.target_price_change_pct, 0.30)
        self.assertAlmostEqual(result.recommendation_change, 0.5)  # improvement (mean went down)
        self.assertAlmostEqual(result.analyst_count_change_pct, 0.2)

    def test_single_snapshot_gives_none(self) -> None:
        self._consensus("TICK", "2026-07-25", target_mean_price=100.0)
        result = sf.compute_estimate_revision_inputs("TICK", "2026-07-25", lookback_days=60, db_path=self.db_path)
        self.assertIsNone(result.target_price_change_pct)
        self.assertEqual(result.n_snapshots, 1)

    def test_no_data_gives_none(self) -> None:
        result = sf.compute_estimate_revision_inputs("UNKNOWN", "2026-07-25", lookback_days=60, db_path=self.db_path)
        self.assertIsNone(result.target_price_change_pct)
        self.assertEqual(result.n_snapshots, 0)

    def test_future_snapshots_never_leak_into_past_as_of(self) -> None:
        self._consensus("TICK", "2026-05-01", target_mean_price=100.0)
        self._consensus("TICK", "2026-09-01", target_mean_price=999.0)
        result = sf.compute_estimate_revision_inputs("TICK", "2026-06-01", lookback_days=60, db_path=self.db_path)
        self.assertEqual(result.n_snapshots, 1)
        self.assertIsNone(result.target_price_change_pct)

    def test_short_history_falls_back_to_oldest_snapshot(self) -> None:
        self._consensus("TICK", "2026-07-20", target_mean_price=100.0)
        self._consensus("TICK", "2026-07-25", target_mean_price=110.0)
        result = sf.compute_estimate_revision_inputs("TICK", "2026-07-25", lookback_days=60, db_path=self.db_path)
        self.assertAlmostEqual(result.target_price_change_pct, 0.10)
        self.assertEqual(result.lookback_snapshot_date, "2026-07-20")


if __name__ == "__main__":
    unittest.main()
