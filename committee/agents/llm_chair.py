from __future__ import annotations

"""LLM-powered chair agent with rule-based fallback."""

import json
from dataclasses import dataclass

from committee.agents.chair_stub import ChairStub
from committee.schemas.committee_result import CommitteeResult
from committee.schemas.debate import DebateRound
from committee.schemas.snapshot import Snapshot
from committee.schemas.stance import Stance
from committee.tools.openai_chat import chat_completion, load_openai_config


@dataclass(frozen=True)
class ChairLLMOptions:
    """Runtime options for chair LLM consensus."""

    model: str = "gpt-4.1-mini"
    temperature: float = 0.1


class LLMChairAgent:
    """Generate committee consensus via LLM, then validate schema."""

    def __init__(self, *, fallback_agent: ChairStub, options: ChairLLMOptions):
        self.fallback_agent = fallback_agent
        self.options = options

    def run(self, snapshot: Snapshot, stances: list[Stance], debate_round: DebateRound | None = None) -> CommitteeResult:
        """Return a strict CommitteeResult with safe fallback on any error."""

        try:
            config = load_openai_config()
            system_prompt = self._system_prompt()
            user_prompt = self._user_prompt(snapshot=snapshot, stances=stances, debate_round=debate_round)
            raw = chat_completion(
                config=config,
                model=self.options.model,
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=self.options.temperature,
            )
            parsed = json.loads(raw)
            return CommitteeResult.model_validate(parsed)
        except Exception:
            return self.fallback_agent.run(stances)

    @staticmethod
    def _system_prompt() -> str:
        return (
            "You are the CHAIR of an investment committee. "
            "Synthesize agent stances into one pragmatic consensus. "
            "Use both market indicators and agent opinions as evidence. "
            "Do not overfit to one-day moves; prioritize cumulative context when available. "
            "Output JSON only. No markdown. "
            "All natural-language text must be in Korean. "
            "Required keys: consensus, key_points, disagreements, ops_guidance, sugeup_narrative. "
            "consensus must be one sentence. "
            "key_points must be 1~3 items with keys point, sources. "
            "disagreements must be 1~3 items with keys topic, majority, minority, minority_agents, why_it_matters. "
            "ops_guidance must be exactly 3 items with levels OK, CAUTION, AVOID and concise text. "
            "sugeup_narrative must be a plain-text Korean string (no markdown, no bullet symbols) "
            "structured as exactly 3 paragraphs separated by newlines:\n"
            "  Paragraph 1 — '외국인 매도 이유': Explain WHY foreigners are selling. "
            "Consider profit-taking after large cumulative gains, passive fund rebalancing when "
            "Korea/semiconductor weight exceeded limits, and FX pressure (USD/KRW rising with selling). "
            "Use the actual flow numbers from the data.\n"
            "  Paragraph 2 — '개인 매수 이유와 리스크': Explain WHY retail investors are buying "
            "(AI/semiconductor narrative, re-rating thesis) and what the key risk is "
            "(leverage level, forced selling risk, speed of absorption vs. foreign supply).\n"
            "  Paragraph 3 — '시나리오 판단과 투자 결론': State the most likely short-term outcome "
            "(sharp crash vs. high-volatility range-bound vs. healthy pullback then rally). "
            "Give one actionable conclusion: what existing holders should do and what new entrants should watch. "
            "Total length: 200~500 Korean characters per paragraph, 600~1500 chars total. "
            "Prefer evidence IDs and agent names from the provided input."
        )

    @staticmethod
    def _user_prompt(snapshot: Snapshot, stances: list[Stance], debate_round: DebateRound | None = None) -> str:
        m = snapshot.markets
        macro = snapshot.macro
        indicator_context = {
            "market_summary": snapshot.market_summary.note,
            "flow_summary": snapshot.flow_summary.note,
            "flow_totals_eok": {
                "foreign_net": snapshot.flow_summary.foreign_net,
                "institution_net": snapshot.flow_summary.institution_net,
                "retail_net": snapshot.flow_summary.retail_net,
            },
            "korean_market_flow": (
                snapshot.korean_market_flow.model_dump() if snapshot.korean_market_flow else None
            ),
            "cumulative_context": (
                snapshot.cumulative_context.model_dump() if snapshot.cumulative_context else None
            ),
            "indices": {
                "kospi_pct": m.kr.kospi_pct,
                "kosdaq_pct": m.kr.kosdaq_pct,
                "sp500_pct": m.us.sp500_pct,
                "nasdaq_pct": m.us.nasdaq_pct,
                "dow_pct": m.us.dow_pct,
            },
            "fx_vol": {
                "usdkrw": m.fx.usdkrw,
                "usdkrw_pct": m.fx.usdkrw_pct,
                "vix": m.volatility.vix,
            },
            "macro_daily": macro.daily.model_dump() if macro else None,
            "macro_monthly": macro.monthly.model_dump() if macro else None,
            "macro_quarterly": macro.quarterly.model_dump() if macro else None,
            "macro_structural": macro.structural.model_dump() if macro else None,
            "headlines": snapshot.news_headlines[:20],
        }
        agent_opinions = [
            {
                "agent_name": stance.agent_name.value,
                "regime_tag": stance.regime_tag.value,
                "confidence": stance.confidence.value,
                "core_claims": stance.core_claims,
                "korean_comment": stance.korean_comment,
                "evidence_ids": stance.evidence_ids,
            }
            for stance in stances
        ]
        payload = {
            "indicator_context": indicator_context,
            "agent_opinions": agent_opinions,
            "debate_round": debate_round.model_dump() if debate_round is not None else None,
            "raw_snapshot": snapshot.model_dump(),
        }
        return json.dumps(payload, ensure_ascii=False)
