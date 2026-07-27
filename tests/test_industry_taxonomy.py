from __future__ import annotations

from pathlib import Path
import json
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from committee.industry_cycle.taxonomy import (
    TAXONOMY_PATH,
    TaxonomyValidationError,
    list_industry_ids,
    load_taxonomy,
    load_taxonomy_raw,
    validate_taxonomy,
)


class IndustryTaxonomyConfigTests(unittest.TestCase):
    """The real config/industry_taxonomy.json must be present and valid."""

    def test_real_config_loads_and_validates(self) -> None:
        self.assertTrue(TAXONOMY_PATH.exists())
        payload = load_taxonomy()
        self.assertGreaterEqual(len(payload["industries"]), 20)

    def test_real_config_has_no_duplicate_ids(self) -> None:
        ids = list_industry_ids()
        self.assertEqual(len(ids), len(set(ids)))

    def test_real_config_entries_have_names_and_valid_coverage_status(self) -> None:
        payload = load_taxonomy()
        for entry in payload["industries"]:
            self.assertTrue(entry["name_kr"])
            self.assertTrue(entry["country_scope"])
            self.assertIn(entry.get("coverage_status"), {"OK", "INSUFFICIENT", None})

    def test_exactly_25_industries_are_active_and_have_one_to_three_stocks(self) -> None:
        payload = load_taxonomy()
        active_ids = {
            entry["industry_id"]
            for entry in payload["industries"]
            if entry.get("active", True)
        }
        self.assertEqual(len(active_ids), 25)

        assets = json.loads((ROOT / "config" / "industry_etfs.json").read_text(encoding="utf-8"))
        current_stocks = [
            row
            for row in assets["mappings"]
            if row.get("asset_type") == "STOCK"
            and row.get("valid_to") is None
            and row["industry_id"] in active_ids
        ]
        for industry_id in active_ids:
            count = sum(1 for row in current_stocks if row["industry_id"] == industry_id)
            self.assertGreaterEqual(count, 1, industry_id)
            self.assertLessEqual(count, 3, industry_id)


class IndustryTaxonomyValidationTests(unittest.TestCase):
    def _valid_entry(self, industry_id: str = "semiconductors") -> dict:
        return {
            "industry_id": industry_id,
            "name_kr": "반도체",
            "name_en": "Semiconductors",
            "country_scope": ["KR", "US"],
            "active": True,
            "coverage_status": "INSUFFICIENT",
            "aliases": [],
        }

    def test_valid_payload_has_no_errors(self) -> None:
        payload = {"industries": [self._valid_entry()]}
        self.assertEqual(validate_taxonomy(payload), [])

    def test_empty_industries_is_invalid(self) -> None:
        errors = validate_taxonomy({"industries": []})
        self.assertTrue(any("non-empty" in e for e in errors))

    def test_duplicate_industry_id_is_detected(self) -> None:
        payload = {"industries": [self._valid_entry("semiconductors"), self._valid_entry("semiconductors")]}
        errors = validate_taxonomy(payload)
        self.assertTrue(any("duplicate industry_id" in e for e in errors))

    def test_missing_name_kr_is_detected(self) -> None:
        entry = self._valid_entry()
        del entry["name_kr"]
        errors = validate_taxonomy({"industries": [entry]})
        self.assertTrue(any("name_kr is required" in e for e in errors))

    def test_invalid_country_scope_value_is_detected(self) -> None:
        entry = self._valid_entry()
        entry["country_scope"] = ["JP"]
        errors = validate_taxonomy({"industries": [entry]})
        self.assertTrue(any("unsupported country_scope" in e for e in errors))

    def test_empty_country_scope_is_detected(self) -> None:
        entry = self._valid_entry()
        entry["country_scope"] = []
        errors = validate_taxonomy({"industries": [entry]})
        self.assertTrue(any("country_scope must be a non-empty list" in e for e in errors))

    def test_invalid_coverage_status_is_detected(self) -> None:
        entry = self._valid_entry()
        entry["coverage_status"] = "MAYBE"
        errors = validate_taxonomy({"industries": [entry]})
        self.assertTrue(any("coverage_status must be one of" in e for e in errors))

    def test_alias_missing_external_code_is_detected(self) -> None:
        entry = self._valid_entry()
        entry["aliases"] = [{"provider": "GICS"}]
        errors = validate_taxonomy({"industries": [entry]})
        self.assertTrue(any("external_code is required" in e for e in errors))

    def test_load_taxonomy_raises_on_invalid_payload(self) -> None:
        import json
        import tempfile

        with tempfile.TemporaryDirectory() as td:
            bad_path = Path(td) / "bad_taxonomy.json"
            bad_path.write_text(json.dumps({"industries": []}), encoding="utf-8")
            with self.assertRaises(TaxonomyValidationError):
                load_taxonomy(bad_path)

    def test_load_taxonomy_raw_missing_file_raises(self) -> None:
        with self.assertRaises(FileNotFoundError):
            load_taxonomy_raw(Path("does/not/exist.json"))


if __name__ == "__main__":
    unittest.main()
