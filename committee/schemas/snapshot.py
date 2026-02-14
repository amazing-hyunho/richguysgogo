from __future__ import annotations

# Snapshot schema for shared daily facts.

from typing import Annotated

from pydantic import BaseModel, Field, constr


ShortText = constr(strip_whitespace=True, min_length=1, max_length=200)
MediumText = constr(strip_whitespace=True, min_length=1, max_length=500)
Ticker = constr(strip_whitespace=True, min_length=1, max_length=12)

SectorMoves = Annotated[list[ShortText], Field(min_length=1, max_length=10)]
NewsHeadlines = Annotated[list[ShortText], Field(min_length=1, max_length=10)]
Watchlist = Annotated[list[Ticker], Field(min_length=1, max_length=50)]


class MarketSummary(BaseModel):
    """Structured market summary."""
    note: MediumText
    kospi_change_pct: float
    usdkrw: float

    class Config:
        extra = "forbid"


class FlowSummary(BaseModel):
    """Structured flow summary."""
    note: MediumText
    foreign_net: float
    institution_net: float
    retail_net: float

    class Config:
        extra = "forbid"


# --- Global markets: KR, US indices and FX (new top-level key, pipeline intact). ---


class MarketsKR(BaseModel):
    """Korean market daily percentage changes."""
    kospi_pct: float
    kosdaq_pct: float

    class Config:
        extra = "forbid"


class MarketsUS(BaseModel):
    """US market daily percentage changes."""
    sp500_pct: float
    nasdaq_pct: float
    dow_pct: float

    class Config:
        extra = "forbid"


class MarketsFX(BaseModel):
    """FX spot and daily percentage change."""
    usdkrw: float
    usdkrw_pct: float

    class Config:
        extra = "forbid"


class Markets(BaseModel):
    """Aggregated global markets for report display."""
    kr: MarketsKR
    us: MarketsUS
    fx: MarketsFX

    class Config:
        extra = "forbid"


class Snapshot(BaseModel):
    """Single shared fact packet for the daily meeting."""

    market_summary: MarketSummary = Field(..., description="Compact market summary.")
    flow_summary: FlowSummary = Field(..., description="Supply-demand flow summary.")
    sector_moves: SectorMoves = Field(..., description="Sector movement highlights.")
    news_headlines: NewsHeadlines = Field(..., description="News headlines.")
    watchlist: Watchlist = Field(..., description="Symbols to monitor.")
    markets: Markets = Field(..., description="Global markets: KR/US indices and FX.")

    class Config:
        extra = "forbid"
