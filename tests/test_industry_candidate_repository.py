from __future__ import annotations

from pathlib import Path
import sqlite3
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from committee.core.database import init_db
from committee.industry_cycle import candidate_repository as cr


class TempDbTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self._tmpdir = tempfile.TemporaryDirectory()
        self.db_path = Path(self._tmpdir.name) / "test.db"

    def tearDown(self) -> None:
        self._tmpdir.cleanup()


class SchemaTests(TempDbTestCase):
    def test_new_tables_are_created(self) -> None:
        init_db(self.db_path)
        conn = sqlite3.connect(self.db_path)
        existing = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()}
        conn.close()
        self.assertIn("industry_earnings_breadth_weekly", existing)
        self.assertIn("industry_candidate", existing)


class EarningsBreadthRepositoryTests(TempDbTestCase):
    def test_upsert_and_get_roundtrip(self) -> None:
        cr.upsert_industry_earnings_breadth_weekly(
            {
                "industry_id": "semiconductors",
                "as_of": "2026-07-25",
                "model_version": "stock_candidate_v1",
                "data_cutoff_at": "2026-07-25T00:00:00+00:00",
                "earnings_revision_score": 65.0,
                "earnings_revision_evidence": [{"ticker": "A", "is_improving": True}],
                "breadth_score": 55.0,
                "breadth_evidence": [{"ticker": "A", "is_positive_relative_strength": True}],
                "n_tickers_considered": 3,
            },
            db_path=self.db_path,
        )
        row = cr.get_earnings_breadth_weekly("semiconductors", "2026-07-25", "stock_candidate_v1", db_path=self.db_path)
        self.assertIsNotNone(row)
        self.assertAlmostEqual(row["earnings_revision_score"], 65.0)
        self.assertAlmostEqual(row["breadth_score"], 55.0)
        self.assertEqual(row["earnings_revision_evidence"], [{"ticker": "A", "is_improving": True}])
        self.assertEqual(row["n_tickers_considered"], 3)

    def test_upsert_is_idempotent_not_duplicated(self) -> None:
        record = {
            "industry_id": "semiconductors", "as_of": "2026-07-25", "model_version": "v1",
            "data_cutoff_at": "2026-07-25T00:00:00+00:00", "earnings_revision_score": 50.0,
        }
        cr.upsert_industry_earnings_breadth_weekly(record, db_path=self.db_path)
        cr.upsert_industry_earnings_breadth_weekly({**record, "earnings_revision_score": 70.0}, db_path=self.db_path)
        rows = cr.list_earnings_breadth_weekly("semiconductors", db_path=self.db_path)
        self.assertEqual(len(rows), 1)
        self.assertAlmostEqual(rows[0]["earnings_revision_score"], 70.0)

    def test_different_model_versions_both_preserved(self) -> None:
        base = {
            "industry_id": "semiconductors", "as_of": "2026-07-25",
            "data_cutoff_at": "2026-07-25T00:00:00+00:00",
        }
        cr.upsert_industry_earnings_breadth_weekly({**base, "model_version": "v1", "earnings_revision_score": 40.0}, db_path=self.db_path)
        cr.upsert_industry_earnings_breadth_weekly({**base, "model_version": "v2", "earnings_revision_score": 80.0}, db_path=self.db_path)
        rows = cr.list_earnings_breadth_weekly("semiconductors", db_path=self.db_path)
        self.assertEqual(len(rows), 2)

    def test_missing_required_field_raises(self) -> None:
        with self.assertRaises(ValueError):
            cr.upsert_industry_earnings_breadth_weekly({"industry_id": "semiconductors"}, db_path=self.db_path)

    def test_none_score_stays_null(self) -> None:
        cr.upsert_industry_earnings_breadth_weekly(
            {
                "industry_id": "semiconductors", "as_of": "2026-07-25", "model_version": "v1",
                "data_cutoff_at": "2026-07-25T00:00:00+00:00", "earnings_revision_score": None,
            },
            db_path=self.db_path,
        )
        row = cr.get_earnings_breadth_weekly("semiconductors", "2026-07-25", "v1", db_path=self.db_path)
        self.assertIsNone(row["earnings_revision_score"])


