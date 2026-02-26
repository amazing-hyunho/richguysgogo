from __future__ import annotations

# Stub earnings-revision agent with simple heuristics.

from committee.agents.base import PreAnalysisAgent
from committee.schemas.snapshot import Snapshot
from committee.schemas.stance import AgentName, ConfidenceLevel, RegimeTag, Stance


class EarningsStub(PreAnalysisAgent):
    """Generate an earnings-revision stance from headlines and market context."""

    def run(self, snapshot: Snapshot) -> Stance:
        """Return stance using simple earnings surprise/revision keywords."""
        derived_score = (
            snapshot.phase_two_signals.earnings_signal_score
            if snapshot.phase_two_signals is not None
            else 0.0
        )

        if derived_score <= -1.0:
            regime = RegimeTag.RISK_OFF
            confidence = ConfidenceLevel.MED
            claims = [
                "실적/가이던스 하향 신호가 누적됩니다.",
                "이익 추정치 둔화 가능성이 커졌습니다.",
                "밸류에이션 리레이팅 압력이 발생할 수 있습니다.",
            ]
            comment = "이익 모멘텀이 약해져 방어적 접근이 유리합니다."
        elif derived_score >= 1.0 or snapshot.markets.kr.kospi_pct >= 1.0:
            regime = RegimeTag.RISK_ON
            confidence = ConfidenceLevel.MED
            claims = [
                "실적/가이던스 상향 관련 단서가 우세합니다.",
                "이익 추정치 개선 기대가 유지됩니다.",
                "주가 상승의 펀더멘털 정당화 가능성이 있습니다.",
            ]
            comment = "이익 모멘텀이 견조해 위험자산 선호를 지지합니다."
        else:
            regime = RegimeTag.NEUTRAL
            confidence = ConfidenceLevel.LOW
            claims = [
                "실적 추정치 방향성이 뚜렷하지 않습니다.",
                "상향/하향 신호가 혼재되어 있습니다.",
                "확증 신호 전까지 중립 대응이 적절합니다.",
            ]
            comment = "이익 모멘텀 신호가 혼재되어 중립을 유지합니다."

        return Stance(
            agent_name=AgentName.EARNINGS,
            core_claims=claims[:3],
            korean_comment=comment,
            regime_tag=regime,
            evidence_ids=[
                "snapshot.phase_two_signals.earnings_signal_score",
                "snapshot.news_headlines",
                "snapshot.market_summary.note",
            ],
            confidence=confidence,
        )
