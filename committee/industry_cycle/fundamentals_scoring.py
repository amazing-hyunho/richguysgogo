from __future__ import annotations

"""Phase 2: `fundamentals_score` computation (pure, DB reads only, no writes/network).

Computes one 0~100 `fundamentals_score` per `(industry_id, as_of)` from the
industry's mapped indicators (`industry_indicator_map`) and their
point-in-time-safe observations (`indicator_observation`, gated via
`committee.industry_cycle.repository.get_observations_as_of` --
`known_at <= as_of`, so this can never leak future knowledge into a past
signal). Reuses `committee.industry_cycle.scoring_common.weighted_logistic_score`
for the same explainable weighted-sum -> logistic(...)*100 contract Phase 1-B
uses for price scores (design doc section 7.1's fundamentals_score policy:
missing indicators are excluded and remaining weights renormalized, never
zero-filled).

Per-indicator standardization
------------------------------
Unlike price features (already naturally centered at 0: a return of 0% or an
MA gap of 0 is neutral), raw fundamentals values have heterogeneous natural
scales and directions (PMI's neutral is 50, not 0; a rising inventory level
can be bearish depending on the indicator). Each `indicator_catalog` entry
may carry an optional `baseline` (config/industry_indicators.json's
`indicators` list; defaults to 0.0 when absent -- correct for already
zero-centered transforms like yoy_pct/mom_pct) representing that indicator's
neutral/typical raw value -- a property of the SERIES itself (its unit),
not of any one industry's mapping to it. Each `industry_indicator_map`
mapping separately carries the required `direction` ('positive'/'negative')
for THAT industry. Standardization is:

    standardized = (raw_value - baseline) * (+1 if direction=='positive' else -1)

...applied BEFORE calling `weighted_logistic_score` (which then only weights
+ renormalizes + squashes; no further baseline centering happens there).

Staleness / delay penalty
--------------------------
An observation older than `staleness_max_periods_by_frequency[frequency]`
whole periods (from `config/industry_cycle_fundamentals_model.json`) relative
to `as_of` is treated as effectively missing (excluded, weight renormalized
away) rather than included with a stale value -- this is the "데이터 완전성과
지연 패널티" requirement (design doc section 12, Phase 2 item 5). `data_completeness`
reports the fraction of the industry's currently-valid indicator weight that
was actually usable (present AND not stale).
"""

from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any, Dict, List, Optional

from committee.industry_cycle import repository
from committee.industry_cycle.scoring_common import ScoreComponent, ScoreResult, weighted_logistic_score

_PERIOD_DAYS = {
    "daily": 1,
    "weekly": 7,
    "monthly": 30,
    "quarterly": 91,
    "annual": 365,
}


@dataclass(frozen=True)
class IndicatorEvidence:
    """One mapped indicator's contribution (or reason for exclusion) to `fundamentals_score`."""

    indicator_id: str
    direction: Optional[str]
    weight_declared: float
    included: bool
    reason: Optional[str] = None
    raw_value: Optional[float] = None
    baseline: float = 0.0
    standardized_value: Optional[float] = None
    observed_at: Optional[str] = None
    weight_normalized: Optional[float] = None
    weighted_value: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "indicator_id": self.indicator_id,
            "direction": self.direction,
            "weight_declared": self.weight_declared,
            "included": self.included,
            "reason": self.reason,
            "raw_value": self.raw_value,
            "baseline": self.baseline,
            "standardized_value": self.standardized_value,
            "observed_at": self.observed_at,
            "weight_normalized": self.weight_normalized,
            "weighted_value": self.weighted_value,
        }


@dataclass(frozen=True)
class FundamentalsScoreBundle:
    industry_id: str
    as_of: str
    score: Optional[float]
    weighted_sum: Optional[float]
    reason: Optional[str]
    data_completeness: float
    evidence: List[IndicatorEvidence] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "industry_id": self.industry_id,
            "as_of": self.as_of,
            "score": self.score,
            "weighted_sum": self.weighted_sum,
            "reason": self.reason,
            "data_completeness": self.data_completeness,
            "evidence": [e.to_dict() for e in self.evidence],
        }

    def non_price_evidence(self) -> List[IndicatorEvidence]:
        """Mapped indicators that actually contributed a value (used as 'non-price evidence' count,
        design doc section 12 Phase 2 completion criterion: '회복 초입 신호마다 최소 2개 이상의
        비가격 근거가 있다')."""
        return [e for e in self.evidence if e.included]


def _is_valid_at(mapping: Dict[str, Any], as_of: str) -> bool:
    valid_from = mapping.get("valid_from")
    valid_to = mapping.get("valid_to")
    if valid_from and as_of < str(valid_from):
        return False
    if valid_to and as_of > str(valid_to):
        return False
    return True


def _periods_stale(observed_at: str, as_of: str, frequency: Optional[str]) -> Optional[float]:
    try:
        observed_date = date.fromisoformat(observed_at[:10])
        as_of_date = date.fromisoformat(as_of[:10])
    except ValueError:
        return None
    period_days = _PERIOD_DAYS.get(frequency or "monthly", 30)
    age_days = (as_of_date - observed_date).days
    if age_days < 0:
        return None
    return age_days / period_days


