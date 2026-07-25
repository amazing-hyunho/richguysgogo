from __future__ import annotations

from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from committee.industry_cycle.price_models import AssetPriceRecord
from committee.tools.industry_price_provider import (
    IndustryPriceProvider,
    PriceFetchError,
    _end_of_day_utc,
    safe_fetch_daily_prices,
)


class _AlwaysFailsProvider(IndustryPriceProvider):
    name = "always_fails"

    def fetch_daily_prices(self, **kwargs):
        raise PriceFetchError("simulated_provider_outage")


class _AlwaysSucceedsProvider(IndustryPriceProvider):
    name = "always_succeeds"

    def fetch_daily_prices(self, *, asset_id, symbol, market, currency, start, end):
        return [
            AssetPriceRecord(
                asset_id=asset_id,
                market=market,
                currency=currency,
                trade_date=start,
                close_price=100.0,
                adj_close_price=100.0,
                adjustment_status="adjusted",
                source=self.name,
                source_ref=symbol,
                available_at=_end_of_day_utc(start),
                collected_at="2026-07-25T00:00:00+00:00",
            )
        ]


class _RaisesUnexpectedError(IndustryPriceProvider):
    name = "raises_unexpected"

    def fetch_daily_prices(self, **kwargs):
        raise ValueError("not even a PriceFetchError")


class SafeFetchDailyPricesTests(unittest.TestCase):
    def test_provider_failure_does_not_raise_and_returns_reason(self) -> None:
        records, error = safe_fetch_daily_prices(
            _AlwaysFailsProvider(),
            asset_id="SOXX",
            symbol="SOXX",
            market="US",
            currency="USD",
            start="2026-01-01",
            end="2026-01-31",
        )
        self.assertEqual(records, [])
        self.assertIn("simulated_provider_outage", error or "")

    def test_unexpected_exception_type_is_also_isolated(self) -> None:
        """Isolation must not depend on the provider raising `PriceFetchError`
        specifically (design item 8: any provider failure must be caught)."""
        records, error = safe_fetch_daily_prices(
            _RaisesUnexpectedError(),
            asset_id="SOXX",
            symbol="SOXX",
            market="US",
            currency="USD",
            start="2026-01-01",
            end="2026-01-31",
        )
        self.assertEqual(records, [])
        self.assertIsNotNone(error)

    def test_successful_provider_returns_records_and_no_error(self) -> None:
        records, error = safe_fetch_daily_prices(
            _AlwaysSucceedsProvider(),
            asset_id="SOXX",
            symbol="SOXX",
            market="US",
            currency="USD",
            start="2026-01-01",
            end="2026-01-31",
        )
        self.assertIsNone(error)
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0].asset_id, "SOXX")
        self.assertEqual(records[0].adjustment_status, "adjusted")


class EndOfDayUtcPolicyTests(unittest.TestCase):
    def test_is_deterministic_function_of_trade_date_only(self) -> None:
        """The availability policy must not depend on wall-clock 'now' —
        this is what makes backfilling old prices "today" still leave them
        visible to historical as-of queries."""
        self.assertEqual(_end_of_day_utc("2015-03-02"), "2015-03-02T23:59:59+00:00")
        self.assertEqual(_end_of_day_utc("2026-07-25"), _end_of_day_utc("2026-07-25"))


class AssetPriceRecordValidationTests(unittest.TestCase):
    def test_rejects_unsupported_market(self) -> None:
        with self.assertRaises(ValueError):
            AssetPriceRecord(asset_id="X", market="JP", currency="USD", trade_date="2026-01-01")

    def test_rejects_unsupported_currency(self) -> None:
        with self.assertRaises(ValueError):
            AssetPriceRecord(asset_id="X", market="US", currency="JPY", trade_date="2026-01-01")

    def test_rejects_unsupported_adjustment_status(self) -> None:
        with self.assertRaises(ValueError):
            AssetPriceRecord(
                asset_id="X",
                market="US",
                currency="USD",
                trade_date="2026-01-01",
                adjustment_status="maybe",
            )

    def test_missing_prices_default_to_none(self) -> None:
        record = AssetPriceRecord(asset_id="X", market="US", currency="USD", trade_date="2026-01-01")
        self.assertIsNone(record.close_price)
        self.assertIsNone(record.adj_close_price)
        self.assertIsNone(record.volume)
        self.assertEqual(record.adjustment_status, "unknown")


if __name__ == "__main__":
    unittest.main()
