from __future__ import annotations

"""Phase 1-B: price-only sub-score computation (pure, no DB/network access).

Computes the four 0~100 price-only scores from the task spec:
`relative_strength_score`, `trend_score`, `overheat_score`, `price_risk_score`.

Design:
- Every score is `weighted_sum -> logistic(scale_k * weighted_sum) * 100`.
  This keeps the score always within (0, 100), monotonic in its inputs, and
  fully explainable (each component's raw value / normalized weight /
  weighted contribution is returned alongside the score).
- Missing (`None`) components are excluded from the weighted sum and the
  remaining components' weights are renormalized to sum to 1 -- mirroring
  the design doc's fundamentals_score policy (section 7.1: "데이터가 없는
  항목은 0점 처리하지 않고, 사용 가능한 항목의 가중치를 다시 합이 1이 되도록
  정규화한다"). A real `0.0` raw value is a normal, included input; it is
  never confused with a missing one.
- Optional per-component `baselines` (from config) are subtracted from the
  raw value before weighting: `relative_strength`/`trend`/`overheat`'s raw
  inputs (returns, MA gaps) are already naturally centered at 0 (no
  drawdown/deviation == 0), but `price_risk`'s raw inputs
  (`drawdown_severity`, `vol_60d`, `below_ma_ratio`) are all >= 0 by
  construction, so WITHOUT a baseline the weighted sum could never go
  negative and the score could never signal "below-average risk" (it would
  be stuck at >= 50). The configured baseline is what "typical/neutral"
  looks like for that component, so a below-baseline value correctly pulls
  the score under 50.
- If fewer than `min_components` (from config) are available, the score is
  `None` entirely (task item 2: "데이터 부족 시 0점으로 처리하지 말고 NULL
  또는 판정 보류").

Scale caveat (documented, not hidden): `price_risk`'s components have very
different natural magnitudes (drawdown/below_ma_ratio are O(0.1-1),
vol_60d is O(0.01-0.05)). This module does not attempt statistical
normalization across components -- the config's per-component weight is the
single tuning knob that also compensates for scale differences. This is an
explicit, documented simplification of a rule-based v1 model, not a
precision-calibrated one; retuning happens by editing
`config/industry_cycle_price_model.json` (and bumping `model_version`),
never by editing this code.
"""

from dataclasses import dataclass
from typing import Any, Dict

from committee.industry_cycle.price_features import WeeklyPriceFeatures
from committee.industry_cycle.scoring_common import ScoreComponent, ScoreResult, weighted_logistic_score

__all__ = [
    "ScoreComponent",
    "ScoreResult",
    "PriceScoreBundle",
    "compute_relative_strength_score",
    "compute_trend_score",
    "compute_overheat_score",
    "compute_price_risk_score",
    "compute_price_score_bundle",
]


@dataclass(frozen=True)
class PriceScoreBundle:
    relative_strength: ScoreResult
    trend: ScoreResult
    overheat: ScoreResult
    price_risk: ScoreResult

    def to_dict(self) -> Dict[str, Any]:
        return {
            "relative_strength": self.relative_strength.to_dict(),
            "trend": self.trend.to_dict(),
            "overheat": self.overheat.to_dict(),
            "price_risk": self.price_risk.to_dict(),
        }


def compute_relative_strength_score(features: WeeklyPriceFeatures, model_config: Dict[str, Any]) -> ScoreResult:
    raw = {
        "rel_return_3m": features.rel_return_3m,
        "rel_return_6m": features.rel_return_6m,
        "rel_return_12m": features.rel_return_12m,
    }
    return weighted_logistic_score(raw, model_config["score_weights"]["relative_strength"])


def compute_trend_score(features: WeeklyPriceFeatures, model_config: Dict[str, Any]) -> ScoreResult:
    raw = {
        "ma20_gap": features.ma20_gap,
        "ma60_gap": features.ma60_gap,
        "ma120_gap": features.ma120_gap,
        "ma200_gap": features.ma200_gap,
    }
    return weighted_logistic_score(raw, model_config["score_weights"]["trend"])


def compute_overheat_score(features: WeeklyPriceFeatures, model_config: Dict[str, Any]) -> ScoreResult:
    raw = {
        "ma200_gap": features.ma200_gap,
        "return_1m": features.return_1m,
        "volume_change": features.volume_change,
    }
    return weighted_logistic_score(raw, model_config["score_weights"]["overheat"])


def compute_price_risk_score(features: WeeklyPriceFeatures, model_config: Dict[str, Any]) -> ScoreResult:
    drawdown_severity = None if features.drawdown_from_52w_high is None else -features.drawdown_from_52w_high
    raw = {
        "drawdown_severity": drawdown_severity,
        "vol_60d": features.vol_60d,
        "below_ma_ratio": features.below_ma_ratio,
    }
    return weighted_logistic_score(raw, model_config["score_weights"]["price_risk"])


def compute_price_score_bundle(features: WeeklyPriceFeatures, model_config: Dict[str, Any]) -> PriceScoreBundle:
    return PriceScoreBundle(
        relative_strength=compute_relative_strength_score(features, model_config),
        trend=compute_trend_score(features, model_config),
        overheat=compute_overheat_score(features, model_config),
        price_risk=compute_price_risk_score(features, model_config),
    )
