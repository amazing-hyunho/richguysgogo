from __future__ import annotations

"""LLM-backed pre-analysis agents with schema-safe fallback."""

import json
import os
from dataclasses import dataclass

from committee.agents.base import PreAnalysisAgent
from committee.agents.model_profiles import ModelBackend, get_agent_model_candidates
from committee.agents.system_prompts import get_system_prompt
from committee.core.trace_logger import TraceLogger
from committee.schemas.snapshot import Snapshot
from committee.schemas.stance import AgentName, Stance
from committee.tools.openai_chat import chat_completion, load_openai_config


@dataclass(frozen=True)
class LLMRunOptions:
    """Options for LLM-backed pre-analysis."""

    backend: ModelBackend = ModelBackend.OPENAI
    temperature: float = 0.1


class LLMPreAnalysisAgent(PreAnalysisAgent):
    """One LLM-backed pre-analysis agent with deterministic schema parsing."""

    def __init__(self, agent_name: AgentName, fallback_agent: PreAnalysisAgent, options: LLMRunOptions | None = None):
        self.agent_name = agent_name
        self.fallback_agent = fallback_agent
        self.options = options or LLMRunOptions()

    def run(self, snapshot: Snapshot) -> Stance:
        """Run LLM generation, fallback to stub on any failure."""

        if self.options.backend != ModelBackend.OPENAI:
            return self.fallback_agent.run(snapshot)

        trace = TraceLogger(os.getenv("LLM_TRACE_PATH"))
        try:
            config = load_openai_config()
            system_prompt = get_system_prompt(self.agent_name, snapshot)
            user_prompt = self._build_user_prompt(snapshot)
            candidates = get_agent_model_candidates(self.agent_name, self.options.backend)
        except Exception as exc:
            fallback = self.fallback_agent.run(snapshot)
            trace.log(
                "llm_agent_response",
                {
                    "agent": self.agent_name.value,
                    "backend": self.options.backend.value,
                    "errors": [{"stage": "prepare", "error": str(exc)}],
                    "fallback_used": True,
                    "fallback_stance": fallback.model_dump(),
                },
            )
            return fallback

        errors: list[dict[str, str]] = []

        for model in candidates:
            try:
                text = chat_completion(
                    config=config,
                    model=model,
                    system_prompt=system_prompt,
                    user_prompt=user_prompt,
                    temperature=self.options.temperature,
                )
                parsed = json.loads(text)
                parsed["agent_name"] = self.agent_name.value
                stance = Stance.model_validate(parsed)
                trace.log(
                    "llm_agent_response",
                    {
                        "agent": self.agent_name.value,
                        "model": model,
                        "backend": self.options.backend.value,
                        "system_prompt": system_prompt,
                        "user_prompt": user_prompt,
                        "raw_response": text,
                        "parsed": stance.model_dump(),
                        "fallback_used": False,
                    },
                )
                return stance
            except Exception as exc:
                error_text = str(exc)
                print(f"[llm][{self.agent_name.value}] model {model} failed: {error_text[:160]}")
                errors.append({"model": model, "error": error_text})

        fallback = self.fallback_agent.run(snapshot)
        trace.log(
            "llm_agent_response",
            {
                "agent": self.agent_name.value,
                "backend": self.options.backend.value,
                "errors": errors,
                "fallback_used": True,
                "fallback_stance": fallback.model_dump(),
            },
        )
        return fallback

    def _build_user_prompt(self, snapshot: Snapshot) -> str:
        return json.dumps(
            {
                "snapshot": snapshot.model_dump(),
                "instruction": "Generate one stance JSON for this agent.",
                "allowed_evidence_ids": [
                    "snapshot.market_summary.note",
                    "snapshot.market_summary.usdkrw",
                    "snapshot.market_summary.kospi_change_pct",
                    "snapshot.flow_summary.note",
                    "snapshot.sector_moves",
                    "snapshot.news_headlines",
                    "snapshot.watchlist",
                ],
            },
            ensure_ascii=False,
        )
