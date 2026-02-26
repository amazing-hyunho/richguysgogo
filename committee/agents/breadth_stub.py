from __future__ import annotations

# Stub breadth/technical regime agent with simple heuristics.

from committee.agents.base import PreAnalysisAgent
from committee.schemas.snapshot import Snapshot
from committee.schemas.stance import AgentName, ConfidenceLevel, RegimeTag, Stance


class BreadthStub(PreAnalysisAgent):
    """Generate a breadth/technical stance from cross-market spread."""

    def run(self, snapshot: Snapshot) -> Stance:
        """Return stance by comparing KR/US index diffusion and volatility."""
        spread = (
            snapshot.phase_two_signals.breadth_signal_score
            if snapshot.phase_two_signals is not None
            else (snapshot.markets.kr.kospi_pct + snapshot.markets.kr.kosdaq_pct) / 2.0
        )
        vix = snapshot.markets.volatility.vix

        if spread >= 1.2 and vix < 25:
            regime = RegimeTag.RISK_ON
            confidence = ConfidenceLevel.MED
            claims = [
                "국내 지수 확산 강도가 미국 대비 우위입니다.",
                "시장 내부체력(브레드스)이 개선되는 구간입니다.",
                "추세 추종 전략의 효율이 높아질 수 있습니다.",
            ]
            comment = "브레드스가 개선되어 기술적 추세는 우호적입니다."
        elif spread <= -1.2 or vix >= 30:
            regime = RegimeTag.RISK_OFF
            confidence = ConfidenceLevel.MED
            claims = [
                "지수 확산이 약화되어 추세 신뢰도가 낮습니다.",
                "변동성 레짐이 위험자산에 불리한 구간입니다.",
                "손절·비중관리 규칙을 강화할 필요가 있습니다.",
            ]
            comment = "브레드스 약화와 변동성 상승으로 보수적 대응이 필요합니다."
        else:
            regime = RegimeTag.NEUTRAL
            confidence = ConfidenceLevel.LOW
            claims = [
                "추세 확산과 역추세 신호가 공존합니다.",
                "기술적 우위가 명확하지 않습니다.",
                "방향 확정 전까지 균형 비중이 적절합니다.",
            ]
            comment = "브레드스 신호가 혼재되어 중립 대응이 합리적입니다."

        return Stance(
            agent_name=AgentName.BREADTH,
            core_claims=claims[:3],
            korean_comment=comment,
            regime_tag=regime,
            evidence_ids=[
                "snapshot.phase_two_signals.breadth_signal_score",
                "snapshot.markets.volatility.vix",
                "snapshot.market_summary.note",
            ],
            confidence=confidence,
        )
