from __future__ import annotations

from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from committee.industry_cycle import fundamentals_ingest, repository


class ApplyTransformTests(unittest.TestCase):
    def test_level_passes_through_unchanged(self) -> None:
        rows = [{"observed_at": "2024-01-01", "value": 55.0, "published_at": "2024-02-01"}]
        out = fundamentals_ingest.apply_transform(rows, transform="level", frequency="monthly")
        self.assertEqual(out, rows)

    def test_mom_pct_uses_one_period_back(self) -> None:
        rows = [
            {"observed_at": "2024-01-01", "value": 100.0, "published_at": "p1"},
            {"observed_at": "2024-02-01", "value": 110.0, "published_at": "p2"},
        ]
        out = fundamentals_ingest.apply_transform(rows, transform="mom_pct", frequency="monthly")
        self.assertEqual(len(out), 1)
        self.assertAlmostEqual(out[0]["value"], 10.0)
        self.assertEqual(out[0]["observed_at"], "2024-02-01")

    def test_yoy_pct_uses_twelve_periods_back_for_monthly(self) -> None:
        rows = [{"observed_at": f"2023-{m:02d}-01", "value": 100.0, "published_at": "p"} for m in range(1, 13)]
        rows.append({"observed_at": "2024-01-01", "value": 110.0, "published_at": "p2"})
        out = fundamentals_ingest.apply_transform(rows, transform="yoy_pct", frequency="monthly")
        self.assertEqual(len(out), 1)
        self.assertAlmostEqual(out[0]["value"], 10.0)

    def test_insufficient_history_drops_entries_not_zero_fills(self) -> None:
        rows = [{"observed_at": "2024-01-01", "value": 100.0, "published_at": "p"}]
        out = fundamentals_ingest.apply_transform(rows, transform="yoy_pct", frequency="monthly")
        self.assertEqual(out, [])

    def test_zero_prior_value_is_dropped_not_divided(self) -> None:
        rows = [
            {"observed_at": "2024-01-01", "value": 0.0, "published_at": "p1"},
            {"observed_at": "2024-02-01", "value": 5.0, "published_at": "p2"},
        ]
        out = fundamentals_ingest.apply_transform(rows, transform="mom_pct", frequency="monthly")
        self.assertEqual(out, [])

    def test_unknown_transform_raises(self) -> None:
        with self.assertRaises(ValueError):
            fundamentals_ingest.apply_transform([], transform="bogus", frequency="monthly")


