from __future__ import annotations

# Stub macro agent with simple rules.

from committee.agents.base import PreAnalysisAgent
from committee.schemas.snapshot import Snapshot
from committee.schemas.stance import AgentName, ConfidenceLevel, RegimeTag, Stance


class MacroStub(PreAnalysisAgent):
    """Generate a macro stance from snapshot notes."""
    def run(self, snapshot: Snapshot) -> Stance:
        """Return a stance based on market summary text."""
        data_unavailable = (
            snapshot.market_summary.usdkrw == 0.0
            and snapshot.market_summary.kospi_change_pct == 0.0
            and "fetch_failed" in snapshot.market_summary.note
        )
        if data_unavailable:
            regime = RegimeTag.NEUTRAL
            confidence = ConfidenceLevel.LOW
            claims = ["Macro data unavailable.", "Use neutral stance."]
            comment = "거시 데이터가 부족해 중립을 유지합니다."
        elif "volatile" in snapshot.market_summary.note.lower():
            regime = RegimeTag.RISK_OFF
            confidence = ConfidenceLevel.MED
            claims = ["Macro tone is cautious.", "Volatility noted.", "Prefer defense."]
            comment = "변동성 경고가 있어 방어적 접근이 필요합니다."
        else:
            regime = RegimeTag.NEUTRAL
            confidence = ConfidenceLevel.MED
            claims = ["Macro tone is balanced.", "No major shocks.", "Stay selective."]
            comment = "거시는 균형적이며 선택적 대응이 적절합니다."

        return Stance(
            agent_name=AgentName.MACRO,
            core_claims=claims[:3],
            korean_comment=comment,
            regime_tag=regime,
            evidence_ids=[
                "snapshot.market_summary.usdkrw",
                "snapshot.market_summary.kospi_change_pct",
                "snapshot.news_headlines",
            ],
            confidence=confidence,
        )
