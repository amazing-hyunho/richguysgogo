from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from committee.industry_cycle import etf_quality as eq
from committee.industry_cycle import price_repository
from committee.industry_cycle.stock_model_config import load_stock_model_config


class ConfigTests(unittest.TestCase):
    def test_real_catalog_loads_and_validates(self) -> None:
        catalog = eq.load_etf_quality_catalog()
        self.assertIn("etfs", catalog)
        self.assertTrue(any(e["asset_id"] == "SOXX" for e in catalog["etfs"]))

    def test_duplicate_asset_id_is_rejected(self) -> None:
        payload = {"etfs": [{"asset_id": "AAA"}, {"asset_id": "AAA"}]}
        errors = eq.validate_etf_quality_catalog(payload)
        self.assertTrue(any("duplicate" in e for e in errors))

    def test_bad_numeric_field_is_rejected(self) -> None:
        payload = {"etfs": [{"asset_id": "AAA", "aum_usd_equivalent": "lots"}]}
        errors = eq.validate_etf_quality_catalog(payload)
        self.assertTrue(any("aum_usd_equivalent" in e for e in errors))


class EvaluateQualityTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = load_stock_model_config()

    def test_fully_passing_etf(self) -> None:
        inputs = eq.ETFQualityCheckInputs(
            asset_id="GOOD",
            aum_usd_equivalent=1_000_000_000,
            expense_ratio=0.002,
            bid_ask_spread_bp=5,
            is_leveraged_or_inverse=False,
            listing_days=2000,
            industry_purity_pct=0.9,
        )
        result = eq.evaluate_etf_quality(inputs, self.config)
        self.assertTrue(result.passed)
        self.assertEqual(result.reasons, [])
        self.assertEqual(result.unknown_checks, [])

    def test_low_aum_fails(self) -> None:
        inputs = eq.ETFQualityCheckInputs(asset_id="SMALL", aum_usd_equivalent=1_000_000)
        result = eq.evaluate_etf_quality(inputs, self.config)
        self.assertFalse(result.passed)
        self.assertTrue(any("aum_below_minimum" in r for r in result.reasons))

    def test_high_expense_ratio_fails(self) -> None:
        inputs = eq.ETFQualityCheckInputs(asset_id="EXPENSIVE", expense_ratio=0.02)
        result = eq.evaluate_etf_quality(inputs, self.config)
        self.assertFalse(result.passed)
        self.assertTrue(any("expense_ratio_above_maximum" in r for r in result.reasons))

    def test_leveraged_etf_fails(self) -> None:
        inputs = eq.ETFQualityCheckInputs(asset_id="LEV3X", is_leveraged_or_inverse=True)
        result = eq.evaluate_etf_quality(inputs, self.config)
        self.assertFalse(result.passed)
        self.assertIn("leveraged_or_inverse_etf_excluded", result.reasons)

    def test_insufficient_listing_history_fails(self) -> None:
        inputs = eq.ETFQualityCheckInputs(asset_id="NEWETF", listing_days=10)
        result = eq.evaluate_etf_quality(inputs, self.config)
        self.assertFalse(result.passed)
        self.assertTrue(any("insufficient_listing_history" in r for r in result.reasons))

    def test_low_industry_purity_fails(self) -> None:
        inputs = eq.ETFQualityCheckInputs(asset_id="BROAD", industry_purity_pct=0.1)
        result = eq.evaluate_etf_quality(inputs, self.config)
        self.assertFalse(result.passed)
        self.assertTrue(any("industry_purity_below_minimum" in r for r in result.reasons))

    def test_all_unknown_inputs_pass_with_unknown_checks_reported(self) -> None:
        inputs = eq.ETFQualityCheckInputs(asset_id="UNKNOWN")
        result = eq.evaluate_etf_quality(inputs, self.config)
        self.assertTrue(result.passed)
        self.assertGreater(len(result.unknown_checks), 0)


class ListingDaysTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmpdir = tempfile.TemporaryDirectory()
        self.db_path = Path(self._tmpdir.name) / "test.db"

    def tearDown(self) -> None:
        self._tmpdir.cleanup()

    def test_listing_days_counts_available_price_rows(self) -> None:
        end = date(2026, 7, 24)
        records = []
        d = end
        n = 0
        while n < 50:
            if d.weekday() < 5:
                records.append(
                    {
                        "asset_id": "ETF1", "market": "US", "currency": "USD",
                        "trade_date": d.isoformat(), "close_price": 100.0,
                        "available_at": f"{d.isoformat()}T23:59:59+00:00",
                    }
                )
                n += 1
            d -= timedelta(days=1)
        price_repository.bulk_upsert_asset_price_daily(records, db_path=self.db_path)
        listing_days = eq.compute_listing_days("ETF1", "2026-07-25", db_path=self.db_path)
        self.assertEqual(listing_days, 50)

    def test_no_price_data_gives_none(self) -> None:
        listing_days = eq.compute_listing_days("GHOST", "2026-07-25", db_path=self.db_path)
        self.assertIsNone(listing_days)


class EvaluateFromCatalogTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = load_stock_model_config()
        self._tmpdir = tempfile.TemporaryDirectory()
        self.db_path = Path(self._tmpdir.name) / "test.db"

    def tearDown(self) -> None:
        self._tmpdir.cleanup()

    def test_unknown_asset_not_in_catalog_fails(self) -> None:
        catalog = {"etfs": []}
        result = eq.evaluate_etf_from_catalog(
            "NOTFOUND", "2026-07-25", catalog=catalog, stock_model_config=self.config, db_path=self.db_path
        )
        self.assertFalse(result.passed)
        self.assertIn("etf_not_in_quality_catalog", result.reasons)

    def test_real_soxx_catalog_entry_evaluates(self) -> None:
        catalog = eq.load_etf_quality_catalog()
        result = eq.evaluate_etf_from_catalog(
            "SOXX", "2026-07-25", catalog=catalog, stock_model_config=self.config, db_path=self.db_path
        )
        # Real AUM ($47.8B) and expense ratio (0.34%) both comfortably pass; listing_days
        # is unknown in this temp DB (no price backfill here), so it's an unknown_check.
        self.assertNotIn("aum_below_minimum", " ".join(result.reasons))
        self.assertIn("listing_days_unknown", result.unknown_checks)


if __name__ == "__main__":
    unittest.main()
