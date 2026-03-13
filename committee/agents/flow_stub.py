from __future__ import annotations

# Stub flow agent with simple rules.

from committee.agents.base import PreAnalysisAgent
from committee.schemas.snapshot import Snapshot
from committee.schemas.stance import AgentName, ConfidenceLevel, RegimeTag, Stance


class FlowStub(PreAnalysisAgent):
    """Generate a flow stance from snapshot notes."""
    def run(self, snapshot: Snapshot) -> Stance:
        """Return a stance based on flow summary text."""
        foreign = snapshot.flow_summary.foreign_net
        institution = snapshot.flow_summary.institution_net
        retail = snapshot.flow_summary.retail_net
        pro_total = foreign + institution
        data_unavailable = (
            (
                foreign == 0.0
                or institution == 0.0
                or retail == 0.0
            )
            and "fetch_failed" in snapshot.flow_summary.note
        )
        if data_unavailable:
            regime = RegimeTag.NEUTRAL
            confidence = ConfidenceLevel.LOW
            claims = ["Flow data unavailable.", "Use neutral stance."]
            comment = "수급 데이터가 없어 중립을 유지합니다."
        elif pro_total >= 300 and retail <= 0:
            regime = RegimeTag.RISK_ON
            confidence = ConfidenceLevel.HIGH
            claims = ["외국인+기관 순매수가 강합니다.", "프로 수급이 방향성을 지지합니다.", "위험자산 선호가 강화됩니다."]
            comment = "수급 흐름이 우호적이라 위험 선호가 높아 보입니다."
        elif pro_total <= -300 and retail >= 0:
            regime = RegimeTag.RISK_OFF
            confidence = ConfidenceLevel.MED
            claims = ["외국인+기관 순매도가 우세합니다.", "수급 역풍이 확대되고 있습니다.", "방어 비중이 유리합니다."]
            comment = "수급 역풍이 커져 방어적 대응이 필요합니다."
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
            evidence_ids=[
                "snapshot.flow_summary.foreign_net",
                "snapshot.flow_summary.institution_net",
                "snapshot.flow_summary.retail_net",
            ],
            confidence=confidence,
        )
