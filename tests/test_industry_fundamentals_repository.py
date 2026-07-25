from __future__ import annotations

from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from committee.industry_cycle import fundamentals_repository


def _record(**overrides):
    defaults = dict(
        industry_id="semiconductors",
        as_of="2024-06-15",
        model_version="fundamentals_only_v1",
        data_cutoff_at="2024-06-15",
        data_completeness=0.75,
        fundamentals_score=62.5,
        weighted_sum=0.5,
        reason=None,
        indicators_used=[{"indicator_id": "a", "raw_value": 1.0}],
    )
    defaults.update(overrides)
    return defaults


class UpsertTests(unittest.TestCase):
    def test_rerunning_same_key_is_idempotent(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            db_path = Path(td) / "investment.db"
            for _ in range(3):
                fundamentals_repository.upsert_industry_fundamentals_weekly(_record(), db_path=db_path)
            rows = fundamentals_repository.list_fundamentals_weekly("semiconductors", db_path=db_path)
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["fundamentals_score"], 62.5)

    def test_rerun_with_changed_score_overwrites_in_place(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            db_path = Path(td) / "investment.db"
            fundamentals_repository.upsert_industry_fundamentals_weekly(_record(fundamentals_score=60.0), db_path=db_path)
            fundamentals_repository.upsert_industry_fundamentals_weekly(_record(fundamentals_score=70.0), db_path=db_path)
            rows = fundamentals_repository.list_fundamentals_weekly("semiconductors", db_path=db_path)
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["fundamentals_score"], 70.0)

    def test_different_model_version_preserves_old_row(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            db_path = Path(td) / "investment.db"
            fundamentals_repository.upsert_industry_fundamentals_weekly(
                _record(model_version="fundamentals_only_v1", fundamentals_score=60.0), db_path=db_path
            )
            fundamentals_repository.upsert_industry_fundamentals_weekly(
                _record(model_version="fundamentals_only_v2", fundamentals_score=80.0), db_path=db_path
            )
            rows = fundamentals_repository.list_fundamentals_weekly("semiconductors", db_path=db_path)
            self.assertEqual(len(rows), 2)
            versions = {r["model_version"]: r["fundamentals_score"] for r in rows}
            self.assertEqual(versions, {"fundamentals_only_v1": 60.0, "fundamentals_only_v2": 80.0})

    def test_missing_score_is_stored_as_null_not_zero(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            db_path = Path(td) / "investment.db"
            fundamentals_repository.upsert_industry_fundamentals_weekly(
                _record(fundamentals_score=None, reason="insufficient_data"), db_path=db_path
            )
            row = fundamentals_repository.get_fundamentals_weekly(
                "semiconductors", "2024-06-15", "fundamentals_only_v1", db_path=db_path
            )
            self.assertIsNone(row["fundamentals_score"])
            self.assertEqual(row["reason"], "insufficient_data")

    def test_indicators_used_json_round_trips(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            db_path = Path(td) / "investment.db"
            fundamentals_repository.upsert_industry_fundamentals_weekly(_record(), db_path=db_path)
            row = fundamentals_repository.get_fundamentals_weekly(
                "semiconductors", "2024-06-15", "fundamentals_only_v1", db_path=db_path
            )
            self.assertEqual(row["indicators_used"], [{"indicator_id": "a", "raw_value": 1.0}])

    def test_missing_required_field_raises(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            db_path = Path(td) / "investment.db"
            record = _record()
            del record["industry_id"]
            with self.assertRaises(ValueError):
                fundamentals_repository.upsert_industry_fundamentals_weekly(record, db_path=db_path)


class GetLatestBeforeTests(unittest.TestCase):
    def test_returns_most_recent_prior_row(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            db_path = Path(td) / "investment.db"
            fundamentals_repository.upsert_industry_fundamentals_weekly(
                _record(as_of="2024-06-01", fundamentals_score=50.0), db_path=db_path
            )
            fundamentals_repository.upsert_industry_fundamentals_weekly(
                _record(as_of="2024-06-08", fundamentals_score=55.0), db_path=db_path
            )
            latest = fundamentals_repository.get_latest_fundamentals_before(
                "semiconductors", "2024-06-15", "fundamentals_only_v1", db_path=db_path
            )
            self.assertEqual(latest["as_of"], "2024-06-08")
            self.assertEqual(latest["fundamentals_score"], 55.0)

    def test_none_when_no_prior_row(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            db_path = Path(td) / "investment.db"
            latest = fundamentals_repository.get_latest_fundamentals_before(
                "semiconductors", "2024-06-15", "fundamentals_only_v1", db_path=db_path
            )
            self.assertIsNone(latest)


if __name__ == "__main__":
    unittest.main()
