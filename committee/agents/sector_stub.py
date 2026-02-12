from __future__ import annotations

# Stub sector agent with simple rules.

from committee.agents.base import PreAnalysisAgent
from committee.schemas.snapshot import Snapshot
from committee.schemas.stance import AgentName, ConfidenceLevel, RegimeTag, Stance


class SectorStub(PreAnalysisAgent):
    """Generate a sector stance from snapshot sector moves."""
    def run(self, snapshot: Snapshot) -> Stance:
        """Return a stance based on sector movement text."""
        sector_text = " ".join(snapshot.sector_moves).lower()
        if "tech" in sector_text and "firm" in sector_text:
            regime = RegimeTag.RISK_ON
            confidence = ConfidenceLevel.MED
            claims = ["Growth sectors show strength.", "Tech tone is firm.", "Risk appetite improving."]
        else:
            regime = RegimeTag.NEUTRAL
            confidence = ConfidenceLevel.LOW
            claims = ["Sector moves are mixed.", "No clear leader.", "Maintain balance."]

        return Stance(
            agent_name=AgentName.SECTOR,
            core_claims=claims[:3],
            regime_tag=regime,
            evidence_ids=["snapshot.sector_moves", "snapshot.watchlist"],
            confidence=confidence,
        )
