from __future__ import annotations

"""LLM-powered chair agent with rule-based fallback."""

import json
from dataclasses import dataclass

from committee.agents.chair_stub import ChairStub
from committee.schemas.committee_result import CommitteeResult
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

    def run(self, snapshot: Snapshot, stances: list[Stance]) -> CommitteeResult:
        """Return a strict CommitteeResult with safe fallback on any error."""

        try:
            config = load_openai_config()
            system_prompt = self._system_prompt()
            user_prompt = self._user_prompt(snapshot=snapshot, stances=stances)
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
            "Output JSON only. No markdown. "
            "All natural-language text must be in Korean. "
            "Required keys: consensus, key_points, disagreements, ops_guidance. "
            "consensus must be one sentence. "
            "key_points must be 1~3 items with keys point, sources. "
            "disagreements must be 1~3 items with keys topic, majority, minority, minority_agents, why_it_matters. "
            "ops_guidance must be exactly 3 items with levels OK, CAUTION, AVOID and concise text. "
            "Prefer evidence IDs and agent names from the provided input."
        )

    @staticmethod
    def _user_prompt(snapshot: Snapshot, stances: list[Stance]) -> str:
        m = snapshot.markets
        macro = snapshot.macro
        indicator_context = {
            "market_summary": snapshot.market_summary.note,
            "flow_summary": snapshot.flow_summary.note,
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
            "raw_snapshot": snapshot.model_dump(),
        }
        return json.dumps(payload, ensure_ascii=False)
