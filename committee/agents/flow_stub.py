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
        keywords = _flow_keywords(snapshot)
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
            claims = [
                f"핵심 키워드({keywords}) 대비 외국인+기관 순매수가 시장 방향을 지지합니다.",
                "프로 수급이 개인 매도 물량을 흡수하며 위험선호를 강화합니다.",
                "달러·금리·뉴스 리스크가 급격히 악화되지 않는 한 우호적 수급입니다.",
            ]
            comment = f"{keywords} 환경에서도 프로 수급이 우세해 위험 선호가 살아 있습니다."
        elif pro_total <= -300 and retail >= 0:
            regime = RegimeTag.RISK_OFF
            confidence = ConfidenceLevel.MED
            claims = [
                f"핵심 키워드({keywords})와 맞물려 외국인+기관 순매도가 우세합니다.",
                "개인 매수가 하락 압력을 흡수하지만, 환율·금리 부담이 크면 지속성은 낮아집니다.",
                "외국인 매도 축소 또는 USD/KRW 안정 전까지 방어적 해석이 필요합니다.",
            ]
            comment = f"{keywords} 부담 속 개인 흡수만으로는 수급 안정성이 부족합니다."
        else:
            regime = RegimeTag.NEUTRAL
            confidence = ConfidenceLevel.MED
            claims = [
                f"핵심 키워드({keywords}) 대비 수급 쏠림은 제한적입니다.",
                "외국인·기관·개인 흐름이 강한 방향성을 만들지 못하고 있습니다.",
                "거시/뉴스 확인 전까지 포지션은 중립적으로 유지하는 편이 낫습니다.",
            ]
            comment = f"{keywords}를 확인하며 중립 수급으로 해석합니다."

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


def _flow_keywords(snapshot: Snapshot) -> str:
    """Extract compact macro/news keywords for fallback flow commentary."""
    keywords: list[str] = []
    macro = snapshot.macro
    if snapshot.markets.fx.usdkrw >= 1450 or (macro.daily.dxy is not None and macro.daily.dxy >= 100):
        keywords.append("고환율/강달러")
    if macro.daily.us10y is not None and macro.daily.us10y >= 4.3:
        keywords.append("미국금리")
    if snapshot.markets.volatility.vix >= 18:
        keywords.append("변동성")

    headline_text = " ".join(snapshot.news_headlines)
    keyword_map = [
        ("반도체/AI", ("반도체", "AI", "엔비디아", "삼성전자")),
        ("연준/금리", ("연준", "FOMC", "금리", "CPI")),
        ("경기/성장", ("GDP", "성장", "경기")),
        ("정책/관세", ("관세", "정책", "중동", "전쟁")),
    ]
    for label, tokens in keyword_map:
        if any(token in headline_text for token in tokens) and label not in keywords:
            keywords.append(label)

    return ", ".join(keywords[:4]) if keywords else "특이 키워드 제한적"
