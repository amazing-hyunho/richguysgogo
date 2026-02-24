from __future__ import annotations

# Stance schema for per-agent pre-analysis.

from enum import Enum
from typing import Annotated, Optional

from pydantic import BaseModel, Field, constr


ShortText = constr(strip_whitespace=True, min_length=1, max_length=200)
KoreanComment = constr(strip_whitespace=True, min_length=1, max_length=120)
RawResponse = constr(strip_whitespace=False, min_length=1, max_length=4000)
IdToken = constr(
    strip_whitespace=True,
    min_length=1,
    max_length=60,
    pattern=r"^snapshot\.[a-z_]+(\.[a-z_]+)*$",
)

CoreClaims = Annotated[list[ShortText], Field(min_length=1, max_length=3)]
EvidenceIds = Annotated[list[IdToken], Field(min_length=1, max_length=10)]


class RegimeTag(str, Enum):
    """Market regime tag."""
    RISK_ON = "RISK_ON"
    NEUTRAL = "NEUTRAL"
    RISK_OFF = "RISK_OFF"


class ConfidenceLevel(str, Enum):
    """Confidence level for stance."""
    LOW = "LOW"
    MED = "MED"
    HIGH = "HIGH"


class AgentName(str, Enum):
    """Agent identifier."""
    MACRO = "macro"
    FLOW = "flow"
    SECTOR = "sector"
    RISK = "risk"


class Stance(BaseModel):
    """Pre-analysis results per agent."""

    agent_name: AgentName = Field(..., description="Agent identifier.")
    core_claims: CoreClaims = Field(..., description="Key claims (max 3 lines).")
    korean_comment: KoreanComment = Field(..., description="One-line Korean comment.")
    raw_response: Optional[RawResponse] = Field(
        default=None,
        description="Raw LLM response text (JSON string).",
    )
    regime_tag: RegimeTag = Field(..., description="Market regime tag.")
    evidence_ids: EvidenceIds = Field(..., description="Evidence ID list.")
    confidence: ConfidenceLevel = Field(..., description="Confidence level.")

    class Config:
        extra = "forbid"
