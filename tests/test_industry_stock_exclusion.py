from __future__ import annotations

from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from committee.industry_cycle import stock_exclusion as se
from committee.industry_cycle.stock_model_config import load_stock_model_config


class ExclusionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = load_stock_model_config()

    def test_clean_stock_passes(self) -> None:
        inputs = se.ExclusionCheckInputs(
            capital_impaired=False,
            sustained_loss_periods=0,
            fcf_margin=0.1,
            return_3m=0.05,
            data_completeness=0.8,
            liquidity_percentile=0.5,
            listing_days=1000,
            trading_halted=False,
            administrative_issue=False,
        )
        result = se.evaluate_exclusions(inputs, self.config)
        self.assertFalse(result.excluded)
        self.assertEqual(result.reasons, [])
        self.assertEqual(result.unknown_checks, [])

    def test_capital_impairment_excludes(self) -> None:
        inputs = se.ExclusionCheckInputs(capital_impaired=True)
        result = se.evaluate_exclusions(inputs, self.config)
        self.assertTrue(result.excluded)
        self.assertTrue(any("capital_impairment" in r for r in result.reasons))

    def test_sustained_loss_with_negative_cashflow_excludes(self) -> None:
        inputs = se.ExclusionCheckInputs(sustained_loss_periods=3, fcf_margin=-0.05)
        result = se.evaluate_exclusions(inputs, self.config)
        self.assertTrue(result.excluded)
        self.assertTrue(any("sustained_losses_with_negative_cashflow" in r for r in result.reasons))

    def test_sustained_loss_with_positive_cashflow_does_not_exclude(self) -> None:
        inputs = se.ExclusionCheckInputs(sustained_loss_periods=3, fcf_margin=0.05)
        result = se.evaluate_exclusions(inputs, self.config)
        self.assertFalse(result.excluded)

    def test_sustained_loss_below_threshold_does_not_exclude(self) -> None:
        inputs = se.ExclusionCheckInputs(sustained_loss_periods=1, fcf_margin=-0.05)
        result = se.evaluate_exclusions(inputs, self.config)
        self.assertFalse(result.excluded)

    def test_excessive_short_term_surge_excludes(self) -> None:
        inputs = se.ExclusionCheckInputs(return_3m=0.9)
        result = se.evaluate_exclusions(inputs, self.config)
        self.assertTrue(result.excluded)
        self.assertTrue(any("excessive_short_term_surge" in r for r in result.reasons))

    def test_moderate_return_does_not_exclude(self) -> None:
        inputs = se.ExclusionCheckInputs(return_3m=0.2)
        result = se.evaluate_exclusions(inputs, self.config)
        self.assertFalse(result.excluded)

    def test_insufficient_data_completeness_excludes(self) -> None:
        inputs = se.ExclusionCheckInputs(data_completeness=0.1)
        result = se.evaluate_exclusions(inputs, self.config)
        self.assertTrue(result.excluded)
        self.assertTrue(any("insufficient_data_completeness" in r for r in result.reasons))

    def test_low_liquidity_percentile_excludes(self) -> None:
        inputs = se.ExclusionCheckInputs(liquidity_percentile=0.02)
        result = se.evaluate_exclusions(inputs, self.config)
        self.assertTrue(result.excluded)
        self.assertTrue(any("low_liquidity_percentile" in r for r in result.reasons))

    def test_insufficient_listing_history_excludes(self) -> None:
        inputs = se.ExclusionCheckInputs(listing_days=30)
        result = se.evaluate_exclusions(inputs, self.config)
        self.assertTrue(result.excluded)
        self.assertTrue(any("insufficient_listing_history" in r for r in result.reasons))

    def test_trading_halted_excludes(self) -> None:
        inputs = se.ExclusionCheckInputs(trading_halted=True)
        result = se.evaluate_exclusions(inputs, self.config)
        self.assertTrue(result.excluded)
        self.assertIn("trading_halted_or_delisting_risk", result.reasons)

    def test_administrative_issue_excludes(self) -> None:
        inputs = se.ExclusionCheckInputs(administrative_issue=True)
        result = se.evaluate_exclusions(inputs, self.config)
        self.assertTrue(result.excluded)
        self.assertIn("administrative_issue_designation", result.reasons)

    def test_all_unknown_inputs_never_auto_excludes(self) -> None:
        inputs = se.ExclusionCheckInputs()
        result = se.evaluate_exclusions(inputs, self.config)
        self.assertFalse(result.excluded)
        self.assertGreater(len(result.unknown_checks), 0)

    def test_multiple_reasons_all_reported_not_truncated(self) -> None:
        inputs = se.ExclusionCheckInputs(
            capital_impaired=True,
            trading_halted=True,
            return_3m=0.99,
        )
        result = se.evaluate_exclusions(inputs, self.config)
        self.assertGreaterEqual(len(result.reasons), 3)


if __name__ == "__main__":
    unittest.main()
