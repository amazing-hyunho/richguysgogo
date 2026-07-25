from __future__ import annotations

from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from committee.industry_cycle.price_quality import (
    check_price_discontinuities,
    check_price_duplicate_dates,
    check_price_missing_fields,
    check_price_point_in_time_anomalies,
)


class CheckPriceDuplicateDatesTests(unittest.TestCase):
    def test_detects_duplicate_asset_trade_date(self) -> None:
        rows = [
            {"asset_id": "SOXX", "trade_date": "2026-07-01"},
            {"asset_id": "SOXX", "trade_date": "2026-07-01"},
            {"asset_id": "SOXX", "trade_date": "2026-07-02"},
        ]
        events = check_price_duplicate_dates(rows)
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["event_type"], "duplicate_key")

    def test_no_duplicates_across_different_assets(self) -> None:
        rows = [
            {"asset_id": "SOXX", "trade_date": "2026-07-01"},
            {"asset_id": "091160.KS", "trade_date": "2026-07-01"},
        ]
        self.assertEqual(check_price_duplicate_dates(rows), [])


class CheckPriceMissingFieldsTests(unittest.TestCase):
    def test_flags_missing_close_price(self) -> None:
        rows = [
            {"asset_id": "SOXX", "trade_date": "2026-07-01", "close_price": None},
            {"asset_id": "SOXX", "trade_date": "2026-07-02", "close_price": 100.0},
        ]
        events = check_price_missing_fields(rows, required_fields=("close_price",))
        self.assertEqual(len(events), 1)
        self.assertIn("2026-07-01", events[0]["target"])

    def test_zero_close_price_is_not_missing(self) -> None:
        rows = [{"asset_id": "SOXX", "trade_date": "2026-07-01", "close_price": 0.0}]
        self.assertEqual(check_price_missing_fields(rows, required_fields=("close_price",)), [])

    def test_can_check_multiple_required_fields(self) -> None:
        rows = [{"asset_id": "SOXX", "trade_date": "2026-07-01", "close_price": 1.0, "volume": None}]
        events = check_price_missing_fields(rows, required_fields=("close_price", "volume"))
        self.assertEqual(len(events), 1)
        self.assertIn("volume", events[0]["message"])


class CheckPricePointInTimeAnomaliesTests(unittest.TestCase):
    def test_flags_future_trade_date(self) -> None:
        rows = [{"asset_id": "SOXX", "trade_date": "2099-01-01", "available_at": None}]
        events = check_price_point_in_time_anomalies(rows, today="2026-07-25")
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["event_type"], "point_in_time_anomaly")

    def test_flags_available_at_before_trade_date(self) -> None:
        rows = [{"asset_id": "SOXX", "trade_date": "2026-07-10", "available_at": "2026-07-01"}]
        events = check_price_point_in_time_anomalies(rows, today="2026-07-25")
        self.assertEqual(len(events), 1)

    def test_clean_row_produces_no_events(self) -> None:
        rows = [{"asset_id": "SOXX", "trade_date": "2026-07-10", "available_at": "2026-07-10"}]
        self.assertEqual(check_price_point_in_time_anomalies(rows, today="2026-07-25"), [])

    def test_collected_at_in_the_past_is_not_flagged(self) -> None:
        """collected_at is audit-only; a backfill collected long after its
        trade_date must not be treated as a point-in-time anomaly."""
        rows = [
            {
                "asset_id": "SOXX",
                "trade_date": "2015-03-02",
                "available_at": "2015-03-02",
                "collected_at": "2026-07-25",
            }
        ]
        self.assertEqual(check_price_point_in_time_anomalies(rows, today="2026-07-25"), [])


class CheckPriceDiscontinuitiesTests(unittest.TestCase):
    def test_flags_large_adjusted_price_jump(self) -> None:
        rows = [
            {"asset_id": "SOXX", "trade_date": "2026-07-01", "adj_close_price": 100.0},
            {"asset_id": "SOXX", "trade_date": "2026-07-02", "adj_close_price": 150.0},  # +50%
        ]
        events = check_price_discontinuities(rows, threshold_pct=30.0)
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["event_type"], "price_discontinuity")

    def test_no_flag_within_threshold(self) -> None:
        rows = [
            {"asset_id": "SOXX", "trade_date": "2026-07-01", "adj_close_price": 100.0},
            {"asset_id": "SOXX", "trade_date": "2026-07-02", "adj_close_price": 110.0},  # +10%
        ]
        self.assertEqual(check_price_discontinuities(rows, threshold_pct=30.0), [])

    def test_falls_back_to_close_price_when_adj_close_missing(self) -> None:
        rows = [
            {"asset_id": "SOXX", "trade_date": "2026-07-01", "close_price": 100.0},
            {"asset_id": "SOXX", "trade_date": "2026-07-02", "close_price": 200.0},
        ]
        events = check_price_discontinuities(rows, threshold_pct=30.0)
        self.assertEqual(len(events), 1)

    def test_different_assets_are_independent(self) -> None:
        rows = [
            {"asset_id": "SOXX", "trade_date": "2026-07-01", "adj_close_price": 100.0},
            {"asset_id": "091160.KS", "trade_date": "2026-07-01", "adj_close_price": 5.0},
            {"asset_id": "SOXX", "trade_date": "2026-07-02", "adj_close_price": 101.0},
            {"asset_id": "091160.KS", "trade_date": "2026-07-02", "adj_close_price": 5.05},
        ]
        self.assertEqual(check_price_discontinuities(rows, threshold_pct=30.0), [])


if __name__ == "__main__":
    unittest.main()
