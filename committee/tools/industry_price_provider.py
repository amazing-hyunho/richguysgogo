from __future__ import annotations

"""Phase 1-A price provider interface for the industry cycle tracker.

Design goals (docs/industry_cycle_mvp_design.md sections 4.1, 5.1, 12, 14):
- Free-provider-first, same internal record shape regardless of provider
  ("무료 공급자와 유료 공급자는 같은 내부 레코드 형식으로 변환한다").
- One provider's failure must never break the caller's loop over other
  assets, and must never propagate up into the nightly pipeline
  ("공급자 실패가 기존 야간 파이프라인을 중단하지 않도록 격리"). Concrete
  providers are allowed to raise `PriceFetchError` (or let underlying
  exceptions bubble); callers that need fail-safe behavior use
  `safe_fetch_daily_prices` below, mirroring the `safe_*` wrapper pattern in
  `committee/core/database.py`.

This module intentionally makes no real network calls during import or at
module load time. `YahooChartPriceProvider` only performs an HTTP request
when `fetch_daily_prices()` is explicitly invoked by a caller (e.g. the
backfill CLI with `--execute`).
"""

from abc import ABC, abstractmethod
from datetime import UTC, date, datetime, timedelta
from typing import Any, List, Tuple
from urllib.parse import quote

from committee.industry_cycle.price_models import AssetPriceRecord


class PriceFetchError(RuntimeError):
    """Raised when a provider cannot produce price rows for a request."""


class IndustryPriceProvider(ABC):
    """Minimal interface every price provider (free or paid) must implement."""

    name: str = "unknown"

    @abstractmethod
    def fetch_daily_prices(
        self,
        *,
        asset_id: str,
        symbol: str,
        market: str,
        currency: str,
        start: str,
        end: str,
    ) -> List[AssetPriceRecord]:
        """Return daily OHLCV rows for `symbol` between `start`/`end` (inclusive).

        Implementations should raise `PriceFetchError` (or let a descriptive
        exception propagate) on failure rather than silently returning an
        empty list, so callers can distinguish "no data in range" from
        "the provider call failed."
        """


