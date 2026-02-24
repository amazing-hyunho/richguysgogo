from __future__ import annotations

# Stub risk agent with simple rules.

from committee.agents.base import PreAnalysisAgent
from committee.schemas.snapshot import Snapshot
from committee.schemas.stance import AgentName, ConfidenceLevel, RegimeTag, Stance


class RiskStub(PreAnalysisAgent):
    """Generate a risk stance from snapshot headlines."""
    def run(self, snapshot: Snapshot) -> Stance:
        """Return a stance based on news headline text."""
        headline_text = " ".join(snapshot.news_headlines).lower()
        if "risk" in headline_text or "downgrade" in headline_text:
            regime = RegimeTag.RISK_OFF
            confidence = ConfidenceLevel.HIGH
            claims = ["Risk signals elevated.", "Headline risk rising.", "Reduce exposure."]
            comment = "리스크 신호가 높아 노출 축소가 필요합니다."
        else:
            regime = RegimeTag.NEUTRAL
            confidence = ConfidenceLevel.MED
            claims = ["Risk signals stable.", "No acute stress.", "Maintain discipline."]
            comment = "급격한 리스크는 없어 규율을 유지하세요."

        return Stance(
            agent_name=AgentName.RISK,
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
