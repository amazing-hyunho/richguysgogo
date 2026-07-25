from __future__ import annotations

from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from committee.industry_cycle import repository


SAMPLE_TAXONOMY = {
    "industries": [
        {
            "industry_id": "semiconductors",
            "name_kr": "반도체",
            "name_en": "Semiconductors",
            "country_scope": ["KR", "US"],
            "active": True,
            "coverage_status": "INSUFFICIENT",
            "aliases": [
                {"provider": "GICS", "external_code": "453010", "valid_from": "2026-07-25", "valid_to": None}
            ],
        },
        {
            "industry_id": "banks",
            "name_kr": "은행",
            "name_en": "Banks",
            "country_scope": ["KR"],
            "active": True,
            "coverage_status": "INSUFFICIENT",
            "aliases": [],
        },
    ]
}


class IndustryMasterSyncTests(unittest.TestCase):
    def test_sync_creates_expected_rows(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            db_path = Path(td) / "investment.db"
            count = repository.sync_industry_master_from_config(SAMPLE_TAXONOMY, db_path=db_path)
            self.assertEqual(count, 2)

            industries = repository.list_industries(db_path=db_path)
            self.assertEqual({i["industry_id"] for i in industries}, {"semiconductors", "banks"})

            semis = repository.get_industry("semiconductors", db_path=db_path)
            self.assertEqual(semis["name_kr"], "반도체")
            self.assertEqual(semis["country_scope"], ["KR", "US"])

            aliases = repository.list_industry_aliases("semiconductors", db_path=db_path)
            self.assertEqual(len(aliases), 1)
            self.assertEqual(aliases[0]["external_code"], "453010")

    def test_sync_is_reproducible(self) -> None:
        """Same input config -> same DB rows, run twice (Phase 0 completion criterion)."""
        with tempfile.TemporaryDirectory() as td:
            db_path = Path(td) / "investment.db"
            repository.sync_industry_master_from_config(SAMPLE_TAXONOMY, db_path=db_path)
            first = repository.list_industries(db_path=db_path)
            repository.sync_industry_master_from_config(SAMPLE_TAXONOMY, db_path=db_path)
            second = repository.list_industries(db_path=db_path)

            self.assertEqual(len(first), len(second))
            first_by_id = {r["industry_id"]: r for r in first}
            second_by_id = {r["industry_id"]: r for r in second}
            for industry_id, row in first_by_id.items():
                other = second_by_id[industry_id]
                self.assertEqual(row["name_kr"], other["name_kr"])
                self.assertEqual(row["country_scope"], other["country_scope"])
                self.assertEqual(row["coverage_status"], other["coverage_status"])

            aliases_after_two_runs = repository.list_industry_aliases("semiconductors", db_path=db_path)
            self.assertEqual(len(aliases_after_two_runs), 1)

    def test_alias_upsert_with_null_valid_from_does_not_duplicate(self) -> None:
        """SQLite treats NULL as distinct in UNIQUE constraints; the repository
        must not rely on `ON CONFLICT` alone for `valid_from IS NULL` rows."""
        with tempfile.TemporaryDirectory() as td:
            db_path = Path(td) / "investment.db"
            repository.sync_industry_master_from_config(SAMPLE_TAXONOMY, db_path=db_path)
            for _ in range(3):
                repository.upsert_industry_alias(
                    provider="KRX",
                    external_code="G25",
                    industry_id="semiconductors",
                    valid_from=None,
                    db_path=db_path,
                )
            aliases = repository.list_industry_aliases("semiconductors", db_path=db_path)
            krx_aliases = [a for a in aliases if a["provider"] == "KRX"]
            self.assertEqual(len(krx_aliases), 1)

    def test_asset_map_upsert_with_null_valid_from_does_not_duplicate(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            db_path = Path(td) / "investment.db"
            repository.sync_industry_master_from_config(SAMPLE_TAXONOMY, db_path=db_path)
            for _ in range(3):
                repository.upsert_industry_asset_map(
                    asset_id="SOXX",
                    industry_id="semiconductors",
                    asset_type="ETF",
                    market="US",
                    valid_from=None,
                    db_path=db_path,
                )
            assets = repository.list_industry_assets("semiconductors", db_path=db_path)
            self.assertEqual(len(assets), 1)

    def test_theme_map_upsert_with_null_valid_from_does_not_duplicate(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            db_path = Path(td) / "investment.db"
            repository.sync_industry_master_from_config(SAMPLE_TAXONOMY, db_path=db_path)
            for _ in range(3):
                repository.upsert_theme_industry_map(
                    theme_id="hbm",
                    industry_id="semiconductors",
                    valid_from=None,
                    db_path=db_path,
                )
            themes = repository.list_theme_industries("hbm", db_path=db_path)
            self.assertEqual(len(themes), 1)


class IndustryAssetMapTests(unittest.TestCase):
    def test_sync_and_list_assets(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            db_path = Path(td) / "investment.db"
            repository.sync_industry_master_from_config(SAMPLE_TAXONOMY, db_path=db_path)
            mapping = {
                "mappings": [
                    {
                        "asset_id": "SOXX",
                        "asset_type": "ETF",
                        "market": "US",
                        "industry_id": "semiconductors",
                        "weight": 1.0,
                        "valid_from": "2026-07-25",
                        "valid_to": None,
                    }
                ]
            }
            count = repository.sync_industry_assets_from_config(mapping, db_path=db_path)
            self.assertEqual(count, 1)
            assets = repository.list_industry_assets("semiconductors", db_path=db_path)
            self.assertEqual(len(assets), 1)
            self.assertEqual(assets[0]["asset_id"], "SOXX")
            self.assertEqual(assets[0]["weight"], 1.0)


class ThemeIndustryMapTests(unittest.TestCase):
    def test_upsert_and_list(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            db_path = Path(td) / "investment.db"
            repository.sync_industry_master_from_config(SAMPLE_TAXONOMY, db_path=db_path)
            repository.upsert_theme_industry_map(
                theme_id="hbm", industry_id="semiconductors", valid_from="2026-07-25", db_path=db_path
            )
            themes = repository.list_theme_industries("hbm", db_path=db_path)
            self.assertEqual(len(themes), 1)
            self.assertEqual(themes[0]["industry_id"], "semiconductors")


class IndicatorCatalogAndObservationTests(unittest.TestCase):
    def test_catalog_sync(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            db_path = Path(td) / "investment.db"
            catalog = {
                "indicators": [
                    {
                        "indicator_id": "us_ism_pmi",
                        "provider": "FRED",
                        "series_id": "NAPM",
                        "unit": "index",
                        "frequency": "monthly",
                        "transform": "level",
                    }
                ]
            }
            count = repository.sync_indicator_catalog_from_config(catalog, db_path=db_path)
            self.assertEqual(count, 1)
            indicators = repository.list_indicators(db_path=db_path)
            self.assertEqual(indicators[0]["indicator_id"], "us_ism_pmi")

    def test_missing_observation_value_stays_null(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            db_path = Path(td) / "investment.db"
            repository.upsert_indicator_catalog(indicator_id="us_ism_pmi", db_path=db_path)
            repository.insert_indicator_observation(
                indicator_id="us_ism_pmi",
                observed_at="2026-06-30",
                value=None,
                published_at="2026-07-01",
                known_at="2026-07-01",
                db_path=db_path,
            )
            rows = repository.get_observations_as_of("us_ism_pmi", "2026-12-31", db_path=db_path)
            self.assertEqual(len(rows), 1)
            self.assertIsNone(rows[0]["value"])

    def test_get_observations_as_of_excludes_future_known_at(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            db_path = Path(td) / "investment.db"
            repository.upsert_indicator_catalog(indicator_id="us_ism_pmi", db_path=db_path)
            repository.insert_indicator_observation(
                indicator_id="us_ism_pmi",
                observed_at="2026-06-30",
                value=52.1,
                known_at="2026-07-01",
                db_path=db_path,
            )
            repository.insert_indicator_observation(
                indicator_id="us_ism_pmi",
                observed_at="2026-07-31",
                value=53.4,
                known_at="2026-08-01",
                db_path=db_path,
            )
            visible = repository.get_observations_as_of("us_ism_pmi", "2026-07-15", db_path=db_path)
            self.assertEqual(len(visible), 1)
            self.assertEqual(visible[0]["observed_at"], "2026-06-30")

    def test_as_of_bare_date_includes_full_day_of_datetime_known_at(self) -> None:
        """`as_of` is often a bare date while `known_at` may carry a full ISO
        timestamp; any known_at within that same calendar day (00:00~23:59)
        must be included, and this must not depend on SQL string ordering."""
        with tempfile.TemporaryDirectory() as td:
            db_path = Path(td) / "investment.db"
            repository.upsert_indicator_catalog(indicator_id="us_ism_pmi", db_path=db_path)
            repository.insert_indicator_observation(
                indicator_id="us_ism_pmi",
                observed_at="2026-06-30",
                value=52.1,
                known_at="2026-07-15T00:00:01+00:00",
                vintage_at="2026-07-15T00:00:01+00:00",
                db_path=db_path,
            )
            repository.insert_indicator_observation(
                indicator_id="us_ism_pmi",
                observed_at="2026-07-31",
                value=53.0,
                known_at="2026-07-15T23:59:59+00:00",
                vintage_at="2026-07-15T23:59:59+00:00",
                db_path=db_path,
            )
            repository.insert_indicator_observation(
                indicator_id="us_ism_pmi",
                observed_at="2026-08-31",
                value=54.0,
                known_at="2026-07-16T00:00:01+00:00",
                vintage_at="2026-07-16T00:00:01+00:00",
                db_path=db_path,
            )

            visible = repository.get_observations_as_of("us_ism_pmi", "2026-07-15", db_path=db_path)
            visible_observed_ats = {r["observed_at"] for r in visible}
            self.assertEqual(visible_observed_ats, {"2026-06-30", "2026-07-31"})

            # A known_at that is one second into the *next* day must not appear yet.
            self.assertNotIn("2026-08-31", visible_observed_ats)

    def test_revision_creates_new_vintage_row_without_overwriting(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            db_path = Path(td) / "investment.db"
            repository.upsert_indicator_catalog(indicator_id="us_ism_pmi", db_path=db_path)
            repository.insert_indicator_observation(
                indicator_id="us_ism_pmi",
                observed_at="2026-06-30",
                value=52.1,
                known_at="2026-07-01",
                vintage_at="2026-07-01",
                db_path=db_path,
            )
            repository.insert_indicator_observation(
                indicator_id="us_ism_pmi",
                observed_at="2026-06-30",
                value=52.5,
                known_at="2026-08-01",
                vintage_at="2026-08-01",
                db_path=db_path,
            )
            as_of_july = repository.get_observations_as_of("us_ism_pmi", "2026-07-15", db_path=db_path)
            self.assertEqual(len(as_of_july), 1)
            self.assertEqual(as_of_july[0]["value"], 52.1)

            as_of_august = repository.get_observations_as_of("us_ism_pmi", "2026-08-15", db_path=db_path)
            self.assertEqual(len(as_of_august), 2)

    def test_revision_without_explicit_vintage_still_does_not_overwrite_past(self) -> None:
        """A caller that forgets to pass `vintage_at` for a later revision must
        not silently erase what was knowable in the past (design doc 5.1:
        "최신 데이터로 과거 신호를 다시 덮어쓰지 않는다")."""
        with tempfile.TemporaryDirectory() as td:
            db_path = Path(td) / "investment.db"
            repository.upsert_indicator_catalog(indicator_id="us_ism_pmi", db_path=db_path)
            repository.insert_indicator_observation(
                indicator_id="us_ism_pmi",
                observed_at="2026-06-30",
                value=52.1,
                known_at="2026-07-01",
                db_path=db_path,
            )
            # Simulate a later revision collected on a different day, without the
            # caller explicitly passing vintage_at.
            repository.insert_indicator_observation(
                indicator_id="us_ism_pmi",
                observed_at="2026-06-30",
                value=52.5,
                known_at="2026-08-01",
                db_path=db_path,
            )

            as_of_july = repository.get_observations_as_of("us_ism_pmi", "2026-07-15", db_path=db_path)
            self.assertEqual(len(as_of_july), 1)
            self.assertEqual(as_of_july[0]["value"], 52.1)

            as_of_august = repository.get_observations_as_of("us_ism_pmi", "2026-08-15", db_path=db_path)
            self.assertEqual(len(as_of_august), 2)

    def test_same_data_reinsert_without_known_at_is_idempotent(self) -> None:
        """Re-running an identical fetch (no explicit known_at/vintage_at) at a
        different wall-clock time must NOT create a duplicate vintage row."""
        with tempfile.TemporaryDirectory() as td:
            db_path = Path(td) / "investment.db"
            repository.upsert_indicator_catalog(indicator_id="us_ism_pmi", db_path=db_path)

            with patch(
                "committee.industry_cycle.repository._now_iso",
                return_value="2026-07-01T00:00:00+00:00",
            ):
                repository.insert_indicator_observation(
                    indicator_id="us_ism_pmi",
                    observed_at="2026-06-30",
                    value=52.1,
                    db_path=db_path,
                )

            # Same value, same metadata, but re-run "a day later" (different now()).
            with patch(
                "committee.industry_cycle.repository._now_iso",
                return_value="2026-07-02T00:00:00+00:00",
            ):
                repository.insert_indicator_observation(
                    indicator_id="us_ism_pmi",
                    observed_at="2026-06-30",
                    value=52.1,
                    db_path=db_path,
                )

            all_rows = repository.get_observations_as_of("us_ism_pmi", "2099-01-01", db_path=db_path)
            self.assertEqual(len(all_rows), 1)
            # known_at/vintage_at must stay pinned to the *first* collection, not
            # drift to the second call's wall-clock time.
            self.assertEqual(all_rows[0]["known_at"], "2026-07-01T00:00:00+00:00")
            self.assertEqual(all_rows[0]["vintage_at"], "2026-07-01T00:00:00+00:00")

    def test_changed_value_without_known_at_creates_new_vintage(self) -> None:
        """A genuinely different value (no explicit known_at/vintage_at) must
        still be preserved as a new vintage rather than merged/lost."""
        with tempfile.TemporaryDirectory() as td:
            db_path = Path(td) / "investment.db"
            repository.upsert_indicator_catalog(indicator_id="us_ism_pmi", db_path=db_path)

            with patch(
                "committee.industry_cycle.repository._now_iso",
                return_value="2026-07-01T00:00:00+00:00",
            ):
                repository.insert_indicator_observation(
                    indicator_id="us_ism_pmi",
                    observed_at="2026-06-30",
                    value=52.1,
                    db_path=db_path,
                )

            with patch(
                "committee.industry_cycle.repository._now_iso",
                return_value="2026-08-01T00:00:00+00:00",
            ):
                repository.insert_indicator_observation(
                    indicator_id="us_ism_pmi",
                    observed_at="2026-06-30",
                    value=53.0,  # genuine revision
                    db_path=db_path,
                )

            all_rows = repository.get_observations_as_of("us_ism_pmi", "2099-01-01", db_path=db_path)
            self.assertEqual(len(all_rows), 2)
            values = sorted(r["value"] for r in all_rows)
            self.assertEqual(values, [52.1, 53.0])

            # The original vintage must still be visible as of its own known_at,
            # i.e. it was preserved, not overwritten.
            as_of_july = repository.get_observations_as_of("us_ism_pmi", "2026-07-15", db_path=db_path)
            self.assertEqual(len(as_of_july), 1)
            self.assertEqual(as_of_july[0]["value"], 52.1)


class IndustryIndicatorMapTests(unittest.TestCase):
    def _setup_base(self, db_path: Path) -> None:
        repository.sync_industry_master_from_config(SAMPLE_TAXONOMY, db_path=db_path)
        repository.upsert_indicator_catalog(indicator_id="us_ism_pmi", db_path=db_path)

    def test_upsert_and_list(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            db_path = Path(td) / "investment.db"
            self._setup_base(db_path)
            repository.upsert_industry_indicator_map(
                industry_id="semiconductors",
                indicator_id="us_ism_pmi",
                direction="positive",
                weight=0.5,
                valid_from="2026-07-25",
                db_path=db_path,
            )
            rows = repository.list_industry_indicators("semiconductors", db_path=db_path)
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["indicator_id"], "us_ism_pmi")
            self.assertEqual(rows[0]["direction"], "positive")
            self.assertEqual(rows[0]["weight"], 0.5)

    def test_sync_from_config(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            db_path = Path(td) / "investment.db"
            self._setup_base(db_path)
            mapping = {
                "industry_indicator_mappings": [
                    {
                        "industry_id": "semiconductors",
                        "indicator_id": "us_ism_pmi",
                        "direction": "positive",
                        "weight": 0.5,
                        "valid_from": "2026-07-25",
                        "valid_to": None,
                    }
                ]
            }
            count = repository.sync_industry_indicator_map_from_config(mapping, db_path=db_path)
            self.assertEqual(count, 1)
            rows = repository.list_industry_indicators("semiconductors", db_path=db_path)
            self.assertEqual(len(rows), 1)

    def test_upsert_with_null_valid_from_does_not_duplicate(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            db_path = Path(td) / "investment.db"
            self._setup_base(db_path)
            for _ in range(3):
                repository.upsert_industry_indicator_map(
                    industry_id="semiconductors",
                    indicator_id="us_ism_pmi",
                    direction="positive",
                    valid_from=None,
                    db_path=db_path,
                )
            rows = repository.list_industry_indicators("semiconductors", db_path=db_path)
            self.assertEqual(len(rows), 1)

    def test_unknown_industry_id_raises_foreign_key_error(self) -> None:
        import sqlite3

        with tempfile.TemporaryDirectory() as td:
            db_path = Path(td) / "investment.db"
            self._setup_base(db_path)
            with self.assertRaises(sqlite3.IntegrityError):
                repository.upsert_industry_indicator_map(
                    industry_id="does_not_exist",
                    indicator_id="us_ism_pmi",
                    db_path=db_path,
                )


class DataQualityEventRepositoryTests(unittest.TestCase):
    def test_record_and_list_events(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            db_path = Path(td) / "investment.db"
            event_id = repository.record_data_quality_event(
                event_type="missing_data",
                provider="KOSIS",
                target="kr_semiconductor_production_index",
                severity="medium",
                message="no observation for 2026-06",
                db_path=db_path,
            )
            self.assertGreater(event_id, 0)
            open_events = repository.list_data_quality_events(status="open", db_path=db_path)
            self.assertEqual(len(open_events), 1)
            self.assertEqual(open_events[0]["event_type"], "missing_data")


if __name__ == "__main__":
    unittest.main()
