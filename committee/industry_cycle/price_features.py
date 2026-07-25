from __future__ import annotations

"""Phase 1-B: weekly price feature computation (pure, no DB/network access).

Design doc section 12 Phase 1 item 3 ("3·6·12개월 상대강도와 변동성 계산") and
the task's Phase 1-B spec item 1. Every function here operates on a plain
list of `asset_price_daily`-shaped dicts that the caller has ALREADY passed
through `price_repository.get_prices_as_of(asset_id, as_of)` -- this module
never queries the DB or accepts an `as_of` cutoff of its own, so there is no
way for it to reach past the caller-supplied point-in-time boundary
(design doc 5.1: "백테스트는 available_at <= signal_date인 데이터만 사용한다").

Adjusted-price-first policy (task item 1): `build_price_series` prefers
`adj_close_price` and explicitly falls back to the raw `close_price` per
row when the adjusted value is unavailable, recording which field was used
on every point so `data_completeness`/`price_field_used` never silently
hide the fallback.

NULL policy: every feature is `None` (never 0.0) when there is not enough
history to compute it -- see each function's window-length guard.
"""

import math
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Sequence

VALID_PRICE_FIELDS = {"adjusted", "raw_close_fallback"}


@dataclass(frozen=True)
class PricePoint:
    """One usable price observation (adjusted preferred, raw close fallback)."""

    trade_date: str
    price: float
    field_used: str  # 'adjusted' | 'raw_close_fallback'
    volume: Optional[float] = None


def _to_float(value: Any) -> Optional[float]:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def build_price_series(rows: Sequence[Dict[str, Any]]) -> List[PricePoint]:
    """Convert `asset_price_daily` rows into a sorted, gap-free usable series.

    A row contributes a point only if it has *some* usable price
    (`adj_close_price` preferred, `close_price` fallback). Rows with both
    NULL are skipped entirely rather than inserted as a gap value, since
    there is nothing meaningful to fall back to.
    """
    ordered = sorted(rows, key=lambda r: str(r.get("trade_date") or ""))
    points: List[PricePoint] = []
    for row in ordered:
        trade_date = row.get("trade_date")
        if not trade_date:
            continue
        adj = _to_float(row.get("adj_close_price"))
        if adj is not None:
            points.append(
                PricePoint(trade_date=str(trade_date), price=adj, field_used="adjusted", volume=_to_float(row.get("volume")))
            )
            continue
        close = _to_float(row.get("close_price"))
        if close is not None:
            points.append(
                PricePoint(
                    trade_date=str(trade_date), price=close, field_used="raw_close_fallback", volume=_to_float(row.get("volume"))
                )
            )
    return points


def summarize_price_field_used(series: Sequence[PricePoint]) -> Optional[str]:
    """Return 'adjusted' iff every point used the adjusted close, else
    'raw_close_fallback' iff at least one point fell back to the raw close.
    `None` for an empty series (nothing to summarize)."""
    if not series:
        return None
    if any(p.field_used == "raw_close_fallback" for p in series):
        return "raw_close_fallback"
    return "adjusted"


def _return_over_window(series: Sequence[PricePoint], window_days: int) -> Optional[float]:
    if len(series) <= window_days:
        return None
    current = series[-1].price
    past = series[-1 - window_days].price
    if past == 0:
        return None
    return current / past - 1.0


def compute_returns(series: Sequence[PricePoint], windows: Dict[str, int]) -> Dict[str, Optional[float]]:
    """Return `{label: pct_return_or_None}` for each `windows` entry (e.g. '1m' -> 21)."""
    return {label: _return_over_window(series, days) for label, days in windows.items()}


def compute_relative_returns(
    asset_returns: Dict[str, Optional[float]],
    benchmark_returns: Dict[str, Optional[float]],
    labels: Sequence[str],
) -> Dict[str, Optional[float]]:
    """Return `{f"rel_return_{label}": asset - benchmark}`, `None` if either leg is missing."""
    out: Dict[str, Optional[float]] = {}
    for label in labels:
        a = asset_returns.get(label)
        b = benchmark_returns.get(label)
        out[f"rel_return_{label}"] = None if (a is None or b is None) else (a - b)
    return out


def moving_average(series: Sequence[PricePoint], window: int) -> Optional[float]:
    """Simple moving average of the last `window` prices, `None` if too short."""
    if len(series) < window:
        return None
    values = [p.price for p in series[-window:]]
    return sum(values) / len(values)


def compute_moving_averages(series: Sequence[PricePoint], windows: Sequence[int]) -> Dict[int, Optional[float]]:
    return {w: moving_average(series, w) for w in windows}


def daily_returns(series: Sequence[PricePoint]) -> List[float]:
    rets: List[float] = []
    for i in range(1, len(series)):
        prev = series[i - 1].price
        cur = series[i].price
        if prev:
            rets.append(cur / prev - 1.0)
    return rets


