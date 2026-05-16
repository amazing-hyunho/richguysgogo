from __future__ import annotations

# Committee result schema for consensus output.

from enum import Enum
from typing import Annotated, Optional

from pydantic import BaseModel, Field, constr


ShortText = constr(strip_whitespace=True, min_length=1, max_length=200)
SentenceText = constr(strip_whitespace=True, min_length=1, max_length=300)

SourceNames = Annotated[list[ShortText], Field(min_length=1, max_length=5)]


class KeyPoint(BaseModel):
    """Structured key point with sources."""
    point: ShortText
    sources: SourceNames

    class Config:
        extra = "forbid"


KeyPoints = Annotated[list[KeyPoint], Field(min_length=1, max_length=3)]


class Disagreement(BaseModel):
    """Structured disagreement entry."""
    topic: ShortText
    majority: ShortText
    minority: ShortText
    minority_agents: Annotated[list[ShortText], Field(min_length=1, max_length=5)]
    why_it_matters: ShortText

    class Config:
        extra = "forbid"


Disagreements = Annotated[list[Disagreement], Field(min_length=1, max_length=3)]


class OpsGuidanceLevel(str, Enum):
    """Operational guidance level."""
    OK = "OK"
    CAUTION = "CAUTION"
    AVOID = "AVOID"


class OpsGuidance(BaseModel):
    """Operational guidance item."""
    level: OpsGuidanceLevel
    text: ShortText

    class Config:
        extra = "forbid"


OpsGuidanceList = Annotated[list[OpsGuidance], Field(min_length=3, max_length=3)]


class CommitteeResult(BaseModel):
    """Consensus result from the meeting."""

    consensus: SentenceText = Field(
        ...,
        description="Single-sentence consensus.",
    )
    key_points: KeyPoints = Field(..., description="Up to 3 key points.")
    disagreements: Disagreements = Field(..., description="Up to 3 disagreements.")
    ops_guidance: OpsGuidanceList = Field(
        ...,
        description="Operational guidance list (non-binding).",
    )
    sugeup_narrative: Optional[str] = Field(
        default=None,
        description=(
            "Long-form Korean supply-demand narrative (수급 분석). "
            "3 sections: (1) 외국인 매도 이유, (2) 개인 매수 이유·리스크, (3) 시나리오·투자 결론. "
            "Plain text, no markdown. Max ~1500 chars."
        ),
    )

    class Config:
        extra = "forbid"
