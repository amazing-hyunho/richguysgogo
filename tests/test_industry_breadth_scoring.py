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
from committee.industry_cycle import industry_breadth_scoring as ibs
from committee.industry_cycle import price_repository
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

    def _seed_prices(self, asset_id: str, *, n_days: int, start_price: float, daily_drift: float, end: date) -> None:
        dates = _trading_dates(n_days, end)
        records = []
        price = start_price
        for d in dates:
            price *= 1.0 + daily_drift
            records.append(
                {
                    "asset_id": asset_id, "market": "US", "currency": "USD",
                    "trade_date": d.isoformat(), "close_price": price, "adj_close_price": price,
                    "volume": 1_000_000, "available_at": f"{d.isoformat()}T23:59:59+00:00",
                }
            )
        price_repository.bulk_upsert_asset_price_daily(records, db_path=self.db_path)


class EarningsRevisionScoreTests(TempDbTestCase):
    def test_all_tickers_improving_gives_high_score(self) -> None:
        for t in ("A", "B", "C"):
            upsert_financial_metric(
                {"ticker": t, "business_year": "2024", "report_code": "2024-annual", "period_type": "annual",
                 "revenue": 100.0, "updated_at": "2025-01-01T00:00:00+00:00"},
                db_path=self.db_path,
            )
            upsert_financial_metric(
                {"ticker": t, "business_year": "2025", "report_code": "2025-annual", "period_type": "annual",
                 "revenue": 150.0, "updated_at": "2026-01-01T00:00:00+00:00"},
                db_path=self.db_path,
            )
            upsert_stock_consensus(ticker=t, date="2026-05-27", target_mean_price=100.0,
                                    recommendation_mean=2.0, db_path=self.db_path)
            upsert_stock_consensus(ticker=t, date="2026-07-25", target_mean_price=120.0,
                                    recommendation_mean=1.5, db_path=self.db_path)

        bundle = ibs.compute_industry_earnings_revision_score(
            "semiconductors", "2026-07-25", tickers=["A", "B", "C"],
            stock_model_config=self.stock_model_config, db_path=self.db_path,
        )
        self.assertIsNotNone(bundle.score)
        self.assertGreater(bundle.score, 50.0)
        self.assertEqual(len(bundle.evidence), 3)
        self.assertTrue(all(e.is_improving for e in bundle.evidence))

    def test_no_tickers_gives_insufficient_data(self) -> None:
        bundle = ibs.compute_industry_earnings_revision_score(
            "semiconductors", "2026-07-25", tickers=[],
            stock_model_config=self.stock_model_config, db_path=self.db_path,
        )
        self.assertIsNone(bundle.score)

    def test_partial_data_reduces_completeness_not_score_to_zero(self) -> None:
        upsert_financial_metric(
            {"ticker": "ONLYONE", "business_year": "2025", "report_code": "2025-annual", "period_type": "annual",
             "revenue": 100.0, "updated_at": "2026-01-01T00:00:00+00:00"},
            db_path=self.db_path,
        )
        bundle = ibs.compute_industry_earnings_revision_score(
            "semiconductors", "2026-07-25", tickers=["ONLYONE"],
            stock_model_config=self.stock_model_config, db_path=self.db_path,
        )
        self.assertEqual(bundle.data_completeness, 0.0)
        self.assertIsNone(bundle.score)


class BreadthScoreTests(TempDbTestCase):
    def test_factor_row_fast_path_matches_evidence_scoring(self) -> None:
        factor_rows = [
            {
                "asset_id": "UP",
                "rel_return_6m": 0.12,
                "score_breakdown_json": (
                    '{"trend":{"components":[{"key":"ma200_gap","raw_value":0.08}]}}'
                ),
            },
            {
                "asset_id": "DOWN",
                "rel_return_6m": -0.05,
                "score_breakdown_json": (
                    '{"trend":{"components":[{"key":"ma200_gap","raw_value":-0.03}]}}'
                ),
            },
        ]
        bundle = ibs.compute_industry_breadth_score_from_factor_rows(
            "semiconductors",
            "2026-07-25",
            factor_rows=factor_rows,
            stock_model_config=self.stock_model_config,
        )
        self.assertAlmostEqual(bundle.score, 50.0)
        self.assertEqual(bundle.data_completeness, 1.0)
        self.assertEqual(bundle.n_tickers_considered, 2)
        self.assertTrue(bundle.evidence[0].is_positive_relative_strength)
        self.assertFalse(bundle.evidence[1].is_above_200ma)

    def test_all_stocks_outperforming_gives_high_breadth(self) -> None:
        end = date(2026, 7, 24)
        for t in ("X", "Y", "Z"):
            self._seed_prices(t, n_days=300, start_price=100.0, daily_drift=0.003, end=end)
        self._seed_prices("BENCH", n_days=300, start_price=100.0, daily_drift=0.0002, end=end)

        bundle = ibs.compute_industry_breadth_score(
            "semiconductors", "2026-07-25",
            ticker_markets={"X": "US", "Y": "US", "Z": "US"},
            ticker_benchmarks={"X": "BENCH", "Y": "BENCH", "Z": "BENCH"},
            stock_model_config=self.stock_model_config,
            price_feature_config=_PRICE_FEATURE_CONFIG,
            db_path=self.db_path,
        )
        self.assertIsNotNone(bundle.score)
        self.assertGreater(bundle.score, 50.0)
        self.assertTrue(all(e.is_positive_relative_strength for e in bundle.evidence))
        self.assertTrue(all(e.is_above_200ma for e in bundle.evidence))

    def test_no_price_data_gives_none_score(self) -> None:
        bundle = ibs.compute_industry_breadth_score(
            "semiconductors", "2026-07-25",
            ticker_markets={"GHOST": "US"},
            ticker_benchmarks={"GHOST": None},
            stock_model_config=self.stock_model_config,
            price_feature_config=_PRICE_FEATURE_CONFIG,
            db_path=self.db_path,
        )
        self.assertIsNone(bundle.score)
        self.assertEqual(bundle.data_completeness, 0.0)

    def test_mixed_performance_gives_mid_range_score(self) -> None:
        end = date(2026, 7, 24)
        self._seed_prices("UP1", n_days=300, start_price=100.0, daily_drift=0.004, end=end)
        self._seed_prices("UP2", n_days=300, start_price=100.0, daily_drift=0.004, end=end)
        self._seed_prices("DOWN1", n_days=300, start_price=100.0, daily_drift=-0.003, end=end)
        self._seed_prices("DOWN2", n_days=300, start_price=100.0, daily_drift=-0.003, end=end)
        self._seed_prices("BENCH", n_days=300, start_price=100.0, daily_drift=0.0002, end=end)

        bundle = ibs.compute_industry_breadth_score(
            "semiconductors", "2026-07-25",
            ticker_markets={"UP1": "US", "UP2": "US", "DOWN1": "US", "DOWN2": "US"},
            ticker_benchmarks={"UP1": "BENCH", "UP2": "BENCH", "DOWN1": "BENCH", "DOWN2": "BENCH"},
            stock_model_config=self.stock_model_config,
            price_feature_config=_PRICE_FEATURE_CONFIG,
            db_path=self.db_path,
        )
        self.assertIsNotNone(bundle.score)
        self.assertTrue(30.0 < bundle.score < 70.0)


if __name__ == "__main__":
    unittest.main()