def volatility(series: Sequence[PricePoint], window: int) -> Optional[float]:
    """Population stdev of daily returns over the last `window` trading days.

    Requires `window + 1` price points (to derive `window` daily returns);
    `None` when there is not enough history.
    """
    if len(series) < window + 1:
        return None
    recent = series[-(window + 1):]
    rets = daily_returns(recent)
    if len(rets) < window:
        return None
    mean = sum(rets) / len(rets)
    var = sum((r - mean) ** 2 for r in rets) / len(rets)
    return math.sqrt(var)


def drawdown_from_high(series: Sequence[PricePoint], window: int) -> Optional[float]:
    """`current_price / max(price over last `window` days) - 1` (<=0), `None` if too short."""
    if len(series) < window:
        return None
    recent = series[-window:]
    high = max(p.price for p in recent)
    if high == 0:
        return None
    return series[-1].price / high - 1.0


def compute_volume_change(series: Sequence[PricePoint], *, recent_window: int, prior_window: int) -> Optional[float]:
    """Recent avg volume vs. the immediately preceding prior-window avg volume, as pct change.

    `None` when there isn't `recent_window + prior_window` days of history,
    or when volume is missing across an entire sub-window.
    """
    total_needed = recent_window + prior_window
    if len(series) < total_needed:
        return None
    recent = series[-recent_window:]
    prior = series[-total_needed:-recent_window]
    recent_vols = [p.volume for p in recent if p.volume is not None]
    prior_vols = [p.volume for p in prior if p.volume is not None]
    if not recent_vols or not prior_vols:
        return None
    recent_avg = sum(recent_vols) / len(recent_vols)
    prior_avg = sum(prior_vols) / len(prior_vols)
    if prior_avg == 0:
        return None
    return recent_avg / prior_avg - 1.0


def compute_below_ma_ratio(current_price: Optional[float], mas: Dict[int, Optional[float]]) -> Optional[float]:
    """Fraction of *available* moving averages that `current_price` sits below.

    `None` when `current_price` or every MA is missing -- never coerced to 0.
    """
    if current_price is None:
        return None
    available = [ma for ma in mas.values() if ma is not None and ma != 0]
    if not available:
        return None
    below = sum(1 for ma in available if current_price < ma)
    return below / len(available)


def _gap(current_price: Optional[float], ma: Optional[float]) -> Optional[float]:
    """`current_price / ma - 1`, `None` if either side is missing (used for *_gap features)."""
    if current_price is None or ma is None or ma == 0:
        return None
    return current_price / ma - 1.0


_EXPECTED_FEATURE_SLOTS = (
    "return_1m",
    "return_3m",
    "return_6m",
    "return_12m",
    "rel_return_3m",
    "rel_return_6m",
    "rel_return_12m",
    "ma20",
    "ma60",
    "ma120",
    "ma200",
    "drawdown_from_52w_high",
    "vol_20d",
    "vol_60d",
    "volume_change",
)


@dataclass(frozen=True)
class WeeklyPriceFeatures:
    """All raw, explainable inputs computed for one asset as of one `as_of` date."""

    asset_id: str
    market: str
    benchmark_asset_id: Optional[str]
    as_of: str
    price_trade_date: Optional[str]
    price_field_used: Optional[str]
    current_price: Optional[float]
    n_observations: int
    return_1m: Optional[float] = None
    return_3m: Optional[float] = None
    return_6m: Optional[float] = None
    return_12m: Optional[float] = None
    rel_return_3m: Optional[float] = None
    rel_return_6m: Optional[float] = None
    rel_return_12m: Optional[float] = None
    ma20: Optional[float] = None
    ma60: Optional[float] = None
    ma120: Optional[float] = None
    ma200: Optional[float] = None
    ma20_gap: Optional[float] = None
    ma60_gap: Optional[float] = None
    ma120_gap: Optional[float] = None
    ma200_gap: Optional[float] = None
    drawdown_from_52w_high: Optional[float] = None
    vol_20d: Optional[float] = None
    vol_60d: Optional[float] = None
    volume_change: Optional[float] = None
    below_ma_ratio: Optional[float] = None
    data_completeness: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "asset_id": self.asset_id,
            "market": self.market,
            "benchmark_asset_id": self.benchmark_asset_id,
            "as_of": self.as_of,
            "price_trade_date": self.price_trade_date,
            "price_field_used": self.price_field_used,
            "current_price": self.current_price,
            "n_observations": self.n_observations,
            "return_1m": self.return_1m,
            "return_3m": self.return_3m,
            "return_6m": self.return_6m,
            "return_12m": self.return_12m,
            "rel_return_3m": self.rel_return_3m,
            "rel_return_6m": self.rel_return_6m,
            "rel_return_12m": self.rel_return_12m,
            "ma20": self.ma20,
            "ma60": self.ma60,
            "ma120": self.ma120,
            "ma200": self.ma200,
            "drawdown_from_52w_high": self.drawdown_from_52w_high,
            "vol_20d": self.vol_20d,
            "vol_60d": self.vol_60d,
            "volume_change": self.volume_change,
            "below_ma_ratio": self.below_ma_ratio,
            "data_completeness": self.data_completeness,
        }


