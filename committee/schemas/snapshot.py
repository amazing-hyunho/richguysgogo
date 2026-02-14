from __future__ import annotations

# Snapshot schema for shared daily facts.

from typing import Annotated, Optional

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


class KoreanFlowInvestors(BaseModel):
    """Korean market investor net buying (억원, 순매수)."""

    individual: int
    foreign: int
    institution: int

    class Config:
        extra = "forbid"


class KoreanMarketFlow(BaseModel):
    """KOSPI/KOSDAQ investor flow breakdown (optional).

    This is produced by PyKRX and attached to snapshot for report rendering.
    Keys are stable: `market` contains "KOSPI" and "KOSDAQ".
    """

    date: ShortText  # YYYY-MM-DD
    market: dict[str, KoreanFlowInvestors]

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


class MarketsVolatility(BaseModel):
    """Volatility metrics (best-effort)."""
    vix: float

    class Config:
        extra = "forbid"


class Markets(BaseModel):
    """Aggregated global markets for report display."""
    kr: MarketsKR
    us: MarketsUS
    fx: MarketsFX
    volatility: MarketsVolatility

    class Config:
        extra = "forbid"


class MacroDaily(BaseModel):
    """Phase 1: Daily macro indicators (best-effort; missing values are NULL)."""
    us10y: Optional[float] = None
    us2y: Optional[float] = None
    spread_2_10: Optional[float] = None
    vix: Optional[float] = None
    dxy: Optional[float] = None
    usdkrw: Optional[float] = None

    class Config:
        extra = "forbid"


class MacroMonthly(BaseModel):
    """Phase 2: Monthly macro indicators (best-effort; missing values are NULL)."""
    unemployment_rate: Optional[float] = None
    cpi_yoy: Optional[float] = None
    core_cpi_yoy: Optional[float] = None
    pce_yoy: Optional[float] = None
    pmi: Optional[float] = None
    # Wage series clarification:
    # - CES0500000003 is a *level* series (average hourly earnings), not a growth rate.
    #   We keep `wage_growth` for backward compatibility, but it mirrors `wage_level`.
    wage_growth: Optional[float] = None  # backward compatible alias of wage_level
    wage_level: Optional[float] = None
    wage_yoy: Optional[float] = None

    class Config:
        extra = "forbid"


class MacroQuarterly(BaseModel):
    """Phase 3: Quarterly macro indicators (best-effort; missing values are NULL)."""
    real_gdp: Optional[float] = None
    gdp_qoq_annualized: Optional[float] = None

    class Config:
        extra = "forbid"


class MacroStructural(BaseModel):
    """Phase 4: Structural indicators (best-effort).

    - Fed funds rate: policy rate target proxy.
    - Real rate: (nominal 10Y yield - 10Y breakeven inflation) when both available.
    """
    fed_funds_rate: Optional[float] = None
    real_rate: Optional[float] = None

    class Config:
        extra = "forbid"

# --- Macro data foundation (optional; snapshot.json remains backward compatible). ---


class Macro(BaseModel):
    """Macro data bundle (Phase 1 daily + Phase 2 monthly + Phase 3 quarterly + Phase 4 structural)."""
    daily: MacroDaily = Field(default_factory=MacroDaily)
    monthly: MacroMonthly = Field(default_factory=MacroMonthly)
    quarterly: MacroQuarterly = Field(default_factory=MacroQuarterly)
    structural: MacroStructural = Field(default_factory=MacroStructural)

    class Config:
        extra = "forbid"


class Snapshot(BaseModel):
    """Single shared fact packet for the daily meeting."""

    market_summary: MarketSummary = Field(..., description="Compact market summary.")
    flow_summary: FlowSummary = Field(..., description="Supply-demand flow summary.")
    korean_market_flow: Optional[KoreanMarketFlow] = Field(
        default=None,
        description="Korean market flow breakdown (PyKRX): KOSPI/KOSDAQ x investor net buying (억원).",
    )
    sector_moves: SectorMoves = Field(..., description="Sector movement highlights.")
    news_headlines: NewsHeadlines = Field(..., description="News headlines.")
    watchlist: Watchlist = Field(..., description="Symbols to monitor.")
    markets: Markets = Field(..., description="Global markets: KR/US indices and FX.")
    macro: Optional[Macro] = Field(default=None, description="Macro indicators (daily/monthly/quarterly/forward).")

    class Config:
        extra = "forbid"
