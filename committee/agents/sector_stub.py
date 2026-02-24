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
            comment = "성장/테크가 강해 위험 선호가 개선됩니다."
        else:
            regime = RegimeTag.NEUTRAL
            confidence = ConfidenceLevel.LOW
            claims = ["Sector moves are mixed.", "No clear leader.", "Maintain balance."]
            comment = "섹터 주도주가 불명확해 균형 유지가 낫습니다."

        return Stance(
            agent_name=AgentName.SECTOR,
            core_claims=claims[:3],
            korean_comment=comment,
            regime_tag=regime,
            evidence_ids=["snapshot.sector_moves", "snapshot.watchlist"],
            confidence=confidence,
        )
