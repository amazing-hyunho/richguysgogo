from __future__ import annotations

# Debate schemas for one-round meeting-minute discussion.

from typing import Annotated

from pydantic import BaseModel, Field, constr

from committee.schemas.stance import AgentName, IdToken, RegimeTag


ShortText = constr(strip_whitespace=True, min_length=1, max_length=240)


EvidenceIds = Annotated[list[IdToken], Field(min_length=1, max_length=8)]


class DebateMinute(BaseModel):
    """One meeting-minute line from an agent speaker."""

    speaker: AgentName
    speaker_label: ShortText
    summary: ShortText
    references: EvidenceIds
    internal_regime_tag: RegimeTag

    class Config:
        extra = "forbid"


DebateMinutes = Annotated[list[DebateMinute], Field(min_length=1, max_length=14)]


class DebateRound(BaseModel):
    """A single bounded meeting-minute round before final chair synthesis."""

    round_index: int = Field(..., ge=1, le=3)
    facilitator_note: ShortText
    minutes: DebateMinutes
    round_conclusion: ShortText

    class Config:
        extra = "forbid"
