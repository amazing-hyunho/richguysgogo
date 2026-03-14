from __future__ import annotations

# Stub debate round builder in meeting-minute format.

from typing import List

from committee.schemas.debate import DebateMinute, DebateRound
from committee.schemas.snapshot import Snapshot
from committee.schemas.stance import AgentName, RegimeTag, Stance


_AGENT_OWNER_LABELS: dict[AgentName, str] = {
    AgentName.MACRO: "매크로 담당자",
    AgentName.FLOW: "수급 담당자",
    AgentName.SECTOR: "섹터 담당자",
    AgentName.RISK: "리스크 담당자",
    AgentName.EARNINGS: "이익모멘텀 담당자",
    AgentName.BREADTH: "브레드스 담당자",
    AgentName.LIQUIDITY: "유동성 담당자",
}


class DebateStub:
    """Create one deterministic meeting-minute round from existing stances."""

    def run(self, snapshot: Snapshot, stances: List[Stance]) -> DebateRound:
        if not stances:
            return DebateRound(
                round_index=1,
                facilitator_note="참여 가능한 에이전트 의견이 없어 회의를 생략했습니다.",
                minutes=[
                    DebateMinute(
                        speaker=AgentName.MACRO,
                        speaker_label=_agent_owner_label(AgentName.MACRO),
                        summary="당일 회의는 발언 가능한 사전 의견이 없어 보류했습니다.",
                        references=["snapshot.market_summary.note"],
                        internal_regime_tag="NEUTRAL",
                    )
                ],
                round_conclusion="의장 정리: 오늘은 입력된 의견이 부족해 판단을 보류합니다.",
            )

        shared_evidence = _most_shared_evidence(stances)
        minutes: list[DebateMinute] = []

        for stance in stances:
            references = _normalize_evidence(stance.evidence_ids, fallback=shared_evidence)
            metric_hint = _build_metric_hint(snapshot, references)
            summary_parts = [
                f"저는 {_agent_owner_label(stance.agent_name)} 입장에서 '{stance.korean_comment}' 의견을 유지합니다.",
            ]
            if metric_hint:
                summary_parts.append(f"근거 숫자는 {metric_hint}입니다.")
            summary_parts.append("결론은 성급하게 방향 바꾸지 말고, 근거 확인 후 대응하자는 쪽입니다.")
            minutes.append(
                DebateMinute(
                    speaker=stance.agent_name,
                    speaker_label=_agent_owner_label(stance.agent_name),
                    summary=" ".join(summary_parts)[:240],
                    references=references,
                    internal_regime_tag=stance.regime_tag,
                )
            )

        metric_linked_minutes = sum(1 for minute in minutes if _build_metric_hint(snapshot, minute.references))

        return DebateRound(
            round_index=1,
            facilitator_note=(
                f"오늘은 {len(minutes)}명 중 {metric_linked_minutes}명이 숫자 지표를 직접 언급했습니다. "
                "분위기는 급하게 베팅하기보다, 근거를 확인하고 천천히 가자는 쪽으로 모였습니다."
            ),
            minutes=minutes,
            round_conclusion=_build_chair_conclusion(snapshot=snapshot, stances=stances)[:240],
        )


def _agent_owner_label(agent_name: AgentName) -> str:
    return _AGENT_OWNER_LABELS.get(agent_name, f"{agent_name.value} 담당자")


def _most_shared_evidence(stances: List[Stance]) -> str:
    counter: dict[str, int] = {}
    for stance in stances:
        for evidence in stance.evidence_ids:
            counter[evidence] = counter.get(evidence, 0) + 1
    if not counter:
        return "snapshot.market_summary.note"
    return max(counter.items(), key=lambda item: item[1])[0]


def _normalize_evidence(evidence_ids: List[str], fallback: str) -> List[str]:
    cleaned = [item for item in evidence_ids if item.startswith("snapshot.")]
    if cleaned:
        return cleaned[:8]
    return [fallback]


