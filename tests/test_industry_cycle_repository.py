from __future__ import annotations

from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from committee.core.database import init_db
from committee.industry_cycle import cycle_repository as cr


class SchemaTests(unittest.TestCase):
    def test_new_tables_are_created(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            db_path = Path(tmp) / "test.db"
            init_db(db_path)
            import sqlite3

            conn = sqlite3.connect(db_path)
            names = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table';")}
            self.assertIn("industry_cycle_signal", names)
            self.assertIn("industry_signal_reason", names)
            conn.close()


class CycleSignalRepositoryTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmpdir = tempfile.TemporaryDirectory()
        self.db_path = Path(self._tmpdir.name) / "test.db"

    def tearDown(self) -> None:
        self._tmpdir.cleanup()

    def _record(self, **overrides):
        base = {
            "industry_id": "semiconductors",
            "as_of": "2026-07-25",
            "model_version": "cycle_v1",
            "data_cutoff_at": "2026-07-25T00:00:00+00:00",
            "cycle_score": 65.4,
            "confirmed_state": "EXPANSION",
            "confidence": 0.72,
            "is_actionable": True,
            "urgent_flags": [],
            "score_breakdown": {"fundamentals_score": 70.0},
        }
        base.update(overrides)
        return base

    def test_missing_required_field_raises(self) -> None:
        record = self._record()
        del record["as_of"]
        with self.assertRaises(ValueError):
            cr.upsert_industry_cycle_signal(record, db_path=self.db_path)

    def test_upsert_and_get_roundtrip(self) -> None:
        cr.upsert_industry_cycle_signal(self._record(), db_path=self.db_path)
        row = cr.get_cycle_signal("semiconductors", "2026-07-25", "cycle_v1", db_path=self.db_path)
        self.assertIsNotNone(row)
        self.assertEqual(row["confirmed_state"], "EXPANSION")
        self.assertAlmostEqual(row["cycle_score"], 65.4)
        self.assertTrue(row["is_actionable"])
        self.assertEqual(row["urgent_flags"], [])
        self.assertEqual(row["score_breakdown"], {"fundamentals_score": 70.0})

    def test_none_score_stays_null(self) -> None:
        cr.upsert_industry_cycle_signal(self._record(cycle_score=None, confirmed_state="INSUFFICIENT_DATA"), db_path=self.db_path)
        row = cr.get_cycle_signal("semiconductors", "2026-07-25", "cycle_v1", db_path=self.db_path)
        self.assertIsNone(row["cycle_score"])

    def test_upsert_is_idempotent_not_duplicated(self) -> None:
        cr.upsert_industry_cycle_signal(self._record(), db_path=self.db_path)
        cr.upsert_industry_cycle_signal(self._record(cycle_score=80.0), db_path=self.db_path)
        rows = cr.list_cycle_signals("semiconductors", db_path=self.db_path)
        self.assertEqual(len(rows), 1)
        self.assertAlmostEqual(rows[0]["cycle_score"], 80.0)

    def test_different_model_versions_both_preserved(self) -> None:
        cr.upsert_industry_cycle_signal(self._record(model_version="cycle_v1"), db_path=self.db_path)
        cr.upsert_industry_cycle_signal(self._record(model_version="cycle_v2", cycle_score=10.0), db_path=self.db_path)
        rows = cr.list_cycle_signals("semiconductors", db_path=self.db_path)
        self.assertEqual(len(rows), 2)

    def test_get_latest_before_finds_prior_week(self) -> None:
        cr.upsert_industry_cycle_signal(self._record(as_of="2026-07-18", cycle_score=55.0), db_path=self.db_path)
        cr.upsert_industry_cycle_signal(self._record(as_of="2026-07-25", cycle_score=65.0), db_path=self.db_path)
        prev = cr.get_latest_cycle_signal_before("semiconductors", "cycle_v1", "2026-07-25", db_path=self.db_path)
        self.assertIsNotNone(prev)
        self.assertAlmostEqual(prev["cycle_score"], 55.0)


class SignalReasonRepositoryTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmpdir = tempfile.TemporaryDirectory()
        self.db_path = Path(self._tmpdir.name) / "test.db"

    def tearDown(self) -> None:
        self._tmpdir.cleanup()

    def test_missing_required_field_raises(self) -> None:
        with self.assertRaises(ValueError):
            cr.upsert_industry_signal_reason({"industry_id": "x"}, db_path=self.db_path)

    def test_replace_reasons_removes_stale_components(self) -> None:
        cr.replace_industry_signal_reasons(
            "semiconductors", "2026-07-25", "cycle_v1",
            [
                {"component_key": "fundamentals_score", "raw_value": 70.0, "weight": 0.25, "contribution": 5.0},
                {"component_key": "flow_score", "raw_value": 60.0, "weight": 0.15, "contribution": 1.5},
            ],
            db_path=self.db_path,
        )
        # Next week flow_score becomes unavailable -- replace with a smaller set.
        cr.replace_industry_signal_reasons(
            "semiconductors", "2026-07-25", "cycle_v1",
            [{"component_key": "fundamentals_score", "raw_value": 72.0, "weight": 0.30, "contribution": 6.0}],
            db_path=self.db_path,
        )
        rows = cr.list_signal_reasons("semiconductors", "2026-07-25", "cycle_v1", db_path=self.db_path)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["component_key"], "fundamentals_score")

    def test_list_ordered_by_contribution_magnitude(self) -> None:
        cr.replace_industry_signal_reasons(
            "semiconductors", "2026-07-25", "cycle_v1",
            [
                {"component_key": "a", "contribution": 1.0},
                {"component_key": "b", "contribution": -9.0},
                {"component_key": "c", "contribution": 3.0},
            ],
            db_path=self.db_path,
        )
        rows = cr.list_signal_reasons("semiconductors", "2026-07-25", "cycle_v1", db_path=self.db_path)
        self.assertEqual([r["component_key"] for r in rows], ["b", "c", "a"])


if __name__ == "__main__":
    unittest.main()
