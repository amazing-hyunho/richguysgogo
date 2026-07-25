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
from committee.industry_cycle import candidate_ranking as cr
from committee.industry_cycle import candidate_repository, price_repository, repository
from committee.industry_cycle.stock_model_config import load_stock_model_config

_PRICE_FEATURE_CONFIG = {
    "return_windows_trading_days": {"1m": 21, "3m": 63, "6m": 126, "12m": 252},
    "moving_average_windows": [20, 60, 120, 200],
    "volatility_windows": [20, 60],
    "week_52_window_trading_days": 252,
    "volume_change_windows": {"recent": 20, "prior": 60},
}
_PRICE_UNIVERSE = {
    "benchmarks": [{"asset_id": "BENCH", "market": "US", "currency": "USD", "role": "benchmark",
                    "provider": "yahoo_chart", "symbol": "^X"}],
    "assets": [],
}
_ETF_QUALITY_CATALOG = {
    "etfs": [
        {"asset_id": "GOODETF", "aum_usd_equivalent": 1_000_000_000, "expense_ratio": 0.003,
         "is_leveraged_or_inverse": False, "industry_purity_pct": 1.0},
        {"asset_id": "SMALLETF", "aum_usd_equivalent": 1_000_000, "expense_ratio": 0.003,
         "is_leveraged_or_inverse": False, "industry_purity_pct": 1.0},
    ]
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


class CandidateRankingTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmpdir = tempfile.TemporaryDirectory()
        self.db_path = Path(self._tmpdir.name) / "test.db"
        self.stock_model_config = load_stock_model_config()
        self.as_of = "2026-07-25"
        self.end = date(2026, 7, 24)

        repository.upsert_industry_master(industry_id="semiconductors", name_kr="반도체", db_path=self.db_path)

        repository.upsert_industry_asset_map(
            asset_id="GOODETF", industry_id="semiconductors", asset_type="ETF", market="US",
            weight=1.0, valid_from="2026-01-01", db_path=self.db_path,
        )
        repository.upsert_industry_asset_map(
            asset_id="SMALLETF", industry_id="semiconductors", asset_type="ETF", market="US",
            weight=0.5, valid_from="2026-01-01", db_path=self.db_path,
        )
        repository.upsert_industry_asset_map(
            asset_id="GOODCO", industry_id="semiconductors", asset_type="STOCK", market="US",
            weight=0.6, valid_from="2026-01-01", db_path=self.db_path,
        )
        repository.upsert_industry_asset_map(
            asset_id="BADCO", industry_id="semiconductors", asset_type="STOCK", market="US",
            weight=0.4, valid_from="2026-01-01", db_path=self.db_path,
        )

        self._seed_prices("BENCH", daily_drift=0.0002, base_volume=5_000_000)
        self._seed_prices("GOODCO", daily_drift=0.003, base_volume=2_000_000)
        # BADCO gets no price history -> relative_strength/liquidity insufficient, and it's capital-impaired.

        upsert_financial_metric(
            {"ticker": "GOODCO", "business_year": "2024", "report_code": "2024-a", "period_type": "annual",
             "revenue": 100.0, "operating_margin": 10.0, "roe": 8.0, "total_equity": 200.0,
             "updated_at": "2025-01-01T00:00:00+00:00"},
            db_path=self.db_path,
        )
        upsert_financial_metric(
            {"ticker": "GOODCO", "business_year": "2025", "report_code": "2025-a", "period_type": "annual",
             "revenue": 140.0, "operating_margin": 15.0, "roe": 12.0, "total_equity": 220.0,
             "updated_at": "2026-01-01T00:00:00+00:00"},
            db_path=self.db_path,
        )
        upsert_stock_consensus(ticker="GOODCO", date="2026-05-27", target_mean_price=100.0, db_path=self.db_path)
        upsert_stock_consensus(ticker="GOODCO", date="2026-07-25", target_mean_price=130.0, db_path=self.db_path)

        upsert_financial_metric(
            {"ticker": "BADCO", "business_year": "2025", "report_code": "2025-a", "period_type": "annual",
             "revenue": 50.0, "total_equity": -20.0, "updated_at": "2026-01-01T00:00:00+00:00"},
            db_path=self.db_path,
        )

    def tearDown(self) -> None:
        self._tmpdir.cleanup()

    def _seed_prices(self, asset_id: str, *, daily_drift: float, base_volume: float) -> None:
        dates = _trading_dates(300, self.end)
        records = []
        price = 100.0
        for d in dates:
            price *= 1.0 + daily_drift
            records.append(
                {
                    "asset_id": asset_id, "market": "US", "currency": "USD",
                    "trade_date": d.isoformat(), "close_price": price, "adj_close_price": price,
                    "volume": base_volume, "available_at": f"{d.isoformat()}T23:59:59+00:00",
                }
            )
        price_repository.bulk_upsert_asset_price_daily(records, db_path=self.db_path)

    def _build(self):
        return cr.build_candidates_for_industry(
            "semiconductors", self.as_of,
            stock_model_config=self.stock_model_config,
            price_feature_config=_PRICE_FEATURE_CONFIG,
            etf_quality_catalog=_ETF_QUALITY_CATALOG,
            price_universe_payload=_PRICE_UNIVERSE,
            db_path=self.db_path,
        )

    def test_etf_candidates_split_pass_fail(self) -> None:
        result = self._build()
        by_id = {e["asset_id"]: e for e in result.etf_candidates}
        self.assertFalse(by_id["GOODETF"]["excluded"])
        self.assertEqual(by_id["GOODETF"]["rank"], 1)
        self.assertTrue(by_id["SMALLETF"]["excluded"])
        self.assertIsNone(by_id["SMALLETF"]["rank"])
        self.assertTrue(any("aum_below_minimum" in r for r in by_id["SMALLETF"]["exclusion_reasons"]))

    def test_stock_candidates_split_pass_fail(self) -> None:
        result = self._build()
        by_id = {s["asset_id"]: s for s in result.stock_candidates}
        self.assertFalse(by_id["GOODCO"]["excluded"])
        self.assertEqual(by_id["GOODCO"]["rank"], 1)
        self.assertIsNotNone(by_id["GOODCO"]["score"])
        self.assertTrue(by_id["BADCO"]["excluded"])
        self.assertIsNone(by_id["BADCO"]["rank"])
        self.assertIn("capital_impairment", by_id["BADCO"]["exclusion_reasons"])

    def test_industry_level_scores_present(self) -> None:
        result = self._build()
        self.assertIsNotNone(result.earnings_revision)
        self.assertIsNotNone(result.breadth)
        self.assertEqual(result.earnings_revision.n_tickers_considered, 2)

    def test_never_ranks_excluded_asset_even_when_few_candidates(self) -> None:
        """design doc 8.2: '추천 수를 채우기 위해 기준 미달 종목을 포함하지 않는다'."""
        result = self._build()
        for candidate in (*result.etf_candidates, *result.stock_candidates):
            if candidate["excluded"]:
                self.assertIsNone(candidate["rank"])

    def test_persist_writes_all_rows(self) -> None:
        result = self._build()
        n = cr.persist_candidate_ranking(
            result, model_version="stock_candidate_v1", data_cutoff_at="2026-07-25T00:00:00+00:00",
            db_path=self.db_path,
        )
        self.assertEqual(n, 4)  # 2 ETFs + 2 stocks
        rows = candidate_repository.list_industry_candidates(
            "semiconductors", self.as_of, "stock_candidate_v1", db_path=self.db_path
        )
        self.assertEqual(len(rows), 4)
        eb_row = candidate_repository.get_earnings_breadth_weekly(
            "semiconductors", self.as_of, "stock_candidate_v1", db_path=self.db_path
        )
        self.assertIsNotNone(eb_row)

    def test_persist_is_idempotent(self) -> None:
        result = self._build()
        cr.persist_candidate_ranking(
            result, model_version="v1", data_cutoff_at="2026-07-25T00:00:00+00:00", db_path=self.db_path
        )
        cr.persist_candidate_ranking(
            result, model_version="v1", data_cutoff_at="2026-07-25T00:00:00+00:00", db_path=self.db_path
        )
        rows = candidate_repository.list_industry_candidates("semiconductors", self.as_of, "v1", db_path=self.db_path)
        self.assertEqual(len(rows), 4)


if __name__ == "__main__":
    unittest.main()
