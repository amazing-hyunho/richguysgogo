from __future__ import annotations

import copy
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from committee.industry_cycle import price_model_config


def _valid_payload() -> dict:
    return copy.deepcopy(price_model_config.load_price_model_config_raw())


class LoadRealConfigTests(unittest.TestCase):
    def test_real_config_file_is_valid(self) -> None:
        payload = price_model_config.load_price_model_config()
        self.assertTrue(payload["model_version"])
        self.assertIn("relative_strength", payload["score_weights"])

    def test_list_helpers_do_not_raise(self) -> None:
        payload = price_model_config.load_price_model_config()
        self.assertIsInstance(payload["state_thresholds"], dict)
        self.assertIsInstance(payload["confirmation"], dict)


class ValidationTests(unittest.TestCase):
    def test_valid_payload_has_no_errors(self) -> None:
        self.assertEqual(price_model_config.validate_price_model_config(_valid_payload()), [])

    def test_missing_model_version_is_rejected(self) -> None:
        payload = _valid_payload()
        del payload["model_version"]
        errors = price_model_config.validate_price_model_config(payload)
        self.assertTrue(any("model_version" in e for e in errors))

    def test_missing_return_window_is_rejected(self) -> None:
        payload = _valid_payload()
        del payload["return_windows_trading_days"]["12m"]
        errors = price_model_config.validate_price_model_config(payload)
        self.assertTrue(any("12m" in e for e in errors))

    def test_negative_moving_average_window_is_rejected(self) -> None:
        payload = _valid_payload()
        payload["moving_average_windows"] = [20, -5]
        errors = price_model_config.validate_price_model_config(payload)
        self.assertTrue(any("moving_average_windows" in e for e in errors))

    def test_min_components_exceeding_declared_components_is_rejected(self) -> None:
        payload = _valid_payload()
        payload["score_weights"]["trend"]["min_components"] = 99
        errors = price_model_config.validate_price_model_config(payload)
        self.assertTrue(any("min_components" in e for e in errors))

    def test_missing_state_threshold_key_is_rejected(self) -> None:
        payload = _valid_payload()
        del payload["state_thresholds"]["overheat_score_min"]
        errors = price_model_config.validate_price_model_config(payload)
        self.assertTrue(any("overheat_score_min" in e for e in errors))

    def test_missing_confirmation_key_is_rejected(self) -> None:
        payload = _valid_payload()
        del payload["confirmation"]["weeks_required_recovery"]
        errors = price_model_config.validate_price_model_config(payload)
        self.assertTrue(any("weeks_required_recovery" in e for e in errors))

    def test_out_of_range_min_data_completeness_is_rejected(self) -> None:
        payload = _valid_payload()
        payload["min_data_completeness_for_state"] = 1.5
        errors = price_model_config.validate_price_model_config(payload)
        self.assertTrue(any("min_data_completeness_for_state" in e for e in errors))

    def test_load_raises_on_invalid_payload(self) -> None:
        payload = _valid_payload()
        del payload["model_version"]
        import json
        import tempfile

        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "bad_config.json"
            p.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaises(price_model_config.PriceModelConfigValidationError):
                price_model_config.load_price_model_config(p)


if __name__ == "__main__":
    unittest.main()
