from __future__ import annotations

"""Phase 3: per-stock raw component extraction (pure DB reads only, no writes/network).

Reads the PRE-EXISTING `financial_metric` / `stock_consensus` tables (owned by
other parts of the committee codebase, not created by industry_cycle) and
derives small, naturally-centered raw signals feeding
`stock_scoring.compute_stock_score`'s `earnings_quality` / `estimate_revision`
/ `financial_health` sub-score groups (design doc section 8.2's `stock_score`
formula).

Point-in-time caveat (documented limitation, not silently ignored)
--------------------------------------------------------------------
`financial_metric` has no `known_at`/`published_at` column (unlike
`indicator_observation` in Phase 2) -- it only has `updated_at`, which is
when OUR system last wrote the row, not when the filing was actually
released. `_as_of_financial_metric_rows` uses `updated_at <= as_of` as a
best-effort point-in-time proxy: safe for "gives current/forward runs" (an
`as_of` at or after `updated_at` can never see a not-yet-ingested row), but
NOT a guaranteed vintage-accurate backtest input the way Phase 2's FRED/KOSIS
data is. Any Phase 5 backtest over this module's outputs must treat that as
a known accuracy limitation.

`stock_consensus.date` IS a genuine daily snapshot date (when that
consensus view was captured), so it is a reliable point-in-time field and is
gated on directly.
"""

from dataclasses import dataclass, field
from datetime import date, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

from committee.core.database import connect, get_financial_metrics, init_db


def _parse_period_key(business_year: Any) -> Optional[Tuple[int, int]]:
    """Parse `financial_metric.business_year` into a sortable `(year, month)`.

    Handles both observed shapes in the real data: bare `"YYYY"` (Korean
    annual filings, implicit December FY end) and `"YYYY-MM"` (US filings
    with an explicit fiscal-period-end month).
    """
    s = str(business_year or "").strip()
    if len(s) == 4 and s.isdigit():
        return (int(s), 12)
    if len(s) == 7 and s[4] == "-":
        try:
            return (int(s[:4]), int(s[5:7]))
        except ValueError:
            return None
    return None


def _as_of_financial_metric_rows(
    ticker: str, as_of: str, *, limit: int = 12, db_path: Path | None = None
) -> List[Dict[str, Any]]:
    """`financial_metric` rows for `ticker` with `updated_at <= as_of` (see module docstring)."""
    rows = get_financial_metrics(ticker, limit=limit, db_path=db_path)
    return [r for r in rows if r.get("updated_at") and str(r["updated_at"]) <= str(as_of)]


def _select_periods(rows: Sequence[Dict[str, Any]], period_type: str) -> List[Dict[str, Any]]:
    """Rows of one `period_type`, sorted most-recent-first by parsed period key."""
    keyed = [(r, _parse_period_key(r.get("business_year"))) for r in rows if r.get("period_type") == period_type]
    keyed = [(r, k) for r, k in keyed if k is not None]
    keyed.sort(key=lambda pair: pair[1], reverse=True)
    return [r for r, _ in keyed]


