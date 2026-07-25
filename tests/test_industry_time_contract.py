from __future__ import annotations

from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from committee.industry_cycle.time_contract import (
    filter_known_as_of,
    is_known_by,
    validate_point_in_time_row,
)


class IsKnownByTests(unittest.TestCase):
    def test_known_before_as_of_is_true(self) -> None:
        row = {"known_at": "2026-07-01"}
        self.assertTrue(is_known_by(row, "2026-07-15"))

    def test_known_after_as_of_is_false(self) -> None:
        row = {"known_at": "2026-08-01"}
        self.assertFalse(is_known_by(row, "2026-07-15"))

    def test_known_equal_as_of_is_true(self) -> None:
        row = {"known_at": "2026-07-15"}
        self.assertTrue(is_known_by(row, "2026-07-15"))

    def test_missing_known_at_is_conservatively_false(self) -> None:
        row = {"known_at": None}
        self.assertFalse(is_known_by(row, "2026-07-15"))

    def test_custom_known_at_field(self) -> None:
        row = {"collected_at": "2026-07-01"}
        self.assertTrue(is_known_by(row, "2026-07-15", known_at_field="collected_at"))


class FilterKnownAsOfTests(unittest.TestCase):
    def test_filters_out_future_knowledge(self) -> None:
        rows = [
            {"observed_at": "2026-05-01", "known_at": "2026-05-02", "v": 1},
            {"observed_at": "2026-05-01", "known_at": "2026-05-10", "v": 2},
            {"observed_at": "2026-05-03", "known_at": None, "v": 3},
        ]
        visible = filter_known_as_of(rows, "2026-05-03")
        self.assertEqual([r["v"] for r in visible], [1])


class ValidatePointInTimeRowTests(unittest.TestCase):
    def test_valid_row_has_no_issues(self) -> None:
        row = {
            "observed_at": "2026-06-30",
            "published_at": "2026-07-05",
            "known_at": "2026-07-06",
        }
        self.assertEqual(validate_point_in_time_row(row, today="2026-07-25"), [])

    def test_missing_observed_at_is_flagged(self) -> None:
        row = {"published_at": "2026-07-05", "known_at": "2026-07-06"}
        issues = validate_point_in_time_row(row, today="2026-07-25")
        self.assertTrue(any("observed_at is required" in i for i in issues))

    def test_future_dated_row_is_flagged(self) -> None:
        row = {"observed_at": "2026-08-01"}
        issues = validate_point_in_time_row(row, today="2026-07-25")
        self.assertTrue(any("is in the future" in i for i in issues))

    def test_published_before_observed_is_flagged(self) -> None:
        row = {"observed_at": "2026-06-30", "published_at": "2026-06-01"}
        issues = validate_point_in_time_row(row, today="2026-07-25")
        self.assertTrue(any("earlier than observed_at" in i for i in issues))

    def test_known_before_published_is_flagged(self) -> None:
        row = {"observed_at": "2026-06-30", "published_at": "2026-07-05", "known_at": "2026-07-01"}
        issues = validate_point_in_time_row(row, today="2026-07-25")
        self.assertTrue(any("earlier than published_at" in i for i in issues))

    def test_unparseable_observed_at_is_flagged(self) -> None:
        row = {"observed_at": "not-a-date"}
        issues = validate_point_in_time_row(row, today="2026-07-25")
        self.assertTrue(any("not a valid date" in i for i in issues))


if __name__ == "__main__":
    unittest.main()
