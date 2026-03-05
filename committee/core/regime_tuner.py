from __future__ import annotations

"""Stability tuner for committee regime decisions."""

from committee.schemas.committee_result import CommitteeResult, OpsGuidance, OpsGuidanceLevel
from committee.schemas.snapshot import Snapshot
from committee.schemas.stance import ConfidenceLevel, RegimeTag, Stance


_CONFIDENCE_WEIGHT = {
    ConfidenceLevel.LOW: 1.0,
    ConfidenceLevel.MED: 2.0,
    ConfidenceLevel.HIGH: 3.0,
}

_AGENT_WEIGHT = {
    "macro": 1.2,
    "risk": 1.2,
    "liquidity": 1.2,
    "flow": 1.0,
    "breadth": 1.0,
    "sector": 0.9,
    "earnings": 0.8,
}


def tune_committee_result(snapshot: Snapshot, stances: list[Stance], committee_result: CommitteeResult) -> CommitteeResult:
    """Tune committee regime with confidence weighting and cumulative context."""
    implied = _implied_regime_from_consensus(committee_result.consensus)
    weighted = _weighted_regime_from_stances(stances)
    tuned = _apply_cumulative_guardrails(weighted, snapshot)

    if tuned == implied:
        return committee_result

    key_points = [item.model_dump() for item in committee_result.key_points]
    majority_text = f"Majority regime tag: {tuned.value}."
    replaced = False
    for item in key_points:
        point = str(item.get("point", ""))
        if point.startswith("Majority regime tag:"):
            item["point"] = majority_text
            replaced = True
            break
    if not replaced:
        key_points.insert(0, {"point": majority_text, "sources": ["regime_tuner"]})

    key_points.append(
        {
            "point": "Stability guardrail applied from confidence-weighted votes and cumulative context.",
            "sources": ["regime_tuner"],
        }
    )

    return CommitteeResult(
        consensus=_consensus_text(tuned),
        key_points=key_points[:3],
        disagreements=committee_result.disagreements,
        ops_guidance=_ops_guidance(tuned),
    )


def _weighted_regime_from_stances(stances: list[Stance]) -> RegimeTag:
    if not stances:
        return RegimeTag.NEUTRAL

    score = 0.0
    total_weight = 0.0
    for stance in stances:
        c_weight = _CONFIDENCE_WEIGHT.get(stance.confidence, 1.0)
        a_weight = _AGENT_WEIGHT.get(stance.agent_name.value, 1.0)
        weight = c_weight * a_weight
        total_weight += weight
        if stance.regime_tag == RegimeTag.RISK_ON:
            score += weight
        elif stance.regime_tag == RegimeTag.RISK_OFF:
            score -= weight

    if total_weight <= 0:
        return RegimeTag.NEUTRAL
    normalized = score / total_weight

    # Stability dead-zone: weak edge defaults to neutral.
    if normalized >= 0.22:
        return RegimeTag.RISK_ON
    if normalized <= -0.22:
        return RegimeTag.RISK_OFF
    return RegimeTag.NEUTRAL


def _apply_cumulative_guardrails(base: RegimeTag, snapshot: Snapshot) -> RegimeTag:
    cc = snapshot.cumulative_context
    if cc is None or cc.sample_count < 5:
        return base

    # Whipsaw guard: after crash-rebound day, avoid persistent full risk-off.
    if cc.reversal_signal and base == RegimeTag.RISK_OFF:
        return RegimeTag.NEUTRAL

    # Regime persistence from medium-horizon trend.
    if cc.sample_count >= 10:
        if cc.kospi_20d_cum_pct >= 8.0 and cc.vix_5d_avg <= 24.0 and base != RegimeTag.RISK_OFF:
            return RegimeTag.RISK_ON
        if cc.kospi_20d_cum_pct <= -8.0 and cc.vix_5d_avg >= 20.0 and cc.usdkrw_5d_change_pct >= 0.8:
            return RegimeTag.RISK_OFF

    # High short-term turbulence leans neutral unless medium-term trend is very clear.
    if cc.kospi_abs_move_5d_avg >= 3.0 and abs(cc.kospi_20d_cum_pct) < 6.0:
        return RegimeTag.NEUTRAL

    return base


def _implied_regime_from_consensus(consensus: str) -> RegimeTag:
    text = (consensus or "").lower()
    if "risk-on" in text:
        return RegimeTag.RISK_ON
    if "defensive" in text or "reduces risk exposure" in text:
        return RegimeTag.RISK_OFF
    return RegimeTag.NEUTRAL


def _consensus_text(tag: RegimeTag) -> str:
    if tag == RegimeTag.RISK_ON:
        return "Committee supports risk-on positioning with disciplined risk controls."
    if tag == RegimeTag.RISK_OFF:
        return "Committee adopts a defensive posture and reduces risk exposure."
    return "Committee maintains a neutral posture with selective positioning."


def _ops_guidance(tag: RegimeTag) -> list[OpsGuidance]:
    if tag == RegimeTag.RISK_ON:
        return [
            OpsGuidance(level=OpsGuidanceLevel.OK, text="Lean into confirmed momentum leaders."),
            OpsGuidance(level=OpsGuidanceLevel.CAUTION, text="Size positions with volatility limits."),
            OpsGuidance(level=OpsGuidanceLevel.AVOID, text="Avoid chasing overstretched breakouts."),
        ]
    if tag == RegimeTag.RISK_OFF:
        return [
            OpsGuidance(level=OpsGuidanceLevel.OK, text="Keep exposure focused on resilience."),
            OpsGuidance(level=OpsGuidanceLevel.CAUTION, text="Favor defensive positioning."),
            OpsGuidance(level=OpsGuidanceLevel.AVOID, text="Avoid high-beta risk assets."),
        ]
    return [
        OpsGuidance(level=OpsGuidanceLevel.OK, text="Maintain balanced exposure."),
        OpsGuidance(level=OpsGuidanceLevel.CAUTION, text="Keep risk limits tight."),
        OpsGuidance(level=OpsGuidanceLevel.AVOID, text="Avoid aggressive leverage."),
    ]
