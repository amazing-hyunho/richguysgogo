from __future__ import annotations

from pathlib import Path
import json
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from committee.industry_cycle.indicator_catalog import (
    INDICATOR_CONFIG_PATH,
    IndicatorConfigValidationError,
    list_indicator_ids,
    load_indicator_config,
    load_indicator_config_raw,
    validate_indicator_catalog,
    validate_industry_indicator_mappings,
)


class RealIndicatorConfigTests(unittest.TestCase):
    """The real config/industry_indicators.json must be present and valid."""

    def test_real_config_loads_and_validates(self) -> None:
        self.assertTrue(INDICATOR_CONFIG_PATH.exists())
        payload = load_indicator_config()
        self.assertGreaterEqual(len(payload["indicators"]), 1)
        self.assertIn("industry_indicator_mappings", payload)
        self.assertGreaterEqual(len(payload["industry_indicator_mappings"]), 1)

    def test_real_config_has_no_duplicate_indicator_ids(self) -> None:
        ids = list_indicator_ids()
        self.assertEqual(len(ids), len(set(ids)))

    def test_real_config_mappings_reference_known_indicators(self) -> None:
        payload = load_indicator_config()
        catalog_ids = {e["indicator_id"] for e in payload["indicators"]}
        for mapping in payload["industry_indicator_mappings"]:
            self.assertIn(mapping["indicator_id"], catalog_ids)
            self.assertIn(mapping.get("direction"), {"positive", "negative", None})

    def test_every_active_industry_has_three_current_free_kpi_mappings(self) -> None:
        payload = load_indicator_config()
        taxonomy_payload = json.loads(
            (ROOT / "config" / "industry_taxonomy.json").read_text(encoding="utf-8")
        )
        active_ids = {
            row["industry_id"]
            for row in taxonomy_payload["industries"]
            if row.get("active", True)
        }
        current = [
            row
            for row in payload["industry_indicator_mappings"]
            if row.get("valid_to") is None
        ]
        for industry_id in active_ids:
            self.assertEqual(
                sum(1 for row in current if row["industry_id"] == industry_id),
                3,
                industry_id,
            )


class ValidateIndicatorCatalogTests(unittest.TestCase):
    def test_valid_catalog_has_no_errors(self) -> None:
        payload = {"indicators": [{"indicator_id": "a"}, {"indicator_id": "b"}]}
        self.assertEqual(validate_indicator_catalog(payload), [])

    def test_missing_indicator_id_is_detected(self) -> None:
        payload = {"indicators": [{"provider": "FRED"}]}
        errors = validate_indicator_catalog(payload)
        self.assertTrue(any("indicator_id is required" in e for e in errors))

    def test_duplicate_indicator_id_is_detected(self) -> None:
        payload = {"indicators": [{"indicator_id": "a"}, {"indicator_id": "a"}]}
        errors = validate_indicator_catalog(payload)
        self.assertTrue(any("duplicate indicator_id" in e for e in errors))

    def test_indicators_must_be_a_list(self) -> None:
        errors = validate_indicator_catalog({"indicators": "not-a-list"})
        self.assertTrue(any("must be a list" in e for e in errors))


class ValidateIndustryIndicatorMappingsTests(unittest.TestCase):
    def _valid_mapping(self) -> dict:
        return {
            "industry_id": "semiconductors",
            "indicator_id": "us_ism_pmi",
            "direction": "positive",
            "weight": 0.5,
            "valid_from": "2026-07-25",
            "valid_to": None,
        }

    def test_valid_mapping_has_no_errors(self) -> None:
        payload = {"industry_indicator_mappings": [self._valid_mapping()]}
        self.assertEqual(validate_industry_indicator_mappings(payload), [])

    def test_missing_industry_id_is_detected(self) -> None:
        entry = self._valid_mapping()
        del entry["industry_id"]
        errors = validate_industry_indicator_mappings({"industry_indicator_mappings": [entry]})
        self.assertTrue(any("industry_id is required" in e for e in errors))

    def test_missing_indicator_id_is_detected(self) -> None:
        entry = self._valid_mapping()
        del entry["indicator_id"]
        errors = validate_industry_indicator_mappings({"industry_indicator_mappings": [entry]})
        self.assertTrue(any("indicator_id is required" in e for e in errors))

    def test_invalid_direction_is_detected(self) -> None:
        entry = self._valid_mapping()
        entry["direction"] = "sideways"
        errors = validate_industry_indicator_mappings({"industry_indicator_mappings": [entry]})
        self.assertTrue(any("direction must be one of" in e for e in errors))

    def test_non_numeric_weight_is_detected(self) -> None:
        entry = self._valid_mapping()
        entry["weight"] = "half"
        errors = validate_industry_indicator_mappings({"industry_indicator_mappings": [entry]})
        self.assertTrue(any("weight must be numeric" in e for e in errors))

    def test_duplicate_mapping_is_detected(self) -> None:
        payload = {"industry_indicator_mappings": [self._valid_mapping(), self._valid_mapping()]}
        errors = validate_industry_indicator_mappings(payload)
        self.assertTrue(any("duplicate mapping" in e for e in errors))

    def test_unknown_industry_id_is_detected_when_known_ids_given(self) -> None:
        payload = {"industry_indicator_mappings": [self._valid_mapping()]}
        errors = validate_industry_indicator_mappings(payload, known_industry_ids={"banks"})
        self.assertTrue(any("unknown industry_id" in e for e in errors))

    def test_unknown_indicator_id_is_detected_when_known_ids_given(self) -> None:
        payload = {"industry_indicator_mappings": [self._valid_mapping()]}
        errors = validate_industry_indicator_mappings(payload, known_indicator_ids={"other_indicator"})
        self.assertTrue(any("unknown indicator_id" in e for e in errors))

    def test_mappings_must_be_a_list(self) -> None:
        errors = validate_industry_indicator_mappings({"industry_indicator_mappings": "nope"})
        self.assertTrue(any("must be a list" in e for e in errors))


class LoadIndicatorConfigTests(unittest.TestCase):
    def test_load_raises_on_invalid_catalog(self) -> None:
        import json
        import tempfile

        with tempfile.TemporaryDirectory() as td:
            bad_path = Path(td) / "bad_indicators.json"
            bad_path.write_text(
                json.dumps({"indicators": [{"provider": "FRED"}]}), encoding="utf-8"
            )
            with self.assertRaises(IndicatorConfigValidationError):
                load_indicator_config(bad_path)

    def test_load_raises_on_mapping_referencing_unknown_indicator(self) -> None:
        import json
        import tempfile

        with tempfile.TemporaryDirectory() as td:
            bad_path = Path(td) / "bad_indicators.json"
            bad_path.write_text(
                json.dumps(
                    {
                        "indicators": [{"indicator_id": "us_ism_pmi"}],
                        "industry_indicator_mappings": [
                            {"industry_id": "semiconductors", "indicator_id": "does_not_exist"}
                        ],
                    }
                ),
                encoding="utf-8",
            )
            with self.assertRaises(IndicatorConfigValidationError):
                load_indicator_config(bad_path)

    def test_load_raw_missing_file_raises(self) -> None:
        with self.assertRaises(FileNotFoundError):
            load_indicator_config_raw(Path("does/not/exist.json"))


if __name__ == "__main__":
    unittest.main()
