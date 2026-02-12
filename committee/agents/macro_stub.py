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
        elif "volatile" in snapshot.market_summary.note.lower():
            regime = RegimeTag.RISK_OFF
            confidence = ConfidenceLevel.MED
            claims = ["Macro tone is cautious.", "Volatility noted.", "Prefer defense."]
        else:
            regime = RegimeTag.NEUTRAL
            confidence = ConfidenceLevel.MED
            claims = ["Macro tone is balanced.", "No major shocks.", "Stay selective."]

        return Stance(
            agent_name=AgentName.MACRO,
            core_claims=claims[:3],
            regime_tag=regime,
            evidence_ids=[
                "snapshot.market_summary.usdkrw",
                "snapshot.market_summary.kospi_change_pct",
                "snapshot.news_headlines",
            ],
            confidence=confidence,
        )
