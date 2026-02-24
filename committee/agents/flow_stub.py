from __future__ import annotations

# Stub flow agent with simple rules.

from committee.agents.base import PreAnalysisAgent
from committee.schemas.snapshot import Snapshot
from committee.schemas.stance import AgentName, ConfidenceLevel, RegimeTag, Stance


class FlowStub(PreAnalysisAgent):
    """Generate a flow stance from snapshot notes."""
    def run(self, snapshot: Snapshot) -> Stance:
        """Return a stance based on flow summary text."""
        data_unavailable = (
            (
                snapshot.flow_summary.foreign_net == 0.0
                or snapshot.flow_summary.institution_net == 0.0
                or snapshot.flow_summary.retail_net == 0.0
            )
            and "fetch_failed" in snapshot.flow_summary.note
        )
        if data_unavailable:
            regime = RegimeTag.NEUTRAL
            confidence = ConfidenceLevel.LOW
            claims = ["Flow data unavailable.", "Use neutral stance."]
            comment = "수급 데이터가 없어 중립을 유지합니다."
        elif "inflow" in snapshot.flow_summary.note.lower():
            regime = RegimeTag.RISK_ON
            confidence = ConfidenceLevel.HIGH
            claims = ["Flows are supportive.", "Demand leads supply.", "Risk appetite rising."]
            comment = "수급 흐름이 우호적이라 위험 선호가 높아 보입니다."
        else:
            regime = RegimeTag.NEUTRAL
            confidence = ConfidenceLevel.MED
            claims = ["Flows are balanced.", "No strong tilt.", "Keep positions moderate."]
            comment = "수급이 균형적이라 포지션은 보수적으로 유지하세요."

        return Stance(
            agent_name=AgentName.FLOW,
            core_claims=claims[:3],
            korean_comment=comment,
            regime_tag=regime,
            evidence_ids=["snapshot.flow_summary.note", "snapshot.watchlist"],
            confidence=confidence,
        )
