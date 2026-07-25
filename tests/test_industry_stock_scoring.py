from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from committee.core.database import upsert_financial_metric, upsert_stock_consensus
from committee.industry_cycle import price_repository, stock_scoring
from committee.industry_cycle.stock_model_config import load_stock_model_config

_PRICE_FEATURE_CONFIG = {
    "return_windows_trading_days": {"1m": 21, "3m": 63, "6m": 126, "12m": 252},
    "moving_average_windows": [20, 60, 120, 200],
    "volatility_windows": [20, 60],
    "week_52_window_trading_days": 252,
    "volume_change_windows": {"recent": 20, "prior": 60},
}


def _trading_dates(n: int, end: date):
    out = []
    d = end
    while len(out) < n:
        if d.weekday() < 5:
            out.append(d)
        d -= timedelta(days=1)
    out.reverse()
    return out


class TempDbTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self._tmpdir = tempfile.TemporaryDirectory()
        self.db_path = Path(self._tmpdir.name) / "test.db"
        self.stock_model_config = load_stock_model_config()

    def tearDown(self) -> None:
        self._tmpdir.cleanup()

    def _seed_prices(self, asset_id: str, market: str, currency: str, *, n_days: int, start_price: float,
                      daily_drift: float, base_volume: float, end: date) -> None:
        dates = _trading_dates(n_days, end)
        records = []
        price = start_price
        for d in dates:
            price *= 1.0 + daily_drift
            records.append(
                {
                    "asset_id": asset_id,
                    "market": market,
                    "currency": currency,
                    "trade_date": d.isoformat(),
                    "close_price": price,
                    "adj_close_price": price,
                    "volume": base_volume,
                    "available_at": f"{d.isoformat()}T23:59:59+00:00",
                }
            )
        price_repository.bulk_upsert_asset_price_daily(records, db_path=self.db_path)


