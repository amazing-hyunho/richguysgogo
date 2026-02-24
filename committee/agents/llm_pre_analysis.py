from __future__ import annotations

"""LLM-backed pre-analysis agents with schema-safe fallback."""

import json
import os
from dataclasses import dataclass

from committee.agents.base import PreAnalysisAgent
from committee.agents.model_profiles import ModelBackend, get_agent_model_map
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
            model = get_agent_model_map(self.options.backend)[self.agent_name]
            config = load_openai_config()
            system_prompt = get_system_prompt(self.agent_name, snapshot)
            user_prompt = self._build_user_prompt(snapshot)
            last_error: Exception | None = None
            model_used: str | None = None
            response_text: str | None = None

            for candidate_model in self._build_model_candidates(model):
                try:
                    response_text = chat_completion(
                        config=config,
                        model=candidate_model,
                        system_prompt=system_prompt,
                        user_prompt=user_prompt,
                        temperature=self.options.temperature,
                    )
                    model_used = candidate_model
                    break
                except Exception as exc:
                    last_error = exc
                    if self._is_model_access_error(exc):
                        continue
                    raise

            if response_text is None:
                raise RuntimeError(f"openai_model_resolution_failed: {last_error}")

            parsed = json.loads(response_text)
            parsed["agent_name"] = self.agent_name.value
            stance = Stance.model_validate(parsed)
            trace.log(
                "llm_agent_response",
                {
                    "agent": self.agent_name.value,
                    "model": model_used,
                    "backend": self.options.backend.value,
                    "system_prompt": system_prompt,
                    "user_prompt": user_prompt,
                    "raw_response": response_text,
                    "parsed": stance.model_dump(),
                    "fallback_used": False,
                },
            )
            return stance
        except Exception as exc:
            fallback = self.fallback_agent.run(snapshot)
            trace.log(
                "llm_agent_response",
                {
                    "agent": self.agent_name.value,
                    "backend": self.options.backend.value,
                    "error": str(exc),
                    "fallback_used": True,
                    "fallback_stance": fallback.model_dump(),
                },
            )
            return fallback

    def _build_model_candidates(self, default_model: str) -> list[str]:
        candidates: list[str] = []

        per_agent = os.getenv(f"OPENAI_MODEL_{self.agent_name.value.upper()}", "").strip()
        global_default = os.getenv("OPENAI_MODEL", "").strip()
        extra = [item.strip() for item in os.getenv("OPENAI_FALLBACK_MODELS", "gpt-4.1,gpt-4.1-mini,gpt-4o,gpt-4o-mini").split(",")]

        for value in [per_agent, global_default, default_model, *extra]:
            if value and value not in candidates:
                candidates.append(value)
        return candidates

    @staticmethod
    def _is_model_access_error(error: Exception) -> bool:
        message = str(error)
        return "openai_http_403" in message and "does not have access to model" in message

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
