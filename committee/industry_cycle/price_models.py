from __future__ import annotations

"""Phase 1-A data model for the common KR/US asset price contract.

Mirrors `asset_price_daily` in `committee/core/database.py`. This is the
single price shape shared by KR stocks, US stocks, and ETFs from both
countries (design doc section 9: "asset_price_daily: KR/US 공통 가격").

No scoring/signal fields are defined here — those belong to Phase 1-B+.
"""

from dataclasses import dataclass
from typing import Optional

VALID_MARKETS = {"KR", "US"}
VALID_CURRENCIES = {"KRW", "USD"}
VALID_ADJUSTMENT_STATUSES = {"adjusted", "unadjusted", "unknown"}


@dataclass(frozen=True)
class AssetPriceRecord:
    """One daily OHLCV price row for one asset (stock, ETF, or index proxy).

    Field semantics:
    - `close_price`: the raw/unadjusted close as originally printed.
    - `adj_close_price`: the corporate-action-adjusted close (splits,
      dividends, ...). May be `None` when a provider does not supply it.
    - `adjustment_status`: explicit statement of what this row represents —
      `'adjusted'` when `adj_close_price` reflects corporate actions,
      `'unadjusted'` when only the raw close is known reliable, `'unknown'`
      when the provider's adjustment behavior could not be determined.
      Required per design doc 5.1 ("기업행동 조정 여부를 명시한다").
    - `available_at`: when this price became available in the market — a
      deterministic function of `trade_date` (plus the provider's
      availability policy), NOT of when we happened to run the backfill.
      All point-in-time reads gate on `trade_date <= as_of` AND
      `available_at <= as_of` (design doc 5.1). If omitted, the repository
      layer conservatively defaults it to end-of-day UTC on `trade_date`.
    - `collected_at`: when our system actually fetched/wrote this row.
      Audit/data-freshness only — never used for leakage gating. Re-fetching
      the same `(asset_id, trade_date)` is expected to refresh this field
      while leaving `available_at` untouched (see `price_repository`).
    - Missing numeric fields are `None`, never `0.0`.
    """

    asset_id: str
    market: str  # 'KR' | 'US'
    currency: str  # 'KRW' | 'USD'
    trade_date: str
    open_price: Optional[float] = None
    high_price: Optional[float] = None
    low_price: Optional[float] = None
    close_price: Optional[float] = None
    adj_close_price: Optional[float] = None
    volume: Optional[float] = None
    adjustment_status: str = "unknown"
    source: Optional[str] = None
    source_ref: Optional[str] = None
    available_at: Optional[str] = None
    collected_at: Optional[str] = None

    def __post_init__(self) -> None:
        if self.market not in VALID_MARKETS:
            raise ValueError(f"invalid market: {self.market!r} (expected one of {sorted(VALID_MARKETS)})")
        if self.currency not in VALID_CURRENCIES:
            raise ValueError(
                f"invalid currency: {self.currency!r} (expected one of {sorted(VALID_CURRENCIES)})"
            )
        if self.adjustment_status not in VALID_ADJUSTMENT_STATUSES:
            raise ValueError(
                f"invalid adjustment_status: {self.adjustment_status!r} "
                f"(expected one of {sorted(VALID_ADJUSTMENT_STATUSES)})"
            )
