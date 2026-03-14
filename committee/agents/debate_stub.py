from __future__ import annotations

# Stub debate round builder in meeting-minute format.

from typing import List

from committee.schemas.debate import DebateMinute, DebateRound
from committee.schemas.snapshot import Snapshot
from committee.schemas.stance import AgentName, Stance


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
                round_conclusion="회의록 생성은 완료했으며, 최종 판단은 기존 의장 로직을 따릅니다.",
            )

        shared_evidence = _most_shared_evidence(stances)
        minutes: list[DebateMinute] = []

        for stance in stances:
            minutes.append(
                DebateMinute(
                    speaker=stance.agent_name,
                    speaker_label=_agent_owner_label(stance.agent_name),
                    summary=(
                        f"{_agent_owner_label(stance.agent_name)}는 '{stance.korean_comment}'를 유지하며 "
                        f"공통 근거({shared_evidence}) 재확인을 요청했습니다."
                    )[:240],
                    references=_normalize_evidence(stance.evidence_ids, fallback=shared_evidence),
                    internal_regime_tag=stance.regime_tag,
                )
            )

        return DebateRound(
            round_index=1,
            facilitator_note="각 담당자가 핵심 근거를 교차 점검하고 단기 노이즈 과잉해석을 경계하는 데 합의했습니다.",
            minutes=minutes,
            round_conclusion="1라운드 회의록 기준으로 근거 정합성 점검을 마쳤고 최종 합의는 의장이 종합합니다.",
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