class ComputeStockScoreTests(TempDbTestCase):
    def test_full_data_produces_a_score(self) -> None:
        as_of = "2026-07-25"
        end = date(2026, 7, 24)
        self._seed_prices("GOODCO", "US", "USD", n_days=300, start_price=100.0, daily_drift=0.003,
                           base_volume=1_000_000, end=end)
        self._seed_prices("BENCH", "US", "USD", n_days=300, start_price=100.0, daily_drift=0.0002,
                           base_volume=5_000_000, end=end)

        upsert_financial_metric(
            {
                "ticker": "GOODCO", "business_year": "2024", "report_code": "2024-annual",
                "period_type": "annual", "revenue": 100.0, "operating_margin": 10.0, "roe": 8.0,
                "debt_ratio": 40.0, "net_margin": 5.0, "free_cashflow": 5.0, "total_equity": 200.0,
                "updated_at": "2025-01-01T00:00:00+00:00",
            },
            db_path=self.db_path,
        )
        upsert_financial_metric(
            {
                "ticker": "GOODCO", "business_year": "2025", "report_code": "2025-annual",
                "period_type": "annual", "revenue": 130.0, "operating_margin": 15.0, "roe": 12.0,
                "debt_ratio": 35.0, "net_margin": 8.0, "free_cashflow": 10.0, "total_equity": 220.0,
                "updated_at": "2026-01-01T00:00:00+00:00",
            },
            db_path=self.db_path,
        )
        upsert_stock_consensus(ticker="GOODCO", date="2026-05-27", target_mean_price=100.0,
                                recommendation_mean=2.0, num_analysts=10, db_path=self.db_path)
        upsert_stock_consensus(ticker="GOODCO", date="2026-07-25", target_mean_price=130.0,
                                recommendation_mean=1.5, num_analysts=12, db_path=self.db_path)

        bundle = stock_scoring.compute_stock_score(
            "GOODCO", "semiconductors", as_of,
            market="US", benchmark_asset_id="BENCH",
            stock_model_config=self.stock_model_config,
            price_feature_config=_PRICE_FEATURE_CONFIG,
            db_path=self.db_path,
        )
        self.assertIsNotNone(bundle.score)
        self.assertGreaterEqual(bundle.score, 0.0)
        self.assertLessEqual(bundle.score, 100.0)
        self.assertGreater(bundle.data_completeness, 0.9)
        self.assertFalse(bundle.exclusion.excluded)
        # A steadily-outperforming stock should score comfortably above neutral.
        self.assertGreater(bundle.score, 50.0)

    def test_no_price_data_still_scores_from_fundamentals_only(self) -> None:
        upsert_financial_metric(
            {
                "ticker": "NOPRICE", "business_year": "2025", "report_code": "2025-annual",
                "period_type": "annual", "revenue": 100.0, "operating_margin": 10.0, "roe": 8.0,
                "updated_at": "2026-01-01T00:00:00+00:00",
            },
            db_path=self.db_path,
        )
        upsert_stock_consensus(ticker="NOPRICE", date="2026-05-27", target_mean_price=100.0, db_path=self.db_path)
        upsert_stock_consensus(ticker="NOPRICE", date="2026-07-25", target_mean_price=110.0, db_path=self.db_path)

        bundle = stock_scoring.compute_stock_score(
            "NOPRICE", "semiconductors", "2026-07-25",
            market="US", benchmark_asset_id="BENCH",
            stock_model_config=self.stock_model_config,
            price_feature_config=_PRICE_FEATURE_CONFIG,
            db_path=self.db_path,
        )
        self.assertIsNone(bundle.sub_scores["relative_strength"].score)
        self.assertEqual(bundle.sub_scores["relative_strength"].reason, "no_price_data")
        self.assertIsNone(bundle.sub_scores["liquidity"].score)
        # earnings_quality/estimate_revision/financial_health can still combine into a score.
        self.assertIsNotNone(bundle.score)
        self.assertLess(bundle.data_completeness, 1.0)

    def test_no_data_at_all_gives_none_score(self) -> None:
        bundle = stock_scoring.compute_stock_score(
            "GHOST", "semiconductors", "2026-07-25",
            market="US", benchmark_asset_id="BENCH",
            stock_model_config=self.stock_model_config,
            price_feature_config=_PRICE_FEATURE_CONFIG,
            db_path=self.db_path,
        )
        self.assertIsNone(bundle.score)
        self.assertEqual(bundle.data_completeness, 0.0)

    def test_capital_impairment_flags_exclusion(self) -> None:
        upsert_financial_metric(
            {
                "ticker": "BADCO", "business_year": "2025", "report_code": "2025-annual",
                "period_type": "annual", "revenue": 100.0, "total_equity": -50.0,
                "updated_at": "2026-01-01T00:00:00+00:00",
            },
            db_path=self.db_path,
        )
        bundle = stock_scoring.compute_stock_score(
            "BADCO", "semiconductors", "2026-07-25",
            market="US", benchmark_asset_id="BENCH",
            stock_model_config=self.stock_model_config,
            price_feature_config=_PRICE_FEATURE_CONFIG,
            db_path=self.db_path,
        )
        self.assertTrue(bundle.exclusion.excluded)
        self.assertIn("capital_impairment", bundle.exclusion.reasons)

    def test_high_debt_ratio_incurs_risk_penalty(self) -> None:
        end = date(2026, 7, 24)
        self._seed_prices("LEVCO", "US", "USD", n_days=300, start_price=100.0, daily_drift=0.001,
                           base_volume=1_000_000, end=end)
        upsert_financial_metric(
            {
                "ticker": "LEVCO", "business_year": "2025", "report_code": "2025-annual",
                "period_type": "annual", "revenue": 100.0, "operating_margin": 10.0, "roe": 8.0,
                "debt_ratio": 400.0, "net_margin": 5.0,
                "updated_at": "2026-01-01T00:00:00+00:00",
            },
            db_path=self.db_path,
        )
        bundle = stock_scoring.compute_stock_score(
            "LEVCO", "semiconductors", "2026-07-25",
            market="US", benchmark_asset_id=None,
            stock_model_config=self.stock_model_config,
            price_feature_config=_PRICE_FEATURE_CONFIG,
            db_path=self.db_path,
        )
        self.assertGreater(bundle.risk_penalty_points, 0.0)
        self.assertAlmostEqual(bundle.score, max(0.0, bundle.pre_penalty_score - bundle.risk_penalty_points))

    def test_point_in_time_safety_future_financials_excluded(self) -> None:
        upsert_financial_metric(
            {
                "ticker": "FUTUREO", "business_year": "2026", "report_code": "2026-annual",
                "period_type": "annual", "revenue": 999.0, "roe": 99.0,
                "updated_at": "2099-01-01T00:00:00+00:00",
            },
            db_path=self.db_path,
        )
        bundle = stock_scoring.compute_stock_score(
            "FUTUREO", "semiconductors", "2026-07-25",
            market="US", benchmark_asset_id=None,
            stock_model_config=self.stock_model_config,
            price_feature_config=_PRICE_FEATURE_CONFIG,
            db_path=self.db_path,
        )
        self.assertIsNone(bundle.score)


if __name__ == "__main__":
    unittest.main()
