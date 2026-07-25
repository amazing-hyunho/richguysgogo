from __future__ import annotations

"""Phase 1-B: price-only signal backtest (pure logic, no DB/network access).

Design doc section 2 ("성과 지표") and task item 6. This module is
deliberately a SEPARATE code path from signal generation
(`price_features`/`price_scoring`/`price_state_machine`, all of which only
ever see `price_repository.get_prices_as_of(asset_id, as_of=signal_at)`
data): here we intentionally look FORWARD from `signal_at` using whatever
price history has since been recorded, because measuring what actually
happened after a signal is the entire point of a backtest. That is safe
specifically because it is never fed back into `classify_raw_state` /
`apply_confirmation_rule` -- the task constraint this module must honor is
"미래 가격은 성과 측정에만 사용하고 신호 계산에는 절대 사용하지 말 것", not
that this module can't see future prices at all.

Horizons are expressed in trading days (using the same
`return_windows_trading_days` convention as `price_features`) rather than
calendar months, so a horizon lookup is a simple, deterministic index
offset into the asset's own price series -- no calendar/holiday alignment
guesswork.
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Sequence

from committee.industry_cycle.price_features import PricePoint


def _find_index_for_date(series: Sequence[PricePoint], trade_date: str) -> Optional[int]:
    for i, point in enumerate(series):
        if point.trade_date == trade_date:
            return i
    return None


@dataclass(frozen=True)
class ForwardReturnResult:
    horizon_label: str
    horizon_trading_days: int
    signal_trade_date: str
    signal_price: float
    forward_trade_date: Optional[str]
    forward_price: Optional[float]
    asset_return: Optional[float]
    benchmark_return: Optional[float]
    excess_return: Optional[float]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "horizon_label": self.horizon_label,
            "horizon_trading_days": self.horizon_trading_days,
            "signal_trade_date": self.signal_trade_date,
            "signal_price": self.signal_price,
            "forward_trade_date": self.forward_trade_date,
            "forward_price": self.forward_price,
            "asset_return": self.asset_return,
            "benchmark_return": self.benchmark_return,
            "excess_return": self.excess_return,
        }


def compute_forward_returns(
    asset_series: Sequence[PricePoint],
    benchmark_series: Optional[Sequence[PricePoint]],
    *,
    signal_at: str,
    horizons: Dict[str, int],
) -> List[ForwardReturnResult]:
    """Compute forward asset/benchmark/excess returns at each horizon in `horizons`.

    `signal_at` MUST match an exact `trade_date` present in `asset_series`
    (the trade date the signal was actually generated on -- e.g.
    `WeeklyPriceFeatures.price_trade_date`). Returns an empty list if it
    isn't found (caller decides how to treat that as a data-quality issue).
    Each horizon whose forward point falls beyond the recorded history
    (i.e. "not enough time has passed yet") yields `None` return/price
    fields for that horizon, never a fabricated value.

    The benchmark's forward point is located by the SAME trading-day offset
    from the benchmark's own `signal_at`-matching index, not by matching
    calendar dates -- this deliberately tolerates the two countries' price
    series having slightly different trading calendars.
    """
    idx = _find_index_for_date(asset_series, signal_at)
    if idx is None:
        return []

    signal_price = asset_series[idx].price

    b_idx = _find_index_for_date(benchmark_series, signal_at) if benchmark_series else None
    b_signal_price = benchmark_series[b_idx].price if (b_idx is not None and benchmark_series) else None

    results: List[ForwardReturnResult] = []
    for label, days in horizons.items():
        fwd_idx = idx + days
        if fwd_idx < len(asset_series):
            forward_point = asset_series[fwd_idx]
            asset_return: Optional[float] = (
                forward_point.price / signal_price - 1.0 if signal_price else None
            )
            forward_price: Optional[float] = forward_point.price
            forward_trade_date: Optional[str] = forward_point.trade_date
        else:
            asset_return = None
            forward_price = None
            forward_trade_date = None

        benchmark_return: Optional[float] = None
        if b_idx is not None and b_signal_price:
            b_fwd_idx = b_idx + days
            if benchmark_series and b_fwd_idx < len(benchmark_series):
                benchmark_return = benchmark_series[b_fwd_idx].price / b_signal_price - 1.0

        excess_return: Optional[float] = (
            None if (asset_return is None or benchmark_return is None) else asset_return - benchmark_return
        )

        results.append(
            ForwardReturnResult(
                horizon_label=label,
                horizon_trading_days=days,
                signal_trade_date=signal_at,
                signal_price=signal_price,
                forward_trade_date=forward_trade_date,
                forward_price=forward_price,
                asset_return=asset_return,
                benchmark_return=benchmark_return,
                excess_return=excess_return,
            )
        )
    return results


def compute_mfe_mae(
    asset_series: Sequence[PricePoint],
    *,
    signal_at: str,
    max_horizon_trading_days: int,
) -> Dict[str, Optional[float]]:
    """Max favorable/adverse excursion over the `max_horizon_trading_days`
    window strictly after `signal_at`, expressed as pct vs. the signal price.

    `None`/`None` when `signal_at` isn't found or there is no post-signal
    history yet (never fabricated as 0.0).
    """
    idx = _find_index_for_date(asset_series, signal_at)
    if idx is None:
        return {"mfe": None, "mae": None}

    signal_price = asset_series[idx].price
    if not signal_price:
        return {"mfe": None, "mae": None}

    end_idx = min(idx + max_horizon_trading_days, len(asset_series) - 1)
    if end_idx <= idx:
        return {"mfe": None, "mae": None}

    window = asset_series[idx + 1 : end_idx + 1]
    if not window:
        return {"mfe": None, "mae": None}

    rets = [p.price / signal_price - 1.0 for p in window]
    return {"mfe": max(rets), "mae": min(rets)}


def summarize_performance(
    events: Sequence[Dict[str, Any]],
    *,
    horizon_label: str,
) -> Dict[str, Optional[float]]:
    """Aggregate win rate / average / median excess return across `events` at one horizon.

    `events` are plain dicts shaped like `ForwardReturnResult.to_dict()`.
    A "win" is `excess_return > 0` (design doc section 2: "적중률: 6개월
    초과수익률이 0보다 큰 신호의 비율", generalized here to any horizon).
    Events with a missing `excess_return` for the requested horizon are
    excluded from the aggregate rather than counted as a loss.
    """
    excess_values = [
        e["excess_return"]
        for e in events
        if e.get("horizon_label") == horizon_label and e.get("excess_return") is not None
    ]
    if not excess_values:
        return {"win_rate": None, "avg_excess_return": None, "median_excess_return": None, "n": 0}

    n = len(excess_values)
    wins = sum(1 for v in excess_values if v > 0)
    sorted_values = sorted(excess_values)
    if n % 2 == 1:
        median = sorted_values[n // 2]
    else:
        median = (sorted_values[n // 2 - 1] + sorted_values[n // 2]) / 2.0

    return {
        "win_rate": wins / n,
        "avg_excess_return": sum(excess_values) / n,
        "median_excess_return": median,
        "n": n,
    }
