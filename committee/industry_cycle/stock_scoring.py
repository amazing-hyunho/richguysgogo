from __future__ import annotations

"""Phase 3: per-stock `stock_score` computation (pure orchestration, DB reads only).

Implements design doc section 8.2's `stock_score` formula:

    stock_score =
        0.30 * earnings_quality
      + 0.25 * estimate_revision
      + 0.20 * relative_strength
      + 0.15 * financial_health
      + 0.10 * liquidity
      - risk_penalty

Two-level composition (mirrors `price_scoring.py`'s nested design): each of
the five named terms is ITSELF a `weighted_logistic_score` over several
small, naturally-centered raw ratios (see `stock_model_config`'s five
matching config groups), producing a 0~100 sub-score. Those five sub-scores
are then baseline-centered at 50 and combined by one more
`weighted_logistic_score` call into the final 0~100 `stock_score`, then
`risk_penalty` points are subtracted (never below 0).

`relative_strength`/`liquidity` are price-derived and require
`asset_price_daily` history for the ticker (Phase 1-A/1-B's table, asset-type
agnostic). When absent (e.g. a stock never backfilled), those two sub-scores
are `None` with `reason="no_price_data"` -- excluded from `stock_score`'s
weighted sum and renormalized away, exactly like any other missing
component, never treated as 0.
"""

import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional

from committee.industry_cycle import price_repository, stock_fundamentals
from committee.industry_cycle.price_features import WeeklyPriceFeatures, build_price_series, build_weekly_features
from committee.industry_cycle.scoring_common import ScoreResult, weighted_logistic_score
from committee.industry_cycle.stock_exclusion import ExclusionCheckInputs, ExclusionResult, evaluate_exclusions

_SUBSCORE_GROUPS = ("earnings_quality", "estimate_revision", "relative_strength", "financial_health", "liquidity")


def turnover_level(asset_rows, *, window: int = 20) -> Optional[float]:
    """`log10(mean(price * volume))` over the last `window` trading days, `None` if too short."""
    series = build_price_series(asset_rows)
    if len(series) < window:
        return None
    recent = series[-window:]
    dollar_vols = [p.price * p.volume for p in recent if p.volume is not None and p.volume > 0]
    if len(dollar_vols) < window // 2:
        return None
    mean_dollar_vol = sum(dollar_vols) / len(dollar_vols)
    if mean_dollar_vol <= 0:
        return None
    return math.log10(mean_dollar_vol)


@dataclass(frozen=True)
class StockScoreBundle:
    ticker: str
    industry_id: str
    as_of: str
    score: Optional[float]
    pre_penalty_score: Optional[float]
    risk_penalty_points: float
    weighted_sum: Optional[float]
    reason: Optional[str]
    data_completeness: float
    sub_scores: Dict[str, ScoreResult] = field(default_factory=dict)
    exclusion: Optional[ExclusionResult] = None
    price_field_used: Optional[str] = None
    n_price_observations: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ticker": self.ticker,
            "industry_id": self.industry_id,
            "as_of": self.as_of,
            "score": self.score,
            "pre_penalty_score": self.pre_penalty_score,
            "risk_penalty_points": self.risk_penalty_points,
            "weighted_sum": self.weighted_sum,
            "reason": self.reason,
            "data_completeness": self.data_completeness,
            "sub_scores": {k: v.to_dict() for k, v in self.sub_scores.items()},
            "exclusion": self.exclusion.to_dict() if self.exclusion else None,
            "price_field_used": self.price_field_used,
            "n_price_observations": self.n_price_observations,
        }


def load_price_features(
    ticker: str,
    market: str,
    benchmark_asset_id: Optional[str],
    as_of: str,
    price_feature_config: Dict[str, Any],
    db_path: Path | None = None,
):
    """Public wrapper so other Phase 3 modules (`industry_breadth_scoring`) can
    reuse the same asset-agnostic price-feature loading as `compute_stock_score`
    without duplicating the point-in-time price-fetch + feature-build plumbing."""
    return _load_price_features(ticker, market, benchmark_asset_id, as_of, price_feature_config, db_path)


def _load_price_features(
    ticker: str,
    market: str,
    benchmark_asset_id: Optional[str],
    as_of: str,
    price_feature_config: Dict[str, Any],
    db_path: Path | None,
):
    asset_rows = price_repository.get_prices_as_of(ticker, as_of, db_path=db_path)
    if not asset_rows:
        return None, None
    benchmark_rows = (
        price_repository.get_prices_as_of(benchmark_asset_id, as_of, db_path=db_path) if benchmark_asset_id else []
    )
    features = build_weekly_features(
        asset_rows,
        benchmark_rows,
        asset_id=ticker,
        market=market,
        benchmark_asset_id=benchmark_asset_id,
        as_of=as_of,
        config=price_feature_config,
    )
    if features.n_observations == 0:
        return None, None
    return features, asset_rows


