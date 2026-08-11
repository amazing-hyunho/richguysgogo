from __future__ import annotations

"""Minimal OpenAI Chat Completions API client via requests."""

import json
import os
from dataclasses import dataclass

@dataclass(frozen=True)
class OpenAIConfig:
    """Runtime config for OpenAI-compatible chat endpoint."""

    api_key: str
    base_url: str = "https://api.openai.com/v1"


@dataclass(frozen=True)
class ChatCompletionResult:
    content: str
    model: str | None
    input_tokens: int | None
    output_tokens: int | None


def load_openai_config() -> OpenAIConfig:
    """Load OpenAI config from environment variables."""

    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        raise ValueError("OPENAI_API_KEY is required for LLM agents.")
    base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1").strip()
    return OpenAIConfig(api_key=api_key, base_url=base_url)


def chat_completion(
    *,
    config: OpenAIConfig,
    model: str,
    system_prompt: str,
    user_prompt: str,
    temperature: float = 0.1,
    timeout: int = 30,
) -> str:
    """Call chat completions and return text content."""
    return chat_completion_with_metadata(
        config=config,
        model=model,
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        temperature=temperature,
        timeout=timeout,
    ).content


def chat_completion_with_metadata(
    *,
    config: OpenAIConfig,
    model: str,
    system_prompt: str,
    user_prompt: str,
    temperature: float = 0.1,
    timeout: int = 30,
) -> ChatCompletionResult:
    """Call chat completions and retain model/usage metadata for audit."""

    # Keep dry-runs, tests, and non-LLM commands importable even when optional
    # runtime dependencies have not been installed yet.
    import requests

    url = f"{config.base_url.rstrip('/')}/chat/completions"
    payload = {
        "model": model,
        "temperature": temperature,
        "response_format": {"type": "json_object"},
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    }
    response = requests.post(
        url,
        headers={
            "Authorization": f"Bearer {config.api_key}",
            "Content-Type": "application/json",
        },
        data=json.dumps(payload),
        timeout=timeout,
    )
    if response.status_code != 200:
        raise RuntimeError(f"openai_http_{response.status_code}: {response.text[:200]}")

    body = response.json()
    choices = body.get("choices", [])
    if not choices:
        raise RuntimeError("openai_no_choices")
    message = choices[0].get("message", {})
    content = message.get("content")
    if not content:
        raise RuntimeError("openai_empty_content")
    usage = body.get("usage") if isinstance(body.get("usage"), dict) else {}
    return ChatCompletionResult(
        content=str(content),
        model=str(body.get("model")) if body.get("model") else None,
        input_tokens=(
            int(usage["prompt_tokens"]) if usage.get("prompt_tokens") is not None else None
        ),
        output_tokens=(
            int(usage["completion_tokens"]) if usage.get("completion_tokens") is not None else None
        ),
    )
