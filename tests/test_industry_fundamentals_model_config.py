from __future__ import annotations

from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from committee.industry_cycle import fundamentals_model_config as fmc


def _valid_payload(**overrides):
    payload = {
        "model_version": "fundamentals_only_v1",
        "scale_k": 4.0,
        "min_components": 2,
        "staleness_max_periods_by_frequency": {"monthly": 3, "quarterly": 2},
        "min_data_completeness_for_score": 0.34,
        "min_non_price_evidence_count_for_recovery_candidate": 2,
    }
    payload.update(overrides)
    return payload


class ValidationTests(unittest.TestCase):
    def test_valid_payload_has_no_errors(self) -> None:
        self.assertEqual(fmc.validate_fundamentals_model_config(_valid_payload()), [])

    def test_missing_model_version_is_rejected(self) -> None:
        payload = _valid_payload()
        del payload["model_version"]
        errors = fmc.validate_fundamentals_model_config(payload)
        self.assertTrue(any("model_version" in e for e in errors))

    def test_non_positive_scale_k_is_rejected(self) -> None:
        errors = fmc.validate_fundamentals_model_config(_valid_payload(scale_k=0))
        self.assertTrue(any("scale_k" in e for e in errors))

    def test_non_positive_min_components_is_rejected(self) -> None:
        errors = fmc.validate_fundamentals_model_config(_valid_payload(min_components=0))
        self.assertTrue(any("min_components" in e for e in errors))

    def test_unknown_staleness_frequency_is_rejected(self) -> None:
        errors = fmc.validate_fundamentals_model_config(
            _valid_payload(staleness_max_periods_by_frequency={"bogus_freq": 3})
        )
        self.assertTrue(any("staleness_max_periods_by_frequency" in e for e in errors))

    def test_non_positive_staleness_value_is_rejected(self) -> None:
        errors = fmc.validate_fundamentals_model_config(
            _valid_payload(staleness_max_periods_by_frequency={"monthly": 0})
        )
        self.assertTrue(any("staleness_max_periods_by_frequency" in e for e in errors))

    def test_out_of_range_min_data_completeness_is_rejected(self) -> None:
        errors = fmc.validate_fundamentals_model_config(_valid_payload(min_data_completeness_for_score=1.5))
        self.assertTrue(any("min_data_completeness_for_score" in e for e in errors))

    def test_negative_min_evidence_count_is_rejected(self) -> None:
        errors = fmc.validate_fundamentals_model_config(
            _valid_payload(min_non_price_evidence_count_for_recovery_candidate=-1)
        )
        self.assertTrue(any("min_non_price_evidence_count_for_recovery_candidate" in e for e in errors))

    def test_load_raises_on_invalid_payload(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            bad_path = Path(td) / "bad.json"
            bad_path.write_text('{"model_version": ""}', encoding="utf-8")
            with self.assertRaises(fmc.FundamentalsModelConfigValidationError):
                fmc.load_fundamentals_model_config(bad_path)


class LoadRealConfigTests(unittest.TestCase):
    def test_real_config_file_is_valid(self) -> None:
        payload = fmc.load_fundamentals_model_config()
        self.assertTrue(payload["model_version"])


if __name__ == "__main__":
    unittest.main()