def _compute_risk_penalty(
    *,
    fh_inputs: stock_fundamentals.FinancialHealthInputs,
    features: Optional[WeeklyPriceFeatures],
    stock_model_config: Dict[str, Any],
) -> float:
    risk_cfg = stock_model_config["risk_penalty"]
    points = 0.0

    if fh_inputs.debt_ratio_inverse is not None:
        debt_ratio = -fh_inputs.debt_ratio_inverse  # back to a positive ratio (e.g. 3.0 == 300%)
        if debt_ratio > float(risk_cfg["high_debt_ratio_threshold"]):
            points += float(risk_cfg["high_debt_ratio_points"])

    if fh_inputs.sustained_loss_periods >= 1:
        points += float(risk_cfg["sustained_loss_points"])

    surge_threshold = float(stock_model_config["exclusion"]["excessive_short_term_surge_pct_3m"])
    warning_threshold = surge_threshold * 0.7
    if features is not None and features.return_3m is not None and features.return_3m > warning_threshold:
        points += float(risk_cfg["excessive_short_term_surge_points"])

    return min(points, float(risk_cfg["max_total_points"]))


def compute_stock_score(
    ticker: str,
    industry_id: str,
    as_of: str,
    *,
    market: str,
    benchmark_asset_id: Optional[str],
    stock_model_config: Dict[str, Any],
    price_feature_config: Dict[str, Any],
    liquidity_percentile: Optional[float] = None,
    trading_halted: Optional[bool] = None,
    administrative_issue: Optional[bool] = None,
    db_path: Path | None = None,
) -> StockScoreBundle:
    """Compute one stock's `stock_score` as of `as_of` (point-in-time safe, see module docstrings).

    `liquidity_percentile`/`trading_halted`/`administrative_issue` are
    cross-sectional or externally-sourced signals this function cannot
    derive on its own -- pass them in from the caller (`candidate_ranking`,
    which has visibility across the whole candidate set) when available;
    they default to `None` ("unknown", never auto-excluded on that basis).
    """
    eq_inputs = stock_fundamentals.compute_earnings_quality_inputs(ticker, as_of, db_path=db_path)
    fh_inputs = stock_fundamentals.compute_financial_health_inputs(ticker, as_of, db_path=db_path)
    er_inputs = stock_fundamentals.compute_estimate_revision_inputs(
        ticker, as_of, lookback_days=int(stock_model_config["consensus_revision_lookback_days"]), db_path=db_path
    )
    features, asset_rows = _load_price_features(ticker, market, benchmark_asset_id, as_of, price_feature_config, db_path)

    eq_score = weighted_logistic_score(eq_inputs.raw_components(), stock_model_config["earnings_quality"])
    er_score = weighted_logistic_score(er_inputs.raw_components(), stock_model_config["estimate_revision"])
    fh_score = weighted_logistic_score(fh_inputs.raw_components(), stock_model_config["financial_health"])

    if features is not None:
        rel_raw = {
            "rel_return_3m": features.rel_return_3m,
            "rel_return_6m": features.rel_return_6m,
            "rel_return_12m": features.rel_return_12m,
        }
        rs_score = weighted_logistic_score(rel_raw, stock_model_config["relative_strength"])
        liq_raw = {
            "volume_change": features.volume_change,
            "turnover_level": turnover_level(asset_rows) if asset_rows else None,
        }
        liq_score = weighted_logistic_score(liq_raw, stock_model_config["liquidity"])
    else:
        rs_score = ScoreResult(score=None, components=[], weighted_sum=None, reason="no_price_data")
        liq_score = ScoreResult(score=None, components=[], weighted_sum=None, reason="no_price_data")

    sub_scores: Dict[str, ScoreResult] = {
        "earnings_quality": eq_score,
        "estimate_revision": er_score,
        "relative_strength": rs_score,
        "financial_health": fh_score,
        "liquidity": liq_score,
    }

    top_raw = {name: sub_scores[name].score for name in _SUBSCORE_GROUPS}
    top_result = weighted_logistic_score(top_raw, stock_model_config["stock_score"])

    top_weight_cfg: Dict[str, float] = stock_model_config["stock_score"]["components"]
    total_weight = sum(top_weight_cfg.values())
    used_weight = sum(top_weight_cfg[name] for name in _SUBSCORE_GROUPS if sub_scores[name].score is not None)
    data_completeness = (used_weight / total_weight) if total_weight else 0.0

    risk_penalty_points = _compute_risk_penalty(fh_inputs=fh_inputs, features=features, stock_model_config=stock_model_config)
    final_score = None if top_result.score is None else max(0.0, top_result.score - risk_penalty_points)

    exclusion_inputs = ExclusionCheckInputs(
        capital_impaired=fh_inputs.capital_impaired,
        sustained_loss_periods=fh_inputs.sustained_loss_periods,
        fcf_margin=fh_inputs.fcf_margin,
        return_3m=features.return_3m if features is not None else None,
        ma200_gap=features.ma200_gap if features is not None else None,
        data_completeness=data_completeness,
        liquidity_percentile=liquidity_percentile,
        listing_days=features.n_observations if features is not None else None,
        trading_halted=trading_halted,
        administrative_issue=administrative_issue,
    )
    exclusion_result = evaluate_exclusions(exclusion_inputs, stock_model_config)

    return StockScoreBundle(
        ticker=ticker,
        industry_id=industry_id,
        as_of=as_of,
        score=final_score,
        pre_penalty_score=top_result.score,
        risk_penalty_points=risk_penalty_points,
        weighted_sum=top_result.weighted_sum,
        reason=top_result.reason,
        data_completeness=data_completeness,
        sub_scores=sub_scores,
        exclusion=exclusion_result,
        price_field_used=features.price_field_used if features is not None else None,
        n_price_observations=features.n_observations if features is not None else 0,
    )