class IngestIndicatorTests(unittest.TestCase):
    def test_unsupported_provider_is_skipped(self) -> None:
        entry = {"indicator_id": "x", "provider": "ECOS", "series_id": "901Y011", "transform": "level"}
        result = fundamentals_ingest.ingest_indicator(entry)
        self.assertEqual(result.status, "skipped")
        self.assertTrue(result.reason.startswith("unsupported_provider"))

    def test_tbd_series_id_is_skipped(self) -> None:
        entry = {"indicator_id": "x", "provider": "KOSIS", "series_id": "TBD", "transform": "level"}
        result = fundamentals_ingest.ingest_indicator(entry)
        self.assertEqual(result.status, "skipped")
        self.assertEqual(result.reason, "series_id_not_configured")

    def test_fred_success_writes_observations_with_known_at_from_published_at(self) -> None:
        entry = {
            "indicator_id": "us_test_indicator",
            "provider": "FRED",
            "series_id": "TESTSERIES",
            "transform": "level",
            "frequency": "monthly",
        }
        fake_rows = [
            {"observed_at": "2024-01-01", "value": 55.0, "published_at": "2024-02-01"},
            {"observed_at": "2024-02-01", "value": 56.0, "published_at": "2024-03-01"},
        ]
        with tempfile.TemporaryDirectory() as td:
            db_path = Path(td) / "investment.db"
            with mock.patch(
                "committee.tools.fred_industry_provider.fetch_fred_series_initial_releases",
                return_value=fake_rows,
            ):
                result = fundamentals_ingest.ingest_indicator(entry, db_path=db_path)
            self.assertEqual(result.status, "ok")
            self.assertEqual(result.rows_written, 2)
            observations = repository.get_observations_as_of("us_test_indicator", "2030-01-01", db_path=db_path)
            self.assertEqual(len(observations), 2)
            row = next(o for o in observations if o["observed_at"] == "2024-01-01")
            self.assertEqual(row["value"], 55.0)
            self.assertEqual(row["known_at"], "2024-02-01")
            self.assertEqual(row["published_at"], "2024-02-01")

    def test_provider_returning_none_is_skipped(self) -> None:
        entry = {"indicator_id": "x", "provider": "FRED", "series_id": "NOKEY", "transform": "level"}
        with mock.patch(
            "committee.tools.fred_industry_provider.fetch_fred_series_initial_releases", return_value=None
        ):
            result = fundamentals_ingest.ingest_indicator(entry)
        self.assertEqual(result.status, "skipped")
        self.assertEqual(result.reason, "provider_unavailable")

    def test_yoy_transform_with_only_one_observation_is_skipped(self) -> None:
        entry = {"indicator_id": "x", "provider": "FRED", "series_id": "S", "transform": "yoy_pct", "frequency": "monthly"}
        with mock.patch(
            "committee.tools.fred_industry_provider.fetch_fred_series_initial_releases",
            return_value=[{"observed_at": "2024-01-01", "value": 1.0, "published_at": "p"}],
        ):
            result = fundamentals_ingest.ingest_indicator(entry)
        self.assertEqual(result.status, "skipped")
        self.assertEqual(result.reason, "insufficient_history_for_transform")


class IngestCatalogTests(unittest.TestCase):
    def test_one_indicator_failure_does_not_stop_the_batch(self) -> None:
        entries = [
            {"indicator_id": "bad", "provider": "FRED", "series_id": "BADSERIES", "transform": "level"},
            {"indicator_id": "good", "provider": "FRED", "series_id": "GOODSERIES", "transform": "level"},
        ]

        def _fake_fetch(series_id, **kwargs):
            if series_id == "BADSERIES":
                raise RuntimeError("boom")
            return [{"observed_at": "2024-01-01", "value": 1.0, "published_at": "2024-01-02"}]

        with tempfile.TemporaryDirectory() as td:
            db_path = Path(td) / "investment.db"
            with mock.patch(
                "committee.tools.fred_industry_provider.fetch_fred_series_initial_releases",
                side_effect=_fake_fetch,
            ):
                results = fundamentals_ingest.ingest_catalog(entries, db_path=db_path)
        by_id = {r.indicator_id: r for r in results}
        self.assertEqual(by_id["bad"].status, "failed")
        self.assertEqual(by_id["good"].status, "ok")

    def test_failed_indicator_records_a_data_quality_event(self) -> None:
        entries = [{"indicator_id": "bad", "provider": "FRED", "series_id": "BADSERIES", "transform": "level"}]
        with tempfile.TemporaryDirectory() as td:
            db_path = Path(td) / "investment.db"
            with mock.patch(
                "committee.tools.fred_industry_provider.fetch_fred_series_initial_releases",
                side_effect=RuntimeError("boom"),
            ):
                fundamentals_ingest.ingest_catalog(entries, db_path=db_path)
            events = repository.list_data_quality_events(db_path=db_path)
        self.assertTrue(any(e["target"] == "bad" for e in events))

    def test_series_id_not_configured_does_not_spam_data_quality_events(self) -> None:
        entries = [{"indicator_id": "kr_x", "provider": "KOSIS", "series_id": "TBD", "transform": "level"}]
        with tempfile.TemporaryDirectory() as td:
            db_path = Path(td) / "investment.db"
            fundamentals_ingest.ingest_catalog(entries, db_path=db_path)
            events = repository.list_data_quality_events(db_path=db_path)
        self.assertEqual(events, [])


if __name__ == "__main__":
    unittest.main()
