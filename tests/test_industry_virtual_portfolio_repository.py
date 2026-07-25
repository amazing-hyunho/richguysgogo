from __future__ import annotations

from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from committee.industry_cycle import virtual_portfolio_repository as repo


def _record(**overrides):
    base = {
        "industry_id": "semiconductors",
        "model_version": "cycle_v1",
        "entry_as_of": "2026-07-25",
        "entry_trade_date": "2026-07-24",
        "asset_id": "SOXX",
        "asset_market": "US",
        "entry_price": 100.0,
        "entry_state": "CYCLE_RECOVERY_EARLY",
        "benchmark_asset_id": "SP500",
        "benchmark_entry_price": 5000.0,
    }
    base.update(overrides)
    return base


class OpenPositionTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmpdir = tempfile.TemporaryDirectory()
        self.db_path = Path(self._tmpdir.name) / "test.db"

    def tearDown(self) -> None:
        self._tmpdir.cleanup()

    def test_open_position_creates_open_row(self) -> None:
        inserted = repo.open_position(_record(), db_path=self.db_path)
        self.assertTrue(inserted)
        row = repo.get_open_position("semiconductors", "cycle_v1", db_path=self.db_path)
        self.assertIsNotNone(row)
        self.assertEqual(row["status"], "OPEN")
        self.assertEqual(row["entry_price"], 100.0)

    def test_reopening_same_entry_as_of_is_idempotent_noop(self) -> None:
        first = repo.open_position(_record(), db_path=self.db_path)
        second = repo.open_position(_record(entry_price=999.0), db_path=self.db_path)
        self.assertTrue(first)
        self.assertFalse(second)
        row = repo.get_open_position("semiconductors", "cycle_v1", db_path=self.db_path)
        self.assertEqual(row["entry_price"], 100.0)  # untouched by the second attempt

    def test_missing_required_field_raises(self) -> None:
        bad = _record()
        del bad["asset_id"]
        with self.assertRaises(ValueError):
            repo.open_position(bad, db_path=self.db_path)


class ClosePositionTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmpdir = tempfile.TemporaryDirectory()
        self.db_path = Path(self._tmpdir.name) / "test.db"
        repo.open_position(_record(), db_path=self.db_path)
        self.position = repo.get_open_position("semiconductors", "cycle_v1", db_path=self.db_path)

    def tearDown(self) -> None:
        self._tmpdir.cleanup()

    def test_close_position_transitions_status(self) -> None:
        closed = repo.close_position(
            self.position["id"],
            exit_as_of="2026-08-01",
            exit_trade_date="2026-07-31",
            exit_price=90.0,
            exit_reason="deterioration_confirmed:CYCLE_SLOWING",
            benchmark_exit_price=4900.0,
            db_path=self.db_path,
        )
        self.assertTrue(closed)
        row = repo.get_position(self.position["id"], db_path=self.db_path)
        self.assertEqual(row["status"], "CLOSED")
        self.assertEqual(row["exit_price"], 90.0)
        self.assertIsNone(repo.get_open_position("semiconductors", "cycle_v1", db_path=self.db_path))

    def test_closing_already_closed_position_is_idempotent_noop(self) -> None:
        repo.close_position(
            self.position["id"], exit_as_of="2026-08-01", exit_trade_date="2026-07-31",
            exit_price=90.0, exit_reason="r1", benchmark_exit_price=None, db_path=self.db_path,
        )
        second = repo.close_position(
            self.position["id"], exit_as_of="2026-08-08", exit_trade_date="2026-08-07",
            exit_price=1.0, exit_reason="r2", benchmark_exit_price=None, db_path=self.db_path,
        )
        self.assertFalse(second)
        row = repo.get_position(self.position["id"], db_path=self.db_path)
        self.assertEqual(row["exit_price"], 90.0)  # untouched by the second attempt


class ListPositionsTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmpdir = tempfile.TemporaryDirectory()
        self.db_path = Path(self._tmpdir.name) / "test.db"
        repo.open_position(_record(industry_id="semiconductors", entry_as_of="2026-07-25"), db_path=self.db_path)
        repo.open_position(_record(industry_id="banks", entry_as_of="2026-07-25", asset_id="KBE"), db_path=self.db_path)

    def tearDown(self) -> None:
        self._tmpdir.cleanup()

    def test_list_all(self) -> None:
        rows = repo.list_positions(db_path=self.db_path)
        self.assertEqual(len(rows), 2)

    def test_filter_by_industry(self) -> None:
        rows = repo.list_positions(industry_id="banks", db_path=self.db_path)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["industry_id"], "banks")

    def test_filter_by_status(self) -> None:
        pos = repo.get_open_position("semiconductors", "cycle_v1", db_path=self.db_path)
        repo.close_position(
            pos["id"], exit_as_of="2026-08-01", exit_trade_date="2026-07-31", exit_price=1.0,
            exit_reason="r", benchmark_exit_price=None, db_path=self.db_path,
        )
        open_rows = repo.list_positions(status="OPEN", db_path=self.db_path)
        closed_rows = repo.list_positions(status="CLOSED", db_path=self.db_path)
        self.assertEqual(len(open_rows), 1)
        self.assertEqual(len(closed_rows), 1)


if __name__ == "__main__":
    unittest.main()
