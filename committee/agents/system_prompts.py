from __future__ import annotations

"""System prompt templates for per-agent LLM stance generation."""

from committee.schemas.snapshot import Snapshot
from committee.schemas.stance import AgentName


COMMON_OUTPUT_RULES = (
    "Output JSON only. No markdown. "
    "Required keys: agent_name, core_claims, regime_tag, evidence_ids, confidence. "
    "core_claims must be 1~3 short lines. "
    "regime_tag must be one of RISK_ON/NEUTRAL/RISK_OFF. "
    "confidence must be one of LOW/MED/HIGH. "
    "evidence_ids must use allowed snapshot paths only."
)

AGENT_BASE_SYSTEM_PROMPTS: dict[AgentName, str] = {
AGENT_SYSTEM_PROMPTS: dict[AgentName, str] = {
    AgentName.MACRO: (
        "You are the MACRO pre-analysis agent for an investment committee. "
        "Be conservative, explicitly acknowledge uncertainty, and avoid overconfident claims. "
        "Focus on macro regime interpretation from market_summary and macro context. "
        + COMMON_OUTPUT_RULES
    ),
    AgentName.FLOW: (
        "You are the FLOW pre-analysis agent. "
        "Map numeric flow context to directional interpretation with stable logic. "
        "Prefer consistency over creativity. "
        + COMMON_OUTPUT_RULES
    ),
    AgentName.SECTOR: (
        "You are the SECTOR pre-analysis agent. "
        "Perform keyword/sector signal classification and produce concise claims. "
        "Do not invent unseen sectors or tickers. "
        + COMMON_OUTPUT_RULES
    ),
    AgentName.RISK: (
        "You are the RISK pre-analysis agent. "
        "Precision is critical: avoid false alarms and overreaction. "
        "Only emit RISK_OFF when risk evidence is concrete. "
        + COMMON_OUTPUT_RULES
    ),
}


def _snapshot_context_block(snapshot: Snapshot) -> str:
    """Build a compact context block: indices + key indicators + headlines."""

    m = snapshot.markets
    top_headlines = snapshot.news_headlines[:20]
    headline_lines = "\n".join([f"- {item}" for item in top_headlines]) if top_headlines else "- (none)"

    return (
        "\n\nMarket Context (use this as primary evidence):\n"
        f"- KOSPI: {m.kr.kospi_pct:+.2f}%\n"
        f"- KOSDAQ: {m.kr.kosdaq_pct:+.2f}%\n"
        f"- S&P500: {m.us.sp500_pct:+.2f}%\n"
        f"- NASDAQ: {m.us.nasdaq_pct:+.2f}%\n"
        f"- DOW: {m.us.dow_pct:+.2f}%\n"
        f"- USD/KRW: {m.fx.usdkrw:.2f} ({m.fx.usdkrw_pct:+.2f}%)\n"
        f"- VIX: {m.volatility.vix:.2f}\n"
        f"- Market note: {snapshot.market_summary.note}\n"
        f"- Flow note: {snapshot.flow_summary.note}\n"
        "\nNews Headlines (up to 20):\n"
        f"{headline_lines}\n"
    )


def get_system_prompt(agent_name: AgentName, snapshot: Snapshot) -> str:
    """Return per-agent system prompt with live market/headline context."""

    base_prompt = AGENT_BASE_SYSTEM_PROMPTS[agent_name]
    return base_prompt + _snapshot_context_block(snapshot)
def get_system_prompt(agent_name: AgentName) -> str:
    """Return per-agent system prompt."""

    return AGENT_SYSTEM_PROMPTS[agent_name]