class YahooChartPriceProvider(IndustryPriceProvider):
    """Free-tier provider using the public Yahoo Finance chart API.

    Reuses the same endpoint/response shape as
    `scripts/backfill_market_daily_history.py`, but additionally reads the
    `indicators.adjclose` series so both raw and corporate-action-adjusted
    closes are captured (design doc 5.1: "기업행동 조정 여부를 명시한다").

    Availability policy (`available_at`)
    -------------------------------------
    Yahoo's daily bar for `trade_date` is not actually knowable until that
    trading day's session has closed. This provider does not model
    per-market close times or holiday calendars, so it uses a single
    conservative rule for every asset: **`available_at` = end of
    `trade_date` (23:59:59 UTC)** — i.e. "available after that trading day
    ends," per the task's documented conservative options. This is
    deliberately independent of wall-clock fetch time, so backfilling a
    2015 row in 2026 still yields `available_at=2015-...`, not
    `2026-...` (see `committee.industry_cycle.price_repository` for why that
    distinction matters). `collected_at` remains the real fetch wall-clock
    (`datetime.now(UTC)`), used for audit/freshness only.
    """

    name = "yahoo_chart"

    _CHART_BASE = "https://query1.finance.yahoo.com/v8/finance/chart"

    def fetch_daily_prices(
        self,
        *,
        asset_id: str,
        symbol: str,
        market: str,
        currency: str,
        start: str,
        end: str,
    ) -> List[AssetPriceRecord]:
        import requests  # local import: keep this module import-safe without requests at load time

        start_d = date.fromisoformat(str(start))
        end_d = date.fromisoformat(str(end))
        if end_d < start_d:
            raise PriceFetchError(f"end ({end}) is before start ({start})")

        start_epoch = int(
            datetime.combine(start_d - timedelta(days=7), datetime.min.time(), tzinfo=UTC).timestamp()
        )
        end_epoch = int(
            datetime.combine(end_d + timedelta(days=1), datetime.min.time(), tzinfo=UTC).timestamp()
        )
        encoded = quote(symbol, safe="")
        url = f"{self._CHART_BASE}/{encoded}"

        try:
            response = requests.get(
                url,
                params={"interval": "1d", "period1": start_epoch, "period2": end_epoch},
                timeout=12,
                headers={"User-Agent": "DailyAIInvestmentCommittee/1.0"},
            )
        except Exception as exc:  # noqa: BLE001
            raise PriceFetchError(f"http_request_failed[{symbol}]: {exc}") from exc

        if response.status_code != 200:
            raise PriceFetchError(f"http_status_{response.status_code}[{symbol}]")

        try:
            payload = response.json()
        except Exception as exc:  # noqa: BLE001
            raise PriceFetchError(f"invalid_json[{symbol}]: {exc}") from exc

        result = ((payload.get("chart") or {}).get("result") or [])
        if not result:
            raise PriceFetchError(f"empty_result[{symbol}]")
        item = result[0] or {}
        timestamps = item.get("timestamp") or []
        indicators = item.get("indicators") or {}
        quote_block = ((indicators.get("quote") or [{}])[0]) or {}
        adjclose_block = ((indicators.get("adjclose") or [{}])[0]) or {}

        opens = quote_block.get("open") or []
        highs = quote_block.get("high") or []
        lows = quote_block.get("low") or []
        closes = quote_block.get("close") or []
        volumes = quote_block.get("volume") or []
        adj_closes = adjclose_block.get("adjclose") or []

        if not timestamps or not closes:
            raise PriceFetchError(f"missing_series_data[{symbol}]")

        collected_at = datetime.now(UTC).isoformat()
        records: dict[str, AssetPriceRecord] = {}
        for idx, ts in enumerate(timestamps):
            close = closes[idx] if idx < len(closes) else None
            if close is None:
                continue
            trade_d = datetime.fromtimestamp(int(ts), UTC).date().isoformat()
            if trade_d < start_d.isoformat() or trade_d > end_d.isoformat():
                continue

            adj_close = adj_closes[idx] if idx < len(adj_closes) else None
            adjustment_status = "adjusted" if adj_close is not None else "unknown"
            records[trade_d] = AssetPriceRecord(
                asset_id=asset_id,
                market=market,
                currency=currency,
                trade_date=trade_d,
                open_price=_num_or_none(opens[idx] if idx < len(opens) else None),
                high_price=_num_or_none(highs[idx] if idx < len(highs) else None),
                low_price=_num_or_none(lows[idx] if idx < len(lows) else None),
                close_price=_num_or_none(close),
                adj_close_price=_num_or_none(adj_close),
                volume=_num_or_none(volumes[idx] if idx < len(volumes) else None),
                adjustment_status=adjustment_status,
                source=self.name,
                source_ref=symbol,
                available_at=_end_of_day_utc(trade_d),
                collected_at=collected_at,
            )
        return [records[d] for d in sorted(records.keys())]


def _num_or_none(value: Any) -> float | None:
    if value is None:
        return None
    try:
        f = float(value)
    except (TypeError, ValueError):
        return None
    return f


def _end_of_day_utc(trade_date: str) -> str:
    """Conservative `available_at` for one daily bar: 23:59:59 UTC on `trade_date`.

    Deterministic function of `trade_date` alone (never wall-clock "now"),
    so re-fetching or backfilling the same trading day always derives the
    same `available_at` regardless of when the fetch actually happens.
    """
    return f"{trade_date}T23:59:59+00:00"


def safe_fetch_daily_prices(
    provider: IndustryPriceProvider,
    *,
    asset_id: str,
    symbol: str,
    market: str,
    currency: str,
    start: str,
    end: str,
) -> Tuple[List[AssetPriceRecord], str | None]:
    """Fail-safe wrapper: never raises, returns `([], reason)` on any failure.

    Mirrors the `safe_upsert_*` wrapper pattern in `committee/core/database.py`
    so provider outages cannot break a caller that must keep running (design
    doc 14: "데이터 장애 -> 신뢰도 하향, 판정 보류, 품질 이벤트 기록", and
    section 12 Phase 1-A item 8: "공급자 실패가 기존 야간 파이프라인을
    중단하지 않도록 격리").
    """
    try:
        records = provider.fetch_daily_prices(
            asset_id=asset_id, symbol=symbol, market=market, currency=currency, start=start, end=end
        )
        return records, None
    except Exception as exc:  # noqa: BLE001 - isolation boundary, must not raise
        return [], str(exc)
