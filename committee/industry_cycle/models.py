from __future__ import annotations

"""Phase 0 data model definitions for the industry cycle tracker.

These are thin, dependency-free dataclasses that mirror the DB rows created
in `committee/core/database.py`. They give the repository/data_quality/tests
one canonical field definition instead of passing loose dicts everywhere.

No scoring/signal fields are defined here — those belong to Phase 1+.
"""

from dataclasses import dataclass
from typing import Optional, Tuple


@dataclass(frozen=True)
class IndustryMaster:
    """Internal industry standard (`industry_id` is the only stable key).

    External classification codes (GICS, KRX, custom provider codes, ...)
    must never be used as the primary key directly; they are attached via
    `IndustryAlias` instead so classification-scheme changes don't break
    history.
    """

    industry_id: str
    name_kr: str
    name_en: Optional[str] = None
    country_scope: Tuple[str, ...] = ()
    coverage_status: Optional[str] = None  # 'OK' | 'INSUFFICIENT'
    active: bool = True
    notes: Optional[str] = None


@dataclass(frozen=True)
class IndustryAlias:
    """Maps one external classification code to an internal `industry_id`."""

    provider: str
    external_code: str
    industry_id: str
    valid_from: Optional[str] = None
    valid_to: Optional[str] = None


@dataclass(frozen=True)
class IndustryAssetMap:
    """Maps one asset (ETF or stock) to an internal `industry_id`."""

    asset_id: str
    industry_id: str
    asset_type: Optional[str] = None  # 'ETF' | 'STOCK'
    market: Optional[str] = None  # 'KR' | 'US'
    weight: Optional[float] = None
    valid_from: Optional[str] = None
    valid_to: Optional[str] = None


@dataclass(frozen=True)
class IndustryIndicatorMap:
    """Maps one indicator to the industry whose `fundamentals_score` it feeds.

    `direction` records whether a *higher* indicator value should raise
    ('positive') or lower ('negative') the industry's outlook, so scoring
    code (Phase 2+) can apply indicator-direction reversal without hardcoding
    per-indicator sign logic (design doc section 13: "지표 방향성 반전").
    """

    industry_id: str
    indicator_id: str
    direction: Optional[str] = None  # 'positive' | 'negative'
    weight: Optional[float] = None
    valid_from: Optional[str] = None
    valid_to: Optional[str] = None


@dataclass(frozen=True)
class ThemeIndustryMap:
    """Connects a theme (e.g. HBM, robotics) to its parent industry."""

    theme_id: str
    industry_id: str
    valid_from: Optional[str] = None
    valid_to: Optional[str] = None


@dataclass(frozen=True)
class IndicatorCatalogEntry:
    """Definition of one indicator series (not the observations themselves)."""

    indicator_id: str
    provider: Optional[str] = None
    series_id: Optional[str] = None
    unit: Optional[str] = None
    frequency: Optional[str] = None
    transform: Optional[str] = None
    description: Optional[str] = None
    baseline: Optional[float] = None
    """Neutral/typical raw value for this indicator (Phase 2), e.g. 50 for a diffusion
    index like PMI. `None` (not 0.0) means "no override": scoring treats it as 0.0,
    which is already correct for zero-centered transforms like yoy_pct/mom_pct."""


@dataclass(frozen=True)
class IndicatorObservation:
    """One point-in-time observation of an indicator series.

    Field semantics (design doc section 5.1 / 9):
    - observed_at: the reference period/date the value describes (e.g. the
      month-end a CPI print refers to). Required, never NULL.
    - value: the observed value. Stored as NULL (never 0.0) when missing.
    - published_at: the date the source first released this value officially.
      NULL when unknown (some providers do not expose it).
    - known_at: the timestamp our system became aware of / collected this
      value. This is the field backtests must gate on: `known_at <= signal_date`.
    - vintage_at: identifies which revision of `observed_at` this row is. When
      a provider revises a past observation, a *new* row is inserted with a
      later `vintage_at` rather than overwriting the original row — past
      signals are never silently rewritten by later revisions.
    """

    indicator_id: str
    observed_at: str
    value: Optional[float] = None
    published_at: Optional[str] = None
    known_at: Optional[str] = None
    vintage_at: Optional[str] = None
    source_ref: Optional[str] = None


@dataclass(frozen=True)
class DataQualityEvent:
    """One data-quality finding (missing data, lag, revision, anomaly, ...)."""

    event_type: str
    provider: Optional[str] = None
    target: Optional[str] = None
    severity: Optional[str] = None  # 'low' | 'medium' | 'high'
    status: str = "open"  # 'open' | 'resolved'
    message: Optional[str] = None
    detected_at: Optional[str] = None
