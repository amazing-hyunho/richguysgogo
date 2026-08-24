from __future__ import annotations

from datetime import date
import json
from pathlib import Path
import tempfile
import unittest

from committee.future_economy.context import load_latest_committee_agenda


class FutureEconomyContextTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.runs_dir = Path(self.tmp.name)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def _write(self, as_of: str, item_count: int = 1) -> None:
        target = self.runs_dir / as_of / "future_economy" / "committee_agenda.json"
        target.parent.mkdir(parents=True)
        target.write_text(
            json.dumps({
                "schema_version": "future-economy-committee-agenda-v1",
                "as_of": as_of,
                "items": [{"research_id": f"r-{index}"} for index in range(item_count)],
            }),
            encoding="utf-8",
        )

    def test_latest_non_stale_agenda_is_loaded_and_bounded(self) -> None:
        self._write("2026-08-17", item_count=5)
        self._write("2026-08-24", item_count=5)
        result = load_latest_committee_agenda(runs_dir=self.runs_dir, as_of=date(2026, 8, 25))
        self.assertEqual(result["as_of"], "2026-08-24")
        self.assertFalse(result["stale"])
        self.assertEqual(len(result["items"]), 3)

    def test_agenda_older_than_fourteen_days_is_not_forwarded(self) -> None:
        self._write("2026-08-01")
        result = load_latest_committee_agenda(runs_dir=self.runs_dir, as_of=date(2026, 8, 25))
        self.assertTrue(result["stale"])
        self.assertEqual(result["items"], [])
        self.assertEqual(result["reason"], "agenda_too_old")


if __name__ == "__main__":
    unittest.main()
