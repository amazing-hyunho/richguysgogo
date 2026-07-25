from __future__ import annotations

from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from committee.industry_cycle.data_quality import (
    check_duplicate_keys,
    check_point_in_time_anomalies,
    check_validity_overlap,
    compute_missing_rate,
)


class CheckDuplicateKeysTests(unittest.TestCase):
    def test_detects_duplicate_asset_date(self) -> None:
        rows = [
            {"asset_id": "SOXX", "trade_date": "2026-07-01"},
            {"asset_id": "SOXX", "trade_date": "2026-07-01"},
            {"asset_id": "SOXX", "trade_date": "2026-07-02"},
        ]
        events = check_duplicate_keys(rows, ["asset_id", "trade_date"])
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["event_type"], "duplicate_key")

    def test_no_duplicates_returns_empty(self) -> None:
        rows = [
            {"asset_id": "SOXX", "trade_date": "2026-07-01"},
            {"asset_id": "SOXX", "trade_date": "2026-07-02"},
        ]
        self.assertEqual(check_duplicate_keys(rows, ["asset_id", "trade_date"]), [])


class CheckPointInTimeAnomaliesTests(unittest.TestCase):
    def test_flags_future_and_leakage_rows(self) -> None:
        rows = [
            {"indicator_id": "a", "observed_at": "2026-06-30", "published_at": "2026-07-05", "known_at": "2026-07-06"},
            {"indicator_id": "b", "observed_at": "2026-06-30", "published_at": "2026-06-01"},
        ]
        events = check_point_in_time_anomalies(rows, today="2026-07-25")
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["target"], "b")


class CheckValidityOverlapTests(unittest.TestCase):
    def test_detects_overlap_for_same_group(self) -> None:
        rows = [
            {"provider": "GICS", "external_code": "453010", "valid_from": "2020-01-01", "valid_to": "2026-01-01"},
            {"provider": "GICS", "external_code": "453010", "valid_from": "2025-06-01", "valid_to": None},
        ]
        events = check_validity_overlap(rows, group_fields=["provider", "external_code"])
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["event_type"], "validity_overlap")

    def test_no_overlap_for_sequential_windows(self) -> None:
        rows = [
            {"provider": "GICS", "external_code": "453010", "valid_from": "2020-01-01", "valid_to": "2024-12-31"},
            {"provider": "GICS", "external_code": "453010", "valid_from": "2025-01-01", "valid_to": None},
        ]
        self.assertEqual(check_validity_overlap(rows, group_fields=["provider", "external_code"]), [])

    def test_different_groups_do_not_interfere(self) -> None:
        rows = [
            {"provider": "GICS", "external_code": "453010", "valid_from": "2020-01-01", "valid_to": None},
            {"provider": "KRX", "external_code": "G25", "valid_from": "2020-01-01", "valid_to": None},
        ]
        self.assertEqual(check_validity_overlap(rows, group_fields=["provider", "external_code"]), [])


class ComputeMissingRateTests(unittest.TestCase):
    def test_overall_missing_rate(self) -> None:
        rows = [{"value": 1.0}, {"value": None}, {"value": 2.0}, {"value": None}]
        self.assertAlmostEqual(compute_missing_rate(rows, value_field="value")["overall"], 0.5)

    def test_grouped_missing_rate(self) -> None:
        rows = [
            {"provider": "FRED", "value": 1.0},
            {"provider": "FRED", "value": None},
            {"provider": "KOSIS", "value": None},
            {"provider": "KOSIS", "value": None},
        ]
        rates = compute_missing_rate(rows, value_field="value", group_field="provider")
        self.assertAlmostEqual(rates["FRED"], 0.5)
        self.assertAlmostEqual(rates["KOSIS"], 1.0)

    def test_empty_rows_returns_empty_dict(self) -> None:
        self.assertEqual(compute_missing_rate([], value_field="value"), {})

    def test_zero_is_not_treated_as_missing(self) -> None:
        rows = [{"value": 0.0}, {"value": None}]
        self.assertAlmostEqual(compute_missing_rate(rows, value_field="value")["overall"], 0.5)


if __name__ == "__main__":
    unittest.main()