def build_weekly_features(
    asset_rows: Sequence[Dict[str, Any]],
    benchmark_rows: Sequence[Dict[str, Any]],
    *,
    asset_id: str,
    market: str,
    benchmark_asset_id: Optional[str],
    as_of: str,
    config: Dict[str, Any],
) -> WeeklyPriceFeatures:
    """Compute every Phase 1-B weekly feature for one asset.

    `asset_rows`/`benchmark_rows` MUST already be point-in-time filtered by
    the caller (`price_repository.get_prices_as_of(..., as_of)`); this
    function performs no date filtering of its own.
    """
    asset_series = build_price_series(asset_rows)
    benchmark_series = build_price_series(benchmark_rows)

    if not asset_series:
        return WeeklyPriceFeatures(
            asset_id=asset_id,
            market=market,
            benchmark_asset_id=benchmark_asset_id,
            as_of=as_of,
            price_trade_date=None,
            price_field_used=None,
            current_price=None,
            n_observations=0,
            data_completeness=0.0,
        )

    return_windows: Dict[str, int] = config["return_windows_trading_days"]
    ma_windows: Sequence[int] = config["moving_average_windows"]
    vol_windows: Sequence[int] = config["volatility_windows"]
    week_52_window: int = config["week_52_window_trading_days"]
    volume_cfg: Dict[str, int] = config["volume_change_windows"]

    asset_returns = compute_returns(asset_series, return_windows)
    benchmark_returns = compute_returns(benchmark_series, return_windows) if benchmark_series else {
        label: None for label in return_windows
    }
    rel_returns = compute_relative_returns(asset_returns, benchmark_returns, labels=("3m", "6m", "12m"))

    mas = compute_moving_averages(asset_series, ma_windows)
    ma20 = mas.get(20)
    ma60 = mas.get(60)
    ma120 = mas.get(120)
    ma200 = mas.get(200)

    current_price = asset_series[-1].price
    ma20_gap = _gap(current_price, ma20)
    ma60_gap = _gap(current_price, ma60)
    ma120_gap = _gap(current_price, ma120)
    ma200_gap = _gap(current_price, ma200)

    drawdown = drawdown_from_high(asset_series, week_52_window)
    vols = {w: volatility(asset_series, w) for w in vol_windows}
    vol_20d = vols.get(20)
    vol_60d = vols.get(60)
    volume_change = compute_volume_change(
        asset_series, recent_window=volume_cfg["recent"], prior_window=volume_cfg["prior"]
    )
    below_ma_ratio = compute_below_ma_ratio(current_price, {20: ma20, 60: ma60, 120: ma120, 200: ma200})

    filled_slots = 0
    feature_values = {
        "return_1m": asset_returns.get("1m"),
        "return_3m": asset_returns.get("3m"),
        "return_6m": asset_returns.get("6m"),
        "return_12m": asset_returns.get("12m"),
        "rel_return_3m": rel_returns.get("rel_return_3m"),
        "rel_return_6m": rel_returns.get("rel_return_6m"),
        "rel_return_12m": rel_returns.get("rel_return_12m"),
        "ma20": ma20,
        "ma60": ma60,
        "ma120": ma120,
        "ma200": ma200,
        "drawdown_from_52w_high": drawdown,
        "vol_20d": vol_20d,
        "vol_60d": vol_60d,
        "volume_change": volume_change,
    }
    for slot in _EXPECTED_FEATURE_SLOTS:
        if feature_values.get(slot) is not None:
            filled_slots += 1
    data_completeness = filled_slots / len(_EXPECTED_FEATURE_SLOTS)

    return WeeklyPriceFeatures(
        asset_id=asset_id,
        market=market,
        benchmark_asset_id=benchmark_asset_id,
        as_of=as_of,
        price_trade_date=asset_series[-1].trade_date,
        price_field_used=summarize_price_field_used(asset_series),
        current_price=current_price,
        n_observations=len(asset_series),
        return_1m=feature_values["return_1m"],
        return_3m=feature_values["return_3m"],
        return_6m=feature_values["return_6m"],
        return_12m=feature_values["return_12m"],
        rel_return_3m=feature_values["rel_return_3m"],
        rel_return_6m=feature_values["rel_return_6m"],
        rel_return_12m=feature_values["rel_return_12m"],
        ma20=ma20,
        ma60=ma60,
        ma120=ma120,
        ma200=ma200,
        ma20_gap=ma20_gap,
        ma60_gap=ma60_gap,
        ma120_gap=ma120_gap,
        ma200_gap=ma200_gap,
        drawdown_from_52w_high=drawdown,
        vol_20d=vol_20d,
        vol_60d=vol_60d,
        volume_change=volume_change,
        below_ma_ratio=below_ma_ratio,
        data_completeness=data_completeness,
    )