def _select_latest_row(rows: Sequence[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """Most recent row across ALL period types (used for level-based components)."""
    keyed = [(r, _parse_period_key(r.get("business_year"))) for r in rows]
    keyed = [(r, k) for r, k in keyed if k is not None]
    if not keyed:
        return None
    keyed.sort(key=lambda pair: pair[1], reverse=True)
    return keyed[0][0]


@dataclass(frozen=True)
class YoyPair:
    current: Dict[str, Any]
    prior: Optional[Dict[str, Any]]
    yoy_aligned: bool


def _select_yoy_pair(rows: Sequence[Dict[str, Any]]) -> Optional[YoyPair]:
    """Best-available (current, ~12-months-ago) period pair for YoY comparisons.

    Prefers `quarterly` rows (exact same-quarter-last-year match, else a
    best-effort 4-periods-back fallback flagged via `yoy_aligned=False`);
    falls back to `annual` rows (natural 1-period-back YoY) when there are
    not enough quarterly rows. Returns `None` when neither has >=2 periods.
    """
    quarterly = _select_periods(rows, "quarterly")
    if len(quarterly) >= 2:
        current = quarterly[0]
        cur_key = _parse_period_key(current["business_year"])
        target_key = (cur_key[0] - 1, cur_key[1])
        exact = next(
            (r for r in quarterly[1:] if _parse_period_key(r["business_year"]) == target_key), None
        )
        if exact is not None:
            return YoyPair(current=current, prior=exact, yoy_aligned=True)
        if len(quarterly) >= 4:
            return YoyPair(current=current, prior=quarterly[3], yoy_aligned=False)
        return YoyPair(current=current, prior=quarterly[-1], yoy_aligned=False)

    annual = _select_periods(rows, "annual")
    if len(annual) >= 2:
        return YoyPair(current=annual[0], prior=annual[1], yoy_aligned=True)

    return None


def _safe_pct_change(current: Optional[float], prior: Optional[float]) -> Optional[float]:
    if current is None or prior is None or prior == 0:
        return None
    return (current - prior) / abs(prior)


@dataclass(frozen=True)
class EarningsQualityInputs:
    revenue_growth_yoy: Optional[float]
    operating_margin_trend: Optional[float]
    roe: Optional[float]
    yoy_aligned: Optional[bool]
    current_period: Optional[str]
    prior_period: Optional[str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "revenue_growth_yoy": self.revenue_growth_yoy,
            "operating_margin_trend": self.operating_margin_trend,
            "roe": self.roe,
            "yoy_aligned": self.yoy_aligned,
            "current_period": self.current_period,
            "prior_period": self.prior_period,
        }

    def raw_components(self) -> Dict[str, Optional[float]]:
        return {
            "revenue_growth_yoy": self.revenue_growth_yoy,
            "operating_margin_trend": self.operating_margin_trend,
            "roe": self.roe,
        }


def compute_earnings_quality_inputs(ticker: str, as_of: str, *, db_path: Path | None = None) -> EarningsQualityInputs:
    """Raw (unscored) `earnings_quality` inputs from `financial_metric`.

    All three fields are `None` (never fabricated/zero-filled) when the
    ticker does not have enough history in the DB to compute them -- e.g.
    a single-annual-period Korean ticker cannot produce a YoY growth or
    margin trend, only the level-based `roe`.
    """
    rows = _as_of_financial_metric_rows(ticker, as_of, db_path=db_path)
    pair = _select_yoy_pair(rows)
    latest = _select_latest_row(rows)

    revenue_growth_yoy: Optional[float] = None
    operating_margin_trend: Optional[float] = None
    yoy_aligned: Optional[bool] = None
    current_period: Optional[str] = None
    prior_period: Optional[str] = None

    if pair is not None and pair.prior is not None:
        revenue_growth_yoy = _safe_pct_change(pair.current.get("revenue"), pair.prior.get("revenue"))
        cur_margin = pair.current.get("operating_margin")
        prior_margin = pair.prior.get("operating_margin")
        if cur_margin is not None and prior_margin is not None:
            operating_margin_trend = (float(cur_margin) - float(prior_margin)) / 100.0
        yoy_aligned = pair.yoy_aligned
        current_period = str(pair.current.get("business_year"))
        prior_period = str(pair.prior.get("business_year"))

    roe: Optional[float] = None
    if latest is not None and latest.get("roe") is not None:
        roe = float(latest["roe"]) / 100.0

    return EarningsQualityInputs(
        revenue_growth_yoy=revenue_growth_yoy,
        operating_margin_trend=operating_margin_trend,
        roe=roe,
        yoy_aligned=yoy_aligned,
        current_period=current_period,
        prior_period=prior_period,
    )


@dataclass(frozen=True)
class FinancialHealthInputs:
    debt_ratio_inverse: Optional[float]
    net_margin: Optional[float]
    fcf_margin: Optional[float]
    capital_impaired: Optional[bool]
    sustained_loss_periods: int
    latest_period: Optional[str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "debt_ratio_inverse": self.debt_ratio_inverse,
            "net_margin": self.net_margin,
            "fcf_margin": self.fcf_margin,
            "capital_impaired": self.capital_impaired,
            "sustained_loss_periods": self.sustained_loss_periods,
            "latest_period": self.latest_period,
        }

    def raw_components(self) -> Dict[str, Optional[float]]:
        return {
            "debt_ratio_inverse": self.debt_ratio_inverse,
            "net_margin": self.net_margin,
            "fcf_margin": self.fcf_margin,
        }


def _count_sustained_losses(rows: Sequence[Dict[str, Any]], *, period_type: str) -> int:
    """Count consecutive most-recent periods (of one `period_type`) with `net_income < 0`."""
    periods = _select_periods(rows, period_type)
    count = 0
    for r in periods:
        ni = r.get("net_income")
        if ni is None:
            break
        if float(ni) < 0:
            count += 1
        else:
            break
    return count


def compute_financial_health_inputs(ticker: str, as_of: str, *, db_path: Path | None = None) -> FinancialHealthInputs:
    """Raw (unscored) `financial_health` inputs + exclusion-relevant flags."""
    rows = _as_of_financial_metric_rows(ticker, as_of, db_path=db_path)
    latest = _select_latest_row(rows)

    debt_ratio_inverse: Optional[float] = None
    net_margin: Optional[float] = None
    fcf_margin: Optional[float] = None
    capital_impaired: Optional[bool] = None
    latest_period: Optional[str] = None

    if latest is not None:
        latest_period = str(latest.get("business_year"))
        if latest.get("debt_ratio") is not None:
            debt_ratio_inverse = -float(latest["debt_ratio"]) / 100.0
        if latest.get("net_margin") is not None:
            net_margin = float(latest["net_margin"]) / 100.0
        fcf = latest.get("free_cashflow")
        revenue = latest.get("revenue")
        if fcf is not None and revenue:
            fcf_margin = float(fcf) / float(revenue)
        equity = latest.get("total_equity")
        if equity is not None:
            capital_impaired = float(equity) <= 0.0

    quarterly_losses = _count_sustained_losses(rows, period_type="quarterly")
    annual_losses = _count_sustained_losses(rows, period_type="annual")
    sustained_loss_periods = max(quarterly_losses, annual_losses)

    return FinancialHealthInputs(
        debt_ratio_inverse=debt_ratio_inverse,
        net_margin=net_margin,
        fcf_margin=fcf_margin,
        capital_impaired=capital_impaired,
        sustained_loss_periods=sustained_loss_periods,
        latest_period=latest_period,
    )


def _consensus_history_as_of(
    ticker: str, as_of: str, *, db_path: Path | None = None
) -> List[Dict[str, Any]]:
    """`stock_consensus` snapshots for `ticker` with `date <= as_of`, oldest first.

    `date` is a genuine point-in-time snapshot date (unlike
    `financial_metric.updated_at`), so this gate is exact, not a proxy.
    """
    init_db(db_path)
    with connect(db_path) as conn:
        rows = conn.execute(
            """
            SELECT * FROM stock_consensus
            WHERE ticker = :ticker AND date <= :as_of
            ORDER BY date ASC;
            """,
            {"ticker": ticker.strip().upper(), "as_of": as_of},
        ).fetchall()
        return [dict(r) for r in rows]


@dataclass(frozen=True)
class EstimateRevisionInputs:
    target_price_change_pct: Optional[float]
    recommendation_change: Optional[float]
    analyst_count_change_pct: Optional[float]
    lookback_snapshot_date: Optional[str]
    latest_snapshot_date: Optional[str]
    n_snapshots: int

    def to_dict(self) -> Dict[str, Any]:
        return {
            "target_price_change_pct": self.target_price_change_pct,
            "recommendation_change": self.recommendation_change,
            "analyst_count_change_pct": self.analyst_count_change_pct,
            "lookback_snapshot_date": self.lookback_snapshot_date,
            "latest_snapshot_date": self.latest_snapshot_date,
            "n_snapshots": self.n_snapshots,
        }

    def raw_components(self) -> Dict[str, Optional[float]]:
        return {
            "target_price_change_pct": self.target_price_change_pct,
            "recommendation_change": self.recommendation_change,
            "analyst_count_change_pct": self.analyst_count_change_pct,
        }


def compute_estimate_revision_inputs(
    ticker: str, as_of: str, *, lookback_days: int, db_path: Path | None = None
) -> EstimateRevisionInputs:
    """Raw (unscored) `estimate_revision` inputs from `stock_consensus` history.

    Compares the latest snapshot on/before `as_of` against the snapshot
    closest to (but not after) `as_of - lookback_days`; if history is
    shorter than `lookback_days`, falls back to the oldest available
    snapshot (still a real historical value, never fabricated).
    """
    history = _consensus_history_as_of(ticker, as_of, db_path=db_path)
    if len(history) < 2:
        return EstimateRevisionInputs(
            target_price_change_pct=None,
            recommendation_change=None,
            analyst_count_change_pct=None,
            lookback_snapshot_date=None,
            latest_snapshot_date=history[-1]["date"] if history else None,
            n_snapshots=len(history),
        )

    latest = history[-1]
    try:
        cutoff = date.fromisoformat(str(as_of)[:10]) - timedelta(days=lookback_days)
    except ValueError:
        cutoff = None

    past = history[0]
    if cutoff is not None:
        for row in history:
            if date.fromisoformat(str(row["date"])[:10]) <= cutoff:
                past = row
            else:
                break

    target_price_change_pct = _safe_pct_change(latest.get("target_mean_price"), past.get("target_mean_price"))

    recommendation_change: Optional[float] = None
    if latest.get("recommendation_mean") is not None and past.get("recommendation_mean") is not None:
        # Yahoo-style scale: 1=Strong Buy .. 5=Sell, so a DECREASE is bullish.
        recommendation_change = -(float(latest["recommendation_mean"]) - float(past["recommendation_mean"]))

    analyst_count_change_pct = _safe_pct_change(latest.get("num_analysts"), past.get("num_analysts"))

    return EstimateRevisionInputs(
        target_price_change_pct=target_price_change_pct,
        recommendation_change=recommendation_change,
        analyst_count_change_pct=analyst_count_change_pct,
        lookback_snapshot_date=str(past.get("date")),
        latest_snapshot_date=str(latest.get("date")),
        n_snapshots=len(history),
    )
