from __future__ import annotations

from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from committee.industry_cycle import price_universe


class LoadRealConfigTests(unittest.TestCase):
    """Guards against accidental breakage of the checked-in config file."""

    def test_config_file_loads_and_validates(self) -> None:
        payload = price_universe.load_price_universe()
        self.assertIn("benchmarks", payload)
        self.assertIn("assets", payload)
        self.assertGreaterEqual(len(payload["benchmarks"]), 2)
        self.assertGreaterEqual(len(payload["assets"]), 1)

    def test_list_asset_ids_includes_benchmarks_and_assets(self) -> None:
        ids = price_universe.list_asset_ids()
        self.assertIn("KOSPI", ids)
        self.assertIn("SP500", ids)
        self.assertIn("SOXX", ids)


class ValidatePriceUniverseTests(unittest.TestCase):
    def test_valid_payload_has_no_errors(self) -> None:
        payload = {
            "benchmarks": [
                {"asset_id": "KOSPI", "market": "KR", "currency": "KRW", "provider": "yahoo_chart", "symbol": "^KS11"}
            ],
            "assets": [
                {
                    "asset_id": "SOXX",
                    "market": "US",
                    "currency": "USD",
                    "provider": "yahoo_chart",
                    "symbol": "SOXX",
                    "industry_id": "semiconductors",
                }
            ],
        }
        self.assertEqual(price_universe.validate_price_universe(payload), [])

    def test_rejects_unsupported_market(self) -> None:
        payload = {
            "benchmarks": [],
            "assets": [
                {
                    "asset_id": "X",
                    "market": "JP",
                    "currency": "USD",
                    "provider": "yahoo_chart",
                    "symbol": "X",
                    "industry_id": "semiconductors",
                }
            ],
        }
        errors = price_universe.validate_price_universe(payload)
        self.assertTrue(any("market" in e for e in errors))

    def test_rejects_unsupported_currency(self) -> None:
        payload = {
            "benchmarks": [],
            "assets": [
                {
                    "asset_id": "X",
                    "market": "US",
                    "currency": "JPY",
                    "provider": "yahoo_chart",
                    "symbol": "X",
                    "industry_id": "semiconductors",
                }
            ],
        }
        errors = price_universe.validate_price_universe(payload)
        self.assertTrue(any("currency" in e for e in errors))

    def test_asset_entry_without_industry_id_is_rejected(self) -> None:
        payload = {
            "benchmarks": [],
            "assets": [
                {"asset_id": "X", "market": "US", "currency": "USD", "provider": "yahoo_chart", "symbol": "X"}
            ],
        }
        errors = price_universe.validate_price_universe(payload)
        self.assertTrue(any("industry_id" in e for e in errors))

    def test_benchmark_entry_without_industry_id_is_allowed(self) -> None:
        payload = {
            "benchmarks": [
                {"asset_id": "KOSPI", "market": "KR", "currency": "KRW", "provider": "yahoo_chart", "symbol": "^KS11"}
            ],
            "assets": [],
        }
        self.assertEqual(price_universe.validate_price_universe(payload), [])

    def test_duplicate_asset_id_across_benchmarks_and_assets_is_rejected(self) -> None:
        payload = {
            "benchmarks": [
                {"asset_id": "SOXX", "market": "US", "currency": "USD", "provider": "yahoo_chart", "symbol": "SOXX"}
            ],
            "assets": [
                {
                    "asset_id": "SOXX",
                    "market": "US",
                    "currency": "USD",
                    "provider": "yahoo_chart",
                    "symbol": "SOXX",
                    "industry_id": "semiconductors",
                }
            ],
        }
        errors = price_universe.validate_price_universe(payload)
        self.assertTrue(any("duplicate asset_id" in e for e in errors))

    def test_missing_provider_or_symbol_is_rejected(self) -> None:
        payload = {
            "benchmarks": [{"asset_id": "KOSPI", "market": "KR", "currency": "KRW"}],
            "assets": [],
        }
        errors = price_universe.validate_price_universe(payload)
        self.assertTrue(any("provider" in e for e in errors))
        self.assertTrue(any("symbol" in e for e in errors))


if __name__ == "__main__":
    unittest.main()