class CandidateRepositoryTests(TempDbTestCase):
    def _seed(self, asset_id: str, *, score: float, rank: int | None, excluded: bool = False,
              asset_type: str = "STOCK", reasons=None) -> None:
        cr.upsert_industry_candidate(
            {
                "industry_id": "semiconductors", "as_of": "2026-07-25", "model_version": "v1",
                "data_cutoff_at": "2026-07-25T00:00:00+00:00",
                "asset_id": asset_id, "asset_type": asset_type, "market": "US",
                "score": score, "rank": rank, "excluded": excluded,
                "exclusion_reasons": reasons or [],
                "data_completeness": 0.8,
            },
            db_path=self.db_path,
        )

    def test_upsert_and_list_roundtrip(self) -> None:
        self._seed("NVDA", score=90.0, rank=1)
        self._seed("AVGO", score=80.0, rank=2)
        self._seed("BADCO", score=None, rank=None, excluded=True, reasons=["capital_impairment"])

        rows = cr.list_industry_candidates("semiconductors", "2026-07-25", "v1", db_path=self.db_path)
        self.assertEqual(len(rows), 3)
        # Ranked candidates come first, ordered by rank.
        self.assertEqual(rows[0]["asset_id"], "NVDA")
        self.assertEqual(rows[1]["asset_id"], "AVGO")
        self.assertEqual(rows[2]["asset_id"], "BADCO")
        self.assertTrue(rows[2]["excluded"])
        self.assertEqual(rows[2]["exclusion_reasons"], ["capital_impairment"])
        self.assertIsNone(rows[2]["rank"])

    def test_exclude_excluded_filters_them_out(self) -> None:
        self._seed("NVDA", score=90.0, rank=1)
        self._seed("BADCO", score=None, rank=None, excluded=True, reasons=["capital_impairment"])
        rows = cr.list_industry_candidates(
            "semiconductors", "2026-07-25", "v1", include_excluded=False, db_path=self.db_path
        )
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["asset_id"], "NVDA")

    def test_filter_by_asset_type(self) -> None:
        self._seed("NVDA", score=90.0, rank=1, asset_type="STOCK")
        self._seed("SOXX", score=70.0, rank=1, asset_type="ETF")
        stock_rows = cr.list_industry_candidates("semiconductors", "2026-07-25", "v1", asset_type="STOCK", db_path=self.db_path)
        etf_rows = cr.list_industry_candidates("semiconductors", "2026-07-25", "v1", asset_type="ETF", db_path=self.db_path)
        self.assertEqual(len(stock_rows), 1)
        self.assertEqual(stock_rows[0]["asset_id"], "NVDA")
        self.assertEqual(len(etf_rows), 1)
        self.assertEqual(etf_rows[0]["asset_id"], "SOXX")

    def test_upsert_is_idempotent(self) -> None:
        self._seed("NVDA", score=90.0, rank=1)
        self._seed("NVDA", score=95.0, rank=1)
        rows = cr.list_industry_candidates("semiconductors", "2026-07-25", "v1", db_path=self.db_path)
        self.assertEqual(len(rows), 1)
        self.assertAlmostEqual(rows[0]["score"], 95.0)

    def test_get_single_candidate(self) -> None:
        self._seed("NVDA", score=90.0, rank=1)
        row = cr.get_industry_candidate("semiconductors", "2026-07-25", "v1", "NVDA", db_path=self.db_path)
        self.assertIsNotNone(row)
        self.assertAlmostEqual(row["score"], 90.0)

    def test_missing_required_field_raises(self) -> None:
        with self.assertRaises(ValueError):
            cr.upsert_industry_candidate({"industry_id": "semiconductors"}, db_path=self.db_path)


if __name__ == "__main__":
    unittest.main()
