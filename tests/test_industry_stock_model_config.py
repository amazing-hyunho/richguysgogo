from __future__ import annotations

import copy
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from committee.industry_cycle import stock_model_config as smc


def _score_group(**overrides):
    group = {
        "scale_k": 4.0,
        "min_components": 1,
        "components": {"a": 0.5, "b": 0.5},
    }
    group.update(overrides)
    return group


def _valid_payload(**overrides):
    payload = {
        "model_version": "stock_candidate_v1",
        "earnings_quality": _score_group(),
        "estimate_revision": _score_group(),
        "relative_strength": _score_group(),
        "financial_health": _score_group(),
        "liquidity": _score_group(),
        "stock_score": _score_group(
            components={"earnings_quality": 0.3, "estimate_revision": 0.25, "relative_strength": 0.2,
                        "financial_health": 0.15, "liquidity": 0.1},
            min_components=2,
            baselines={"earnings_quality": 50.0},
        ),
        "risk_penalty": {
            "high_debt_ratio_threshold": 3.0,
            "high_debt_ratio_points": 8.0,
            "sustained_loss_points": 12.0,
            "excessive_short_term_surge_points": 10.0,
            "max_total_points": 30.0,
        },
        "exclusion": {
            "min_data_completeness_for_score": 0.34,
            "sustained_loss_periods": 2,
            "excessive_short_term_surge_pct_3m": 0.6,
            "min_history_periods_financial": 2,
            "min_history_snapshots_consensus": 5,
            "min_liquidity_percentile": 0.10,
            "min_listing_days_stock": 180,
        },
        "industry_earnings_revision": _score_group(),
        "industry_breadth": _score_group(),
        "etf_quality": {
            "min_aum_usd_equivalent": 50_000_000,
            "max_expense_ratio": 0.0075,
            "max_spread_bp": 50,
            "exclude_leveraged_inverse": True,
            "min_listing_days": 180,
            "min_industry_purity_pct": 0.5,
        },
        "consensus_revision_lookback_days": 60,
    }
    payload.update(overrides)
    return payload


class ValidationTests(unittest.TestCase):
    def test_valid_payload_has_no_errors(self) -> None:
        self.assertEqual(smc.validate_stock_model_config(_valid_payload()), [])

    def test_missing_model_version_is_rejected(self) -> None:
        payload = _valid_payload()
        del payload["model_version"]
        errors = smc.validate_stock_model_config(payload)
        self.assertTrue(any("model_version" in e for e in errors))

    def test_missing_score_group_is_rejected(self) -> None:
        payload = _valid_payload()
        del payload["relative_strength"]
        errors = smc.validate_stock_model_config(payload)
        self.assertTrue(any("relative_strength" in e for e in errors))

    def test_non_positive_scale_k_is_rejected(self) -> None:
        payload = _valid_payload()
        payload["earnings_quality"] = _score_group(scale_k=0)
        errors = smc.validate_stock_model_config(payload)
        self.assertTrue(any("earnings_quality.scale_k" in e for e in errors))

    def test_min_components_exceeding_component_count_is_rejected(self) -> None:
        payload = _valid_payload()
        payload["liquidity"] = _score_group(min_components=5, components={"a": 1.0})
        errors = smc.validate_stock_model_config(payload)
        self.assertTrue(any("liquidity.min_components" in e for e in errors))

    def test_unknown_baseline_key_is_rejected(self) -> None:
        payload = _valid_payload()
        payload["financial_health"] = _score_group(baselines={"unknown_key": 1.0})
        errors = smc.validate_stock_model_config(payload)
        self.assertTrue(any("financial_health.baselines" in e for e in errors))

    def test_missing_risk_penalty_key_is_rejected(self) -> None:
        payload = _valid_payload()
        del payload["risk_penalty"]["max_total_points"]
        errors = smc.validate_stock_model_config(payload)
        self.assertTrue(any("risk_penalty.max_total_points" in e for e in errors))

    def test_out_of_range_completeness_is_rejected(self) -> None:
        payload = _valid_payload()
        payload["exclusion"]["min_data_completeness_for_score"] = 1.5
        errors = smc.validate_stock_model_config(payload)
        self.assertTrue(any("min_data_completeness_for_score" in e for e in errors))

    def test_etf_quality_bad_boolean_is_rejected(self) -> None:
        payload = _valid_payload()
        payload["etf_quality"]["exclude_leveraged_inverse"] = "yes"
        errors = smc.validate_stock_model_config(payload)
        self.assertTrue(any("exclude_leveraged_inverse" in e for e in errors))

    def test_negative_lookback_days_is_rejected(self) -> None:
        payload = _valid_payload(consensus_revision_lookback_days=-5)
        errors = smc.validate_stock_model_config(payload)
        self.assertTrue(any("consensus_revision_lookback_days" in e for e in errors))

    def test_load_raises_on_invalid_payload(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            bad_path = Path(td) / "bad.json"
            bad_path.write_text('{"model_version": ""}', encoding="utf-8")
            with self.assertRaises(smc.StockModelConfigValidationError):
                smc.load_stock_model_config(bad_path)

    def test_deepcopy_payload_still_valid(self) -> None:
        payload = copy.deepcopy(_valid_payload())
        self.assertEqual(smc.validate_stock_model_config(payload), [])


class LoadRealConfigTests(unittest.TestCase):
    def test_real_config_file_is_valid(self) -> None:
        payload = smc.load_stock_model_config()
        self.assertTrue(payload["model_version"])


if __name__ == "__main__":
    unittest.main()