def _build_metric_hint(snapshot: Snapshot, references: List[str]) -> str:
    hints: list[str] = []
    for reference in references:
        value = _reference_value(snapshot, reference)
        if value is None:
            continue
        hints.append(f"{reference.split('.')[-1]}={value}")
        if len(hints) >= 2:
            break
    return ", ".join(hints)


def _build_chair_conclusion(snapshot: Snapshot, stances: List[Stance]) -> str:
    vote_counts = {
        RegimeTag.RISK_ON: 0,
        RegimeTag.NEUTRAL: 0,
        RegimeTag.RISK_OFF: 0,
    }
    for stance in stances:
        vote_counts[stance.regime_tag] += 1
    majority_tag = max(vote_counts, key=vote_counts.get)

    regime_text = {
        RegimeTag.RISK_ON: "리스크 온",
        RegimeTag.NEUTRAL: "중립",
        RegimeTag.RISK_OFF: "리스크 오프",
    }[majority_tag]

    m = snapshot.markets
    indicator_part = (
        f"KOSPI {m.kr.kospi_pct:+.2f}%, USD/KRW {m.fx.usdkrw:.2f}({m.fx.usdkrw_pct:+.2f}%), "
        f"VIX {m.volatility.vix:.1f}, 외국인 {snapshot.flow_summary.foreign_net:+.0f}억"
    )

    news_part = _news_tone(snapshot.news_headlines)

    if majority_tag == RegimeTag.RISK_OFF:
        action = "비중은 방어적으로 유지하고, 변동성 완화 전까지 공격적 확대는 미룹니다"
    elif majority_tag == RegimeTag.RISK_ON:
        action = "모멘텀이 확인된 구간 위주로 비중을 늘리되 손절 기준은 짧게 가져갑니다"
    else:
        action = "중립 비중을 유지하면서 확인된 시그널에서만 선별 대응합니다"

    return (
        f"의장 정리: 오늘 다수 의견은 {regime_text}입니다. "
        f"근거는 {indicator_part}이고, {news_part}. "
        f"따라서 {action}."
    )


def _news_tone(headlines: list[str]) -> str:
    combined = " ".join(headlines[:20])
    if not combined:
        return "뉴스는 뚜렷한 추세 단서가 제한적"

    caution_keywords = ("전쟁", "긴축", "물가", "변동성", "하락", "관세", "리스크")
    risk_on_keywords = ("완화", "반등", "상승", "회복", "부양")

    caution_hits = sum(combined.count(word) for word in caution_keywords)
    risk_on_hits = sum(combined.count(word) for word in risk_on_keywords)

    if caution_hits > risk_on_hits:
        return "뉴스는 금리·변동성·지정학 이슈 중심의 경계 톤입니다"
    if risk_on_hits > caution_hits:
        return "뉴스는 반등·회복 기대가 섞인 완화 톤입니다"
    return "뉴스는 방향성이 엇갈려 단정하기 어렵습니다"


def _reference_value(snapshot: Snapshot, reference: str) -> str | None:
    if reference == "snapshot.flow_summary.foreign_net":
        return f"{snapshot.flow_summary.foreign_net:+.0f}억"
    if reference == "snapshot.flow_summary.institution_net":
        return f"{snapshot.flow_summary.institution_net:+.0f}억"
    if reference == "snapshot.flow_summary.retail_net":
        return f"{snapshot.flow_summary.retail_net:+.0f}억"
    if reference == "snapshot.market_summary.usdkrw":
        return f"{snapshot.markets.fx.usdkrw:.2f}"
    if reference == "snapshot.market_summary.kospi_change_pct":
        return f"{snapshot.markets.kr.kospi_pct:+.2f}%"
    if reference == "snapshot.markets.volatility.vix":
        return f"{snapshot.markets.volatility.vix:.1f}"
    if reference == "snapshot.macro.daily.dxy" and snapshot.macro is not None:
        return f"{snapshot.macro.daily.dxy:.2f}"
    if reference == "snapshot.macro.structural.real_rate" and snapshot.macro is not None:
        return f"{snapshot.macro.structural.real_rate:.2f}%"
    return None
