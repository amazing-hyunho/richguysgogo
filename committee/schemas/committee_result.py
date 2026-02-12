from __future__ import annotations

# Committee result schema for consensus output.

from enum import Enum
from typing import Annotated

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

    class Config:
        extra = "forbid"
