from __future__ import annotations

from pathlib import Path
import sqlite3
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from committee.core.database import connect, init_db

EXPECTED_TABLES = [
    "industry_master",
    "industry_alias",
    "industry_asset_map",
    "theme_industry_map",
    "indicator_catalog",
    "industry_indicator_map",
    "indicator_observation",
    "data_quality_event",
    "asset_price_daily",
    "industry_ai_run",
]


class IndustryDatabaseMigrationTests(unittest.TestCase):
    def _fresh_db(self, td: str) -> Path:
        db_path = Path(td) / "investment.db"
        init_db(db_path)
        return db_path

    def test_new_tables_are_created(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            db_path = self._fresh_db(td)
            conn = sqlite3.connect(db_path)
            existing = {
                row[0]
                for row in conn.execute(
                    "SELECT name FROM sqlite_master WHERE type='table';"
                ).fetchall()
            }
            conn.close()
            for table in EXPECTED_TABLES:
                self.assertIn(table, existing)

    def test_init_db_is_idempotent(self) -> None:
        """Calling init_db twice on the same DB must not raise or duplicate tables."""
        with tempfile.TemporaryDirectory() as td:
            db_path = Path(td) / "investment.db"
            init_db(db_path)
            init_db(db_path)  # second call must be a no-op, not an error
            conn = sqlite3.connect(db_path)
            count = conn.execute(
                "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='industry_master';"
            ).fetchone()[0]
            conn.close()
            self.assertEqual(count, 1)

    def test_industry_ai_opinion_has_weekly_context_columns(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            db_path = self._fresh_db(td)
            with connect(db_path) as conn:
                cols = {
                    row[1]
                    for row in conn.execute(
                        "PRAGMA table_info(industry_ai_opinion);"
                    ).fetchall()
                }
            self.assertTrue(
                {
                    "prompt_version",
                    "input_hash",
                    "investment_view",
                    "weekly_change",
                    "structural_context",
                }.issubset(cols)
            )

    def test_init_db_does_not_touch_preexisting_tables(self) -> None:
        """Safety net: new migrations must not drop/alter unrelated existing tables."""
        with tempfile.TemporaryDirectory() as td:
            db_path = Path(td) / "investment.db"
            init_db(db_path)
            with connect(db_path) as conn:
                conn.execute(
                    "INSERT INTO ticker_master (ticker, company_name, market, updated_at) "
                    "VALUES ('005930', 'Samsung Electronics', 'KR', '2026-07-25T00:00:00');"
                )
            init_db(db_path)  # re-run migrations
            with connect(db_path) as conn:
                row = conn.execute(
                    "SELECT company_name FROM ticker_master WHERE ticker = '005930';"
                ).fetchone()
            self.assertIsNotNone(row)
            self.assertEqual(row["company_name"], "Samsung Electronics")

    def test_industry_indicator_map_has_working_foreign_keys(self) -> None:
        """`industry_indicator_map` must reject rows referencing unknown
        industry_id/indicator_id (design doc 9: FK + unique constraints)."""
        with tempfile.TemporaryDirectory() as td:
            db_path = self._fresh_db(td)
            with connect(db_path) as conn:
                with self.assertRaises(sqlite3.IntegrityError):
                    conn.execute(
                        """
                        INSERT INTO industry_indicator_map (
                            industry_id, indicator_id, direction, weight, created_at
                        ) VALUES ('does_not_exist', 'also_missing', 'positive', 0.5, '2026-07-25T00:00:00');
                        """
                    )

    def test_missing_values_stay_null_not_zero(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            db_path = self._fresh_db(td)
            with connect(db_path) as conn:
                conn.execute(
                    "INSERT INTO indicator_catalog (indicator_id, created_at) VALUES ('test_ind', '2026-07-25T00:00:00');"
                )
                conn.execute(
                    """
                    INSERT INTO indicator_observation (indicator_id, observed_at, value, created_at)
                    VALUES ('test_ind', '2026-06-30', NULL, '2026-07-25T00:00:00');
                    """
                )
            with connect(db_path) as conn:
                row = conn.execute(
                    "SELECT value FROM indicator_observation WHERE indicator_id = 'test_ind';"
                ).fetchone()
            self.assertIsNone(row["value"])

    def test_asset_price_daily_rejects_duplicate_asset_trade_date(self) -> None:
        """UNIQUE(asset_id, trade_date) must reject a second raw INSERT for the
        same key (application code uses upsert; this proves the DB-level
        safety net the upsert relies on for dedup)."""
        with tempfile.TemporaryDirectory() as td:
            db_path = self._fresh_db(td)
            with connect(db_path) as conn:
                conn.execute(
                    """
                    INSERT INTO asset_price_daily (
                        asset_id, market, currency, trade_date, close_price, created_at
                    ) VALUES ('SOXX', 'US', 'USD', '2026-07-01', 100.0, '2026-07-25T00:00:00');
                    """
                )
            with connect(db_path) as conn:
                with self.assertRaises(sqlite3.IntegrityError):
                    conn.execute(
                        """
                        INSERT INTO asset_price_daily (
                            asset_id, market, currency, trade_date, close_price, created_at
                        ) VALUES ('SOXX', 'US', 'USD', '2026-07-01', 101.0, '2026-07-25T00:00:01');
                        """
                    )

    def test_asset_price_daily_missing_price_stays_null(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            db_path = self._fresh_db(td)
            with connect(db_path) as conn:
                conn.execute(
                    """
                    INSERT INTO asset_price_daily (
                        asset_id, market, currency, trade_date, close_price, created_at
                    ) VALUES ('SOXX', 'US', 'USD', '2026-07-01', NULL, '2026-07-25T00:00:00');
                    """
                )
            with connect(db_path) as conn:
                row = conn.execute(
                    "SELECT close_price FROM asset_price_daily WHERE asset_id = 'SOXX';"
                ).fetchone()
            self.assertIsNone(row["close_price"])

    def test_asset_price_daily_has_available_at_and_collected_at_not_known_at(self) -> None:
        """Phase 1-A time-contract fix: the table must expose separate
        `available_at` (point-in-time gating) and `collected_at` (audit
        only) columns, and must NOT still have the old ambiguous
        `known_at` column."""
        with tempfile.TemporaryDirectory() as td:
            db_path = self._fresh_db(td)
            with connect(db_path) as conn:
                cols = {row[1] for row in conn.execute("PRAGMA table_info(asset_price_daily);").fetchall()}
            self.assertIn("available_at", cols)
            self.assertIn("collected_at", cols)
            self.assertNotIn("known_at", cols)

    def test_legacy_known_at_column_is_migrated_without_data_loss(self) -> None:
        """A DB created before the available_at/collected_at split (single
        `known_at` column) must be safely rebuilt by init_db(), preserving
        existing rows rather than raising or dropping data."""
        with tempfile.TemporaryDirectory() as td:
            db_path = Path(td) / "investment.db"
            with connect(db_path) as conn:
                # Matches the exact pre-fix Phase 1-A schema (full OHLCV column
                # set, single `known_at`) — the only schema version that ever
                # existed before this split, so the migration's SELECT list can
                # assume these columns are present.
                conn.execute(
                    """
                    CREATE TABLE asset_price_daily (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        asset_id TEXT NOT NULL,
                        market TEXT NOT NULL,
                        currency TEXT NOT NULL,
                        trade_date TEXT NOT NULL,
                        open_price REAL,
                        high_price REAL,
                        low_price REAL,
                        close_price REAL,
                        adj_close_price REAL,
                        volume REAL,
                        adjustment_status TEXT,
                        source TEXT,
                        source_ref TEXT,
                        known_at TEXT,
                        created_at TEXT,
                        UNIQUE(asset_id, trade_date)
                    );
                    """
                )
                conn.execute(
                    """
                    INSERT INTO asset_price_daily (
                        asset_id, market, currency, trade_date, close_price, known_at, created_at
                    ) VALUES ('SOXX', 'US', 'USD', '2015-03-02', 42.0, '2026-01-01T00:00:00', '2026-01-01T00:00:00');
                    """
                )

            init_db(db_path)  # must migrate the legacy schema in place

            with connect(db_path) as conn:
                cols = {row[1] for row in conn.execute("PRAGMA table_info(asset_price_daily);").fetchall()}
                self.assertNotIn("known_at", cols)
                self.assertIn("available_at", cols)
                self.assertIn("collected_at", cols)
                row = conn.execute(
                    "SELECT asset_id, trade_date, close_price, available_at, collected_at "
                    "FROM asset_price_daily WHERE asset_id = 'SOXX';"
                ).fetchone()
            self.assertIsNotNone(row)
            self.assertEqual(row["trade_date"], "2015-03-02")
            self.assertEqual(row["close_price"], 42.0)
            # Legacy rows are conservatively seeded from the old known_at for both
            # new columns (see _migrate_asset_price_daily_split_known_at).
            self.assertEqual(row["available_at"], "2026-01-01T00:00:00")
            self.assertEqual(row["collected_at"], "2026-01-01T00:00:00")


if __name__ == "__main__":
    unittest.main()
