from __future__ import annotations

from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from committee.core.database import init_db
from committee.industry_cycle import telegram_dispatch_repository as tdr


class SchemaTests(unittest.TestCase):
    def test_table_is_created(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            db_path = Path(tmp) / "test.db"
            init_db(db_path)
            import sqlite3

            conn = sqlite3.connect(db_path)
            names = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table';")}
            self.assertIn("industry_alert_dispatch_log", names)
            conn.close()


class DispatchRepositoryTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmpdir = tempfile.TemporaryDirectory()
        self.db_path = Path(self._tmpdir.name) / "test.db"

    def tearDown(self) -> None:
        self._tmpdir.cleanup()

    def test_not_dispatched_initially(self) -> None:
        self.assertFalse(
            tdr.has_been_dispatched("semiconductors", "2026-07-25", "cycle_v1", "PRICE_CRASH", db_path=self.db_path)
        )

    def test_record_dispatched_returns_true_first_time_false_second_time(self) -> None:
        first = tdr.record_dispatched("semiconductors", "2026-07-25", "cycle_v1", "PRICE_CRASH", db_path=self.db_path)
        second = tdr.record_dispatched("semiconductors", "2026-07-25", "cycle_v1", "PRICE_CRASH", db_path=self.db_path)
        self.assertTrue(first)
        self.assertFalse(second)

    def test_has_been_dispatched_true_after_recording(self) -> None:
        tdr.record_dispatched("semiconductors", "2026-07-25", "cycle_v1", "PRICE_CRASH", db_path=self.db_path)
        self.assertTrue(
            tdr.has_been_dispatched("semiconductors", "2026-07-25", "cycle_v1", "PRICE_CRASH", db_path=self.db_path)
        )

    def test_different_alert_types_are_independent(self) -> None:
        tdr.record_dispatched("semiconductors", "2026-07-25", "cycle_v1", "PRICE_CRASH", db_path=self.db_path)
        self.assertFalse(
            tdr.has_been_dispatched("semiconductors", "2026-07-25", "cycle_v1", "EARNINGS_SHOCK", db_path=self.db_path)
        )

    def test_different_weeks_are_independent(self) -> None:
        tdr.record_dispatched("semiconductors", "2026-07-25", "cycle_v1", "PRICE_CRASH", db_path=self.db_path)
        self.assertFalse(
            tdr.has_been_dispatched("semiconductors", "2026-08-01", "cycle_v1", "PRICE_CRASH", db_path=self.db_path)
        )


if __name__ == "__main__":
    unittest.main()
