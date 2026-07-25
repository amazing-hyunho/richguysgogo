from __future__ import annotations

"""Shared 0~100 weighted-logistic scoring primitive.

Used by both `price_scoring.py` (Phase 1-B, price-only sub-scores) and
`fundamentals_scoring.py` (Phase 2, `fundamentals_score`). Extracted here so
the explainability contract -- missing components excluded + weights
renormalized, optional baseline-centering, `min_components` gating to `None`
-- is defined exactly once and both phases stay behaviorally identical
without copy-paste drift.

Design (see `price_scoring.py` module docstring for the original rationale):
- `weighted_sum -> logistic(scale_k * weighted_sum) * 100`, always in (0, 100).
- Missing (`None`) components are excluded from the weighted sum; remaining
  components' weights are renormalized to sum to 1 (design doc section 7.1:
  "데이터가 없는 항목은 0점 처리하지 않고, 사용 가능한 항목의 가중치를 다시
  합이 1이 되도록 정규화한다"). A real `0.0` raw value is a normal, included
  input, never confused with a missing one.
- Optional per-component `baselines` are subtracted from the raw value
  before weighting, so components whose "neutral" value isn't naturally 0
  (e.g. ISM PMI's neutral is 50, not 0) can still push the score below 50
  when below baseline.
- If fewer than `min_components` are available, the score is `None` entirely.
"""

import math
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class ScoreComponent:
    """One component's contribution to a score: raw value, normalized weight, weighted value."""

    key: str
    raw_value: Optional[float]
    weight: float
    weighted_value: Optional[float]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "key": self.key,
            "raw_value": self.raw_value,
            "weight": self.weight,
            "weighted_value": self.weighted_value,
        }


@dataclass(frozen=True)
class ScoreResult:
    """One 0~100 score plus its full component breakdown (or `None` + reason)."""

    score: Optional[float]
    components: List[ScoreComponent] = field(default_factory=list)
    weighted_sum: Optional[float] = None
    reason: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "score": self.score,
            "weighted_sum": self.weighted_sum,
            "reason": self.reason,
            "components": [c.to_dict() for c in self.components],
        }


def weighted_logistic_score(
    raw_components: Dict[str, Optional[float]],
    group_config: Dict[str, Any],
) -> ScoreResult:
    """Compute one 0~100 score from named raw components + a weights/scale config.

    `group_config` keys: `components` (dict[name, weight]), `scale_k` (float),
    `min_components` (int), optional `baselines` (dict[name, float]).
    """
    weight_cfg: Dict[str, float] = group_config["components"]
    scale_k: float = float(group_config["scale_k"])
    min_components: int = int(group_config["min_components"])
    baselines: Dict[str, float] = group_config.get("baselines") or {}

    available = {k: v for k, v in raw_components.items() if v is not None and k in weight_cfg}

    if len(available) < min_components:
        components = [
            ScoreComponent(key=k, raw_value=raw_components.get(k), weight=0.0, weighted_value=None)
            for k in weight_cfg
        ]
        return ScoreResult(
            score=None,
            components=components,
            weighted_sum=None,
            reason=(
                f"insufficient_data: {len(available)}/{min_components} required "
                f"components available (of {len(weight_cfg)} declared)"
            ),
        )

    total_weight = sum(weight_cfg[k] for k in available)
    components = []
    weighted_sum = 0.0
    for k in weight_cfg:
        v = raw_components.get(k)
        if k not in available or total_weight == 0:
            components.append(ScoreComponent(key=k, raw_value=v, weight=0.0, weighted_value=None))
            continue
        centered_v = v - baselines.get(k, 0.0)
        w_norm = weight_cfg[k] / total_weight
        weighted_value = centered_v * w_norm
        weighted_sum += weighted_value
        components.append(ScoreComponent(key=k, raw_value=v, weight=w_norm, weighted_value=weighted_value))

    score = 100.0 / (1.0 + math.exp(-scale_k * weighted_sum))
    return ScoreResult(score=score, components=components, weighted_sum=weighted_sum, reason=None)
