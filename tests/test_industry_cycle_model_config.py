from __future__ import annotations

import copy
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from committee.industry_cycle import cycle_model_config as cmc


def _valid_payload() -> dict:
    return json.loads(json.dumps(cmc.load_cycle_model_config_raw()))


class CycleModelConfigTests(unittest.TestCase):
    def test_shipped_config_loads_and_validates(self) -> None:
        cfg = cmc.load_cycle_model_config()
        self.assertEqual(cfg["model_version"], "cycle_v1")
        self.assertIn("flow_score", cfg["cycle_score"]["components"])
        self.assertIn("macro_fit_score", cfg["cycle_score"]["components"])

    def test_missing_model_version_is_rejected(self) -> None:
        payload = _valid_payload()
        del payload["model_version"]
        errors = cmc.validate_cycle_model_config(payload)
        self.assertTrue(any("model_version" in e for e in errors))

    def test_missing_cycle_score_group_is_rejected(self) -> None:
        payload = _valid_payload()
        del payload["cycle_score"]
        errors = cmc.validate_cycle_model_config(payload)
        self.assertTrue(any("cycle_score" in e for e in errors))

    def test_min_components_exceeding_declared_components_is_rejected(self) -> None:
        payload = _valid_payload()
        payload["cycle_score"]["min_components"] = 999
        errors = cmc.validate_cycle_model_config(payload)
        self.assertTrue(any("min_components" in e for e in errors))

    def test_confidence_fraction_out_of_range_is_rejected(self) -> None:
        payload = _valid_payload()
        payload["confidence"]["unknown_history_reliability_default"] = 1.5
        errors = cmc.validate_cycle_model_config(payload)
        self.assertTrue(any("unknown_history_reliability_default" in e for e in errors))

    def test_missing_state_threshold_key_is_rejected(self) -> None:
        payload = _valid_payload()
        del payload["state_thresholds"]["recovery_cycle_score_min"]
        errors = cmc.validate_cycle_model_config(payload)
        self.assertTrue(any("recovery_cycle_score_min" in e for e in errors))

    def test_missing_urgent_alert_key_is_rejected(self) -> None:
        payload = _valid_payload()
        del payload["urgent_alert"]["earnings_shock_score_drop_min"]
        errors = cmc.validate_cycle_model_config(payload)
        self.assertTrue(any("earnings_shock_score_drop_min" in e for e in errors))

    def test_unknown_baseline_key_is_rejected(self) -> None:
        payload = _valid_payload()
        payload["cycle_score"]["baselines"]["not_a_real_component"] = 10.0
        errors = cmc.validate_cycle_model_config(payload)
        self.assertTrue(any("unknown key" in e for e in errors))


if __name__ == "__main__":
    unittest.main()
