from __future__ import annotations

"""Minimal OpenAI Chat Completions API client via requests."""

import json
import os
from dataclasses import dataclass

import requests


@dataclass(frozen=True)
class OpenAIConfig:
    """Runtime config for OpenAI-compatible chat endpoint."""

    api_key: str
    base_url: str = "https://api.openai.com/v1"


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
    return str(content)
