from __future__ import annotations

"""Agent model profile recommendations.

This module centralizes per-agent model preferences so we can start with GPT
and switch to free local models later without touching agent logic.
"""

from dataclasses import dataclass
from enum import Enum

from committee.schemas.stance import AgentName


class ModelBackend(str, Enum):
    """Supported backend families for model selection."""

    OPENAI = "openai"
    LOCAL = "local"


@dataclass(frozen=True)
class AgentModelProfile:
    """Recommended model set for one pre-analysis agent."""

    agent: AgentName
    openai_model: str
    local_model: str
    rationale: str


# Default recommendations:
# - Start with GPT models for quality/stability.
# - Keep local free-model equivalents ready for later cost control.
AGENT_MODEL_PROFILES: dict[AgentName, AgentModelProfile] = {
    AgentName.MACRO: AgentModelProfile(
        agent=AgentName.MACRO,
        openai_model="gpt-4.1",
        local_model="Qwen/Qwen2.5-32B-Instruct",
        rationale="보수적 추론과 불확실성 표현 안정성을 우선.",
    ),
    AgentName.FLOW: AgentModelProfile(
        agent=AgentName.FLOW,
        openai_model="gpt-4.1",
        local_model="Qwen/Qwen2.5-14B-Instruct",
        rationale="수치/문맥 매핑 정확도와 처리비용 균형.",
    ),
    AgentName.SECTOR: AgentModelProfile(
        agent=AgentName.SECTOR,
        openai_model="gpt-4.1",
        local_model="meta-llama/Llama-3.1-8B-Instruct",
        rationale="키워드 분류 중심 업무라 경량 모델 효율이 높음.",
    ),
    AgentName.RISK: AgentModelProfile(
        agent=AgentName.RISK,
        openai_model="gpt-4.1",
        local_model="Qwen/Qwen2.5-32B-Instruct",
        rationale="과민탐지 억제를 위해 precision 우선 모델을 배치.",
    ),
}


def get_agent_model_map(backend: ModelBackend = ModelBackend.OPENAI) -> dict[AgentName, str]:
    """Return the selected model name per agent for a backend."""

    if backend == ModelBackend.OPENAI:
        return {agent: profile.openai_model for agent, profile in AGENT_MODEL_PROFILES.items()}
    if backend == ModelBackend.LOCAL:
        return {agent: profile.local_model for agent, profile in AGENT_MODEL_PROFILES.items()}
    raise ValueError(f"Unsupported backend: {backend}")


def parse_backend(value: str | None) -> ModelBackend:
    """Parse backend string safely with OPENAI default."""

    if not value:
        return ModelBackend.OPENAI
    normalized = value.strip().lower()
    if normalized in {ModelBackend.OPENAI.value, "gpt"}:
        return ModelBackend.OPENAI
    if normalized in {ModelBackend.LOCAL.value, "hf", "ollama"}:
        return ModelBackend.LOCAL
    return ModelBackend.OPENAI
