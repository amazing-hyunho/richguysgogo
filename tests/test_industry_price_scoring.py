from __future__ import annotations

import math
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from committee.industry_cycle import price_model_config, price_scoring
from committee.industry_cycle.price_features import WeeklyPriceFeatures


def _features(**overrides) -> WeeklyPriceFeatures:
    defaults = dict(
        asset_id="SOXX",
        market="US",
        benchmark_asset_id="SP500",
        as_of="2026-07-24",
        price_trade_date="2026-07-24",
        price_field_used="adjusted",
        current_price=100.0,
        n_observations=300,
        return_1m=0.02,
        return_3m=0.05,
        return_6m=0.10,
        return_12m=0.20,
        rel_return_3m=0.03,
        rel_return_6m=0.04,
        rel_return_12m=0.06,
        ma20=98.0,
        ma60=95.0,
        ma120=90.0,
        ma200=85.0,
        ma20_gap=100.0 / 98.0 - 1.0,
        ma60_gap=100.0 / 95.0 - 1.0,
        ma120_gap=100.0 / 90.0 - 1.0,
        ma200_gap=100.0 / 85.0 - 1.0,
        drawdown_from_52w_high=-0.05,
        vol_20d=0.015,
        vol_60d=0.02,
        volume_change=0.10,
        below_ma_ratio=0.0,
        data_completeness=1.0,
    )
    defaults.update(overrides)
    return WeeklyPriceFeatures(**defaults)


class ScoreGroupConfigTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = price_model_config.load_price_model_config()


class RelativeStrengthScoreTests(ScoreGroupConfigTests):
    def test_positive_relative_returns_score_above_50(self) -> None:
        result = price_scoring.compute_relative_strength_score(_features(), self.config)
        self.assertIsNotNone(result.score)
        self.assertGreater(result.score, 50.0)

    def test_negative_relative_returns_score_below_50(self) -> None:
        result = price_scoring.compute_relative_strength_score(
            _features(rel_return_3m=-0.03, rel_return_6m=-0.04, rel_return_12m=-0.06), self.config
        )
        self.assertLess(result.score, 50.0)

    def test_score_bounds_within_0_100(self) -> None:
        result = price_scoring.compute_relative_strength_score(
            _features(rel_return_3m=5.0, rel_return_6m=5.0, rel_return_12m=5.0), self.config
        )
        self.assertGreater(result.score, 0.0)
        self.assertLess(result.score, 100.0)

    def test_insufficient_components_yields_none_score_with_reason(self) -> None:
        result = price_scoring.compute_relative_strength_score(
            _features(rel_return_3m=None, rel_return_6m=None, rel_return_12m=None), self.config
        )
        self.assertIsNone(result.score)
        self.assertIn("insufficient_data", result.reason)

    def test_zero_raw_value_is_included_not_treated_as_missing(self) -> None:
        """A genuine 0.0 relative return must contribute to weighted_sum, unlike None."""
        with_zero = price_scoring.compute_relative_strength_score(
            _features(rel_return_3m=0.0, rel_return_6m=0.10, rel_return_12m=0.10), self.config
        )
        without_component = price_scoring.compute_relative_strength_score(
            _features(rel_return_3m=None, rel_return_6m=0.10, rel_return_12m=0.10), self.config
        )
        self.assertIsNotNone(with_zero.score)
        self.assertIsNotNone(without_component.score)
        self.assertNotAlmostEqual(with_zero.score, without_component.score, places=6)
        used_component = next(c for c in with_zero.components if c.key == "rel_return_3m")
        self.assertEqual(used_component.raw_value, 0.0)
        self.assertIsNotNone(used_component.weighted_value)

        missing_component = next(c for c in without_component.components if c.key == "rel_return_3m")
        self.assertIsNone(missing_component.raw_value)
        self.assertIsNone(missing_component.weighted_value)
        self.assertEqual(missing_component.weight, 0.0)


class TrendScoreTests(ScoreGroupConfigTests):
    def test_price_above_all_mas_scores_above_50(self) -> None:
        result = price_scoring.compute_trend_score(_features(), self.config)
        self.assertGreater(result.score, 50.0)

    def test_price_below_all_mas_scores_below_50(self) -> None:
        result = price_scoring.compute_trend_score(
            _features(ma20_gap=-0.05, ma60_gap=-0.08, ma120_gap=-0.1, ma200_gap=-0.12), self.config
        )
        self.assertLess(result.score, 50.0)

    def test_insufficient_mas_yields_none(self) -> None:
        result = price_scoring.compute_trend_score(
            _features(ma20_gap=0.01, ma60_gap=None, ma120_gap=None, ma200_gap=None), self.config
        )
        self.assertIsNone(result.score)


class OverheatScoreTests(ScoreGroupConfigTests):
    def test_strong_short_term_gain_and_volume_surge_scores_high(self) -> None:
        result = price_scoring.compute_overheat_score(
            _features(ma200_gap=0.5, return_1m=0.3, volume_change=0.8), self.config
        )
        self.assertGreater(result.score, 70.0)

    def test_flat_market_scores_near_50(self) -> None:
        result = price_scoring.compute_overheat_score(
            _features(ma200_gap=0.0, return_1m=0.0, volume_change=0.0), self.config
        )
        self.assertAlmostEqual(result.score, 50.0, places=3)


class PriceRiskScoreTests(ScoreGroupConfigTests):
    def test_big_drawdown_and_high_volatility_scores_high(self) -> None:
        result = price_scoring.compute_price_risk_score(
            _features(drawdown_from_52w_high=-0.35, vol_60d=0.06, below_ma_ratio=1.0), self.config
        )
        self.assertGreater(result.score, 50.0)

    def test_no_drawdown_and_low_volatility_scores_low(self) -> None:
        result = price_scoring.compute_price_risk_score(
            _features(drawdown_from_52w_high=0.0, vol_60d=0.0, below_ma_ratio=0.0), self.config
        )
        self.assertLess(result.score, 50.0)

    def test_drawdown_severity_flips_sign_of_input(self) -> None:
        result = price_scoring.compute_price_risk_score(
            _features(drawdown_from_52w_high=-0.20, vol_60d=0.02, below_ma_ratio=0.5), self.config
        )
        component = next(c for c in result.components if c.key == "drawdown_severity")
        self.assertAlmostEqual(component.raw_value, 0.20)


class PriceScoreBundleTests(ScoreGroupConfigTests):
    def test_bundle_computes_all_four_scores(self) -> None:
        bundle = price_scoring.compute_price_score_bundle(_features(), self.config)
        self.assertIsNotNone(bundle.relative_strength.score)
        self.assertIsNotNone(bundle.trend.score)
        self.assertIsNotNone(bundle.overheat.score)
        self.assertIsNotNone(bundle.price_risk.score)

    def test_bundle_to_dict_round_trips_component_breakdown(self) -> None:
        bundle = price_scoring.compute_price_score_bundle(_features(), self.config)
        d = bundle.to_dict()
        self.assertIn("components", d["relative_strength"])
        self.assertTrue(len(d["relative_strength"]["components"]) > 0)


if __name__ == "__main__":
    unittest.main()
