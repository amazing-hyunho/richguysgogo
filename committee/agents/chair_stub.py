from __future__ import annotations

# Rule-based chair to derive consensus from stances.

from typing import List

from committee.schemas.committee_result import (
    CommitteeResult,
    Disagreement,
    OpsGuidance,
    OpsGuidanceLevel,
)
from committee.schemas.stance import RegimeTag, Stance


class ChairStub:
    """Rule-based chair for consensus without live debate."""

    def run(self, stances: List[Stance]) -> CommitteeResult:
        """Generate a consensus result from stances."""
        total = len(stances)
        risk_off_count = sum(1 for stance in stances if stance.regime_tag == RegimeTag.RISK_OFF)
        tag_counts = {
            RegimeTag.RISK_ON: sum(1 for stance in stances if stance.regime_tag == RegimeTag.RISK_ON),
            RegimeTag.NEUTRAL: sum(1 for stance in stances if stance.regime_tag == RegimeTag.NEUTRAL),
            RegimeTag.RISK_OFF: sum(1 for stance in stances if stance.regime_tag == RegimeTag.RISK_OFF),
        }
        majority_tag = max(tag_counts, key=tag_counts.get) if total else None
        minority_exists = any(
            count > 0 for tag, count in tag_counts.items() if majority_tag is not None and tag != majority_tag
        )

        if total == 0:
            consensus = "No consensus can be formed due to missing stances."
            key_points = [
                {"point": "Stance list is empty.", "sources": ["none"]},
            ]
            disagreements = [
                Disagreement(
                    topic="Regime tags",
                    majority="None",
                    minority="None",
                    minority_agents=["none"],
                    why_it_matters="No stances provided, so no regime disagreement can be assessed.",
                )
            ]
            ops_guidance = [
                OpsGuidance(level=OpsGuidanceLevel.OK, text="Pause until stances are provided."),
                OpsGuidance(level=OpsGuidanceLevel.CAUTION, text="Await minimum stance coverage."),
                OpsGuidance(level=OpsGuidanceLevel.AVOID, text="Do not act without stances."),
            ]
        elif risk_off_count > total / 2:
            consensus = "Committee adopts a defensive posture and reduces risk exposure."
            key_points = _build_key_points(stances, majority_tag)
            disagreements = _build_disagreements(stances, tag_counts, majority_tag)
            ops_guidance = [
                OpsGuidance(level=OpsGuidanceLevel.OK, text="Keep exposure focused on resilience."),
                OpsGuidance(level=OpsGuidanceLevel.CAUTION, text="Favor defensive positioning."),
                OpsGuidance(level=OpsGuidanceLevel.AVOID, text="Avoid high-beta risk assets."),
            ]
        else:
            consensus = "Committee maintains a neutral posture with selective positioning."
            key_points = _build_key_points(stances, majority_tag)
            disagreements = _build_disagreements(stances, tag_counts, majority_tag)
            ops_guidance = [
                OpsGuidance(level=OpsGuidanceLevel.OK, text="Maintain balanced exposure."),
                OpsGuidance(level=OpsGuidanceLevel.CAUTION, text="Keep risk limits tight."),
                OpsGuidance(level=OpsGuidanceLevel.AVOID, text="Avoid aggressive leverage."),
            ]

        result = CommitteeResult(
            consensus=consensus,
            key_points=key_points[:3],
            disagreements=disagreements[:3],
            ops_guidance=ops_guidance,
        )
        if minority_exists and not result.disagreements:
            result.disagreements = [
                Disagreement(
                    topic="Regime tags",
                    majority=majority_tag.value if majority_tag else "None",
                    minority="Minority present",
                    minority_agents=["unknown"],
                    why_it_matters="Minority regime should be recorded for review.",
                )
            ]
        if "\n" in result.consensus:
            raise ValueError("Consensus must be a single sentence.")
        terminators = sum(result.consensus.count(ch) for ch in ".!?")
        if terminators > 1:
            raise ValueError("Consensus must be a single sentence.")
        return result


def _build_disagreements(
    stances: List[Stance],
    tag_counts: dict[RegimeTag, int],
    majority_tag: RegimeTag | None,
) -> List[Disagreement]:
    """Build structured disagreement items from stance tags."""
    if majority_tag is None:
        return [
            Disagreement(
                topic="Regime tags",
                majority="None",
                minority="None",
                minority_agents=["none"],
                why_it_matters="No stances provided, so no regime disagreement can be assessed.",
            )
        ]

    disagreements: List[Disagreement] = []
    minority_exists = any(
        count > 0 for tag, count in tag_counts.items() if tag != majority_tag
    )
    for tag, count in tag_counts.items():
        if tag != majority_tag and count > 0:
            minority_agents = [
                stance.agent_name.value
                for stance in stances
                if stance.regime_tag == tag
            ]
            disagreements.append(
                Disagreement(
                    topic="Regime tags",
                    majority=majority_tag.value,
                    minority=tag.value,
                    minority_agents=minority_agents[:5] or ["unknown"],
                    why_it_matters="Minority risk regime can change positioning boundaries.",
                )
            )

    if not disagreements:
        disagreements.append(
            Disagreement(
                topic="Regime tags",
                majority=majority_tag.value,
                minority="None" if not minority_exists else "Minority present",
                minority_agents=["none"],
                why_it_matters="No dissenting regime tags are present.",
            )
        )

    return disagreements


def _build_key_points(stances: List[Stance], majority_tag: RegimeTag | None) -> List[dict]:
    if not stances:
        return [{"point": "No stances provided.", "sources": ["none"]}]

    key_points: List[dict] = []

    tag_to_agents: dict[RegimeTag, list[str]] = {
        RegimeTag.RISK_ON: [],
        RegimeTag.NEUTRAL: [],
        RegimeTag.RISK_OFF: [],
    }
    for stance in stances:
        tag_to_agents[stance.regime_tag].append(stance.agent_name.value)

    if majority_tag is None:
        majority_tag = max(tag_to_agents, key=lambda tag: len(tag_to_agents[tag]))
    key_points.append(
        {
            "point": f"Majority regime tag: {majority_tag.value}.",
            "sources": tag_to_agents[majority_tag][:5] or ["unknown"],
        }
    )

    evidence_to_agents: dict[str, list[str]] = {}
    for stance in stances:
        for evidence in stance.evidence_ids:
            evidence_to_agents.setdefault(evidence, []).append(stance.agent_name.value)

    if evidence_to_agents:
        evidence, agents = max(evidence_to_agents.items(), key=lambda item: len(set(item[1])))
        if len(set(agents)) >= 2:
            key_points.append(
                {
                    "point": f"Shared evidence focus: {evidence}.",
                    "sources": sorted(set(agents))[:5],
                }
            )

    claim_to_agents: dict[str, list[str]] = {}
    for stance in stances:
        for claim in stance.core_claims:
            claim_to_agents.setdefault(claim, []).append(stance.agent_name.value)

    if claim_to_agents:
        claim, agents = max(claim_to_agents.items(), key=lambda item: len(set(item[1])))
        if len(set(agents)) >= 2:
            key_points.append(
                {
                    "point": f"Shared claim: {claim}",
                    "sources": sorted(set(agents))[:5],
                }
            )

    return key_points[:3]
