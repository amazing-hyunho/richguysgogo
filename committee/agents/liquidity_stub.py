from __future__ import annotations

# Stub liquidity/policy-surprise agent with simple heuristics.

from committee.agents.base import PreAnalysisAgent
from committee.schemas.snapshot import Snapshot
from committee.schemas.stance import AgentName, ConfidenceLevel, RegimeTag, Stance


class LiquidityStub(PreAnalysisAgent):
    """Generate a liquidity stance from rates, dollar, and volatility context."""

    def run(self, snapshot: Snapshot) -> Stance:
        """Return stance from macro daily/structural liquidity proxies."""
        macro = snapshot.macro
        dxy = macro.daily.dxy if macro and macro.daily else None
        real_rate = macro.structural.real_rate if macro and macro.structural else None
        spread_2_10 = macro.daily.spread_2_10 if macro and macro.daily else None
        derived_score = (
            snapshot.phase_two_signals.liquidity_signal_score
            if snapshot.phase_two_signals is not None
            else 0.0
        )

        risk_off_signal = derived_score <= -0.8 or (
            (dxy is not None and dxy >= 105)
            or (real_rate is not None and real_rate >= 2.2)
            or (spread_2_10 is not None and spread_2_10 < -0.2)
        )
        risk_on_signal = derived_score >= 0.8 or (
            (dxy is not None and dxy <= 100)
            and (real_rate is None or real_rate <= 1.5)
            and (spread_2_10 is None or spread_2_10 >= 0)
        )

        if risk_off_signal:
            regime = RegimeTag.RISK_OFF
            confidence = ConfidenceLevel.MED
            claims = [
                "달러·실질금리 환경이 위험자산에 부담으로 작용합니다.",
                "유동성 여건이 타이트해 밸류에이션 할인 요인이 큽니다.",
                "정책/금리 민감 자산 비중 축소가 필요합니다.",
            ]
            comment = "유동성 여건이 긴축적이라 보수적 운용이 유리합니다."
        elif risk_on_signal:
            regime = RegimeTag.RISK_ON
            confidence = ConfidenceLevel.MED
            claims = [
                "달러 압력이 완화되고 금리 부담이 제한적입니다.",
                "유동성 환경이 위험자산 회복에 우호적입니다.",
                "정책 충격 가능성이 낮아 비중 확대 여지가 있습니다.",
            ]
            comment = "유동성/정책 환경이 우호적이라 리스크온을 지지합니다."
        else:
            regime = RegimeTag.NEUTRAL
            confidence = ConfidenceLevel.LOW
            claims = [
                "유동성 지표가 방향성 없이 혼재되어 있습니다.",
                "정책 민감도는 높지만 확증 신호는 부족합니다.",
                "과도한 베팅보다 리스크 균형이 유효합니다.",
            ]
            comment = "유동성 신호가 혼재되어 중립적 비중 관리가 적절합니다."

        return Stance(
            agent_name=AgentName.LIQUIDITY,
            core_claims=claims[:3],
            korean_comment=comment,
            regime_tag=regime,
            evidence_ids=[
                "snapshot.phase_two_signals.liquidity_signal_score",
                "snapshot.macro.daily.dxy",
                "snapshot.macro.structural.real_rate",
            ],
            confidence=confidence,
        )