def compute_fundamentals_score(
    industry_id: str,
    as_of: str,
    *,
    fundamentals_model_config: Dict[str, Any],
    db_path: Path | None = None,
) -> FundamentalsScoreBundle:
    """Compute one industry's `fundamentals_score` as of `as_of` (point-in-time safe)."""
    mappings = [
        m
        for m in repository.list_industry_indicators(industry_id, db_path=db_path)
        if _is_valid_at(m, as_of)
    ]
    catalog_by_id = {c["indicator_id"]: c for c in repository.list_indicators(db_path=db_path)}
    staleness_cfg: Dict[str, int] = fundamentals_model_config.get("staleness_max_periods_by_frequency", {})

    evidence: List[IndicatorEvidence] = []
    raw_components: Dict[str, Optional[float]] = {}
    weight_cfg: Dict[str, float] = {}

    for mapping in mappings:
        indicator_id = mapping["indicator_id"]
        direction = mapping.get("direction") or "positive"
        weight = float(mapping.get("weight") if mapping.get("weight") is not None else 1.0)
        weight_cfg[indicator_id] = weight

        catalog_entry = catalog_by_id.get(indicator_id)
        frequency = catalog_entry.get("frequency") if catalog_entry else None
        baseline = float((catalog_entry or {}).get("baseline") or 0.0)

        observations = repository.get_observations_as_of(indicator_id, as_of, db_path=db_path)
        if not observations:
            raw_components[indicator_id] = None
            evidence.append(
                IndicatorEvidence(
                    indicator_id=indicator_id,
                    direction=direction,
                    weight_declared=weight,
                    included=False,
                    reason="no_observation_available",
                    baseline=baseline,
                )
            )
            continue

        latest = observations[0]
        if latest.get("value") is None:
            raw_components[indicator_id] = None
            evidence.append(
                IndicatorEvidence(
                    indicator_id=indicator_id,
                    direction=direction,
                    weight_declared=weight,
                    included=False,
                    reason="observation_value_is_null",
                    observed_at=latest.get("observed_at"),
                    baseline=baseline,
                )
            )
            continue

        max_periods_stale = staleness_cfg.get(frequency or "monthly")
        periods_stale = _periods_stale(latest["observed_at"], as_of, frequency)
        if max_periods_stale is not None and periods_stale is not None and periods_stale > max_periods_stale:
            raw_components[indicator_id] = None
            evidence.append(
                IndicatorEvidence(
                    indicator_id=indicator_id,
                    direction=direction,
                    weight_declared=weight,
                    included=False,
                    reason=f"stale: {periods_stale:.1f} periods old (max {max_periods_stale})",
                    raw_value=latest["value"],
                    observed_at=latest.get("observed_at"),
                    baseline=baseline,
                )
            )
            continue

        sign = 1.0 if direction == "positive" else -1.0
        standardized = (latest["value"] - baseline) * sign
        raw_components[indicator_id] = standardized
        evidence.append(
            IndicatorEvidence(
                indicator_id=indicator_id,
                direction=direction,
                weight_declared=weight,
                included=True,
                raw_value=latest["value"],
                baseline=baseline,
                standardized_value=standardized,
                observed_at=latest.get("observed_at"),
            )
        )

    if not weight_cfg:
        return FundamentalsScoreBundle(
            industry_id=industry_id,
            as_of=as_of,
            score=None,
            weighted_sum=None,
            reason="no_indicators_mapped",
            data_completeness=0.0,
            evidence=[],
        )

    group_config = {
        "components": weight_cfg,
        "scale_k": fundamentals_model_config["scale_k"],
        "min_components": fundamentals_model_config["min_components"],
    }
    result: ScoreResult = weighted_logistic_score(raw_components, group_config)

    total_weight = sum(weight_cfg.values())
    used_weight = sum(weight_cfg[e.indicator_id] for e in evidence if e.included)
    data_completeness = (used_weight / total_weight) if total_weight else 0.0

    result_by_key = {c.key: c for c in result.components}
    final_evidence: List[IndicatorEvidence] = []
    for e in evidence:
        comp = result_by_key.get(e.indicator_id)
        if comp is not None and e.included:
            e = IndicatorEvidence(
                indicator_id=e.indicator_id,
                direction=e.direction,
                weight_declared=e.weight_declared,
                included=e.included,
                reason=e.reason,
                raw_value=e.raw_value,
                baseline=e.baseline,
                standardized_value=e.standardized_value,
                observed_at=e.observed_at,
                weight_normalized=comp.weight,
                weighted_value=comp.weighted_value,
            )
        final_evidence.append(e)

    return FundamentalsScoreBundle(
        industry_id=industry_id,
        as_of=as_of,
        score=result.score,
        weighted_sum=result.weighted_sum,
        reason=result.reason,
        data_completeness=data_completeness,
        evidence=final_evidence,
    )
