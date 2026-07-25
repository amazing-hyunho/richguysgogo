from __future__ import annotations

"""Phase 3: INDUSTRY-level `earnings_revision_score` / `breadth_score` (pure orchestration).

Design doc section 7.1 defines these as industry sub-scores of the (not yet
implemented -- deferred to a later phase) `cycle_score`:

    earnings_revision_score: 매출·이익·EPS 전망의 상향 비율과 변화 속도
    breadth_score: 산업 내 상승 종목 비율, 200일선 상회 비율, 실적 개선 기업 비율

Both are computed here by aggregating PER-STOCK signals (from
`stock_fundamentals`/`stock_scoring`) across every `STOCK`-type asset mapped
to the industry in `industry_asset_map`, then combining the resulting
cross-sectional ratios via `scoring_common.weighted_logistic_score` --
exactly the same explainable weighted-sum -> logistic(...) contract used
everywhere else in this codebase. A ticker missing the underlying data is
simply excluded from that ratio's denominator (never counted against it and
never fabricated as 0/positive).
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from committee.industry_cycle import stock_fundamentals, stock_scoring
from committee.industry_cycle.scoring_common import ScoreResult, weighted_logistic_score


@dataclass(frozen=True)
class TickerBreadthEvidence:
    ticker: str
    rel_return_6m: Optional[float]
    ma200_gap: Optional[float]
    is_positive_relative_strength: Optional[bool]
    is_above_200ma: Optional[bool]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ticker": self.ticker,
            "rel_return_6m": self.rel_return_6m,
            "ma200_gap": self.ma200_gap,
            "is_positive_relative_strength": self.is_positive_relative_strength,
            "is_above_200ma": self.is_above_200ma,
        }


@dataclass(frozen=True)
class TickerEarningsRevisionEvidence:
    ticker: str
    revenue_growth_yoy: Optional[float]
    is_improving: Optional[bool]
    target_price_change_pct: Optional[float]
    recommendation_change: Optional[float]
    is_recommendation_improving: Optional[bool]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ticker": self.ticker,
            "revenue_growth_yoy": self.revenue_growth_yoy,
            "is_improving": self.is_improving,
            "target_price_change_pct": self.target_price_change_pct,
            "recommendation_change": self.recommendation_change,
            "is_recommendation_improving": self.is_recommendation_improving,
        }


@dataclass(frozen=True)
class IndustryBreadthBundle:
    industry_id: str
    as_of: str
    score: Optional[float]
    weighted_sum: Optional[float]
    reason: Optional[str]
    data_completeness: float
    n_tickers_considered: int
    evidence: List[TickerBreadthEvidence] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "industry_id": self.industry_id,
            "as_of": self.as_of,
            "score": self.score,
            "weighted_sum": self.weighted_sum,
            "reason": self.reason,
            "data_completeness": self.data_completeness,
            "n_tickers_considered": self.n_tickers_considered,
            "evidence": [e.to_dict() for e in self.evidence],
        }


@dataclass(frozen=True)
class IndustryEarningsRevisionBundle:
    industry_id: str
    as_of: str
    score: Optional[float]
    weighted_sum: Optional[float]
    reason: Optional[str]
    data_completeness: float
    n_tickers_considered: int
    evidence: List[TickerEarningsRevisionEvidence] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "industry_id": self.industry_id,
            "as_of": self.as_of,
            "score": self.score,
            "weighted_sum": self.weighted_sum,
            "reason": self.reason,
            "data_completeness": self.data_completeness,
            "n_tickers_considered": self.n_tickers_considered,
            "evidence": [e.to_dict() for e in self.evidence],
        }


def _ratio(numerator: int, denominator: int) -> Optional[float]:
    return None if denominator == 0 else numerator / denominator


def compute_industry_earnings_revision_score(
    industry_id: str,
    as_of: str,
    *,
    tickers: List[str],
    stock_model_config: Dict[str, Any],
    db_path: Path | None = None,
) -> IndustryEarningsRevisionBundle:
    """Aggregate `earnings_quality`/`estimate_revision` per-ticker signals into one industry score."""
    lookback_days = int(stock_model_config["consensus_revision_lookback_days"])
    evidence: List[TickerEarningsRevisionEvidence] = []
    target_price_changes: List[float] = []
    n_improving = 0
    n_with_earnings_data = 0
    n_recommendation_improving = 0
    n_with_recommendation_data = 0

    for ticker in tickers:
        eq = stock_fundamentals.compute_earnings_quality_inputs(ticker, as_of, db_path=db_path)
        er = stock_fundamentals.compute_estimate_revision_inputs(ticker, as_of, lookback_days=lookback_days, db_path=db_path)

        is_improving: Optional[bool] = None
        if eq.revenue_growth_yoy is not None:
            is_improving = eq.revenue_growth_yoy > 0
            n_with_earnings_data += 1
            if is_improving:
                n_improving += 1

        if er.target_price_change_pct is not None:
            target_price_changes.append(er.target_price_change_pct)

        is_rec_improving: Optional[bool] = None
        if er.recommendation_change is not None:
            is_rec_improving = er.recommendation_change > 0
            n_with_recommendation_data += 1
            if is_rec_improving:
                n_recommendation_improving += 1

        evidence.append(
            TickerEarningsRevisionEvidence(
                ticker=ticker,
                revenue_growth_yoy=eq.revenue_growth_yoy,
                is_improving=is_improving,
                target_price_change_pct=er.target_price_change_pct,
                recommendation_change=er.recommendation_change,
                is_recommendation_improving=is_rec_improving,
            )
        )

    pct_improving_earnings = _ratio(n_improving, n_with_earnings_data)
    consensus_target_price_change = (
        sum(target_price_changes) / len(target_price_changes) if target_price_changes else None
    )
    consensus_recommendation_improve_pct = _ratio(n_recommendation_improving, n_with_recommendation_data)

    raw = {
        "pct_improving_earnings": pct_improving_earnings,
        "consensus_target_price_change": consensus_target_price_change,
        "consensus_recommendation_improve_pct": consensus_recommendation_improve_pct,
    }
    group_config = stock_model_config["industry_earnings_revision"]
    result: ScoreResult = weighted_logistic_score(raw, group_config)

    weight_cfg: Dict[str, float] = group_config["components"]
    total_weight = sum(weight_cfg.values())
    used_weight = sum(weight_cfg[k] for k, v in raw.items() if v is not None and k in weight_cfg)
    data_completeness = (used_weight / total_weight) if total_weight else 0.0

    return IndustryEarningsRevisionBundle(
        industry_id=industry_id,
        as_of=as_of,
        score=result.score,
        weighted_sum=result.weighted_sum,
        reason=result.reason,
        data_completeness=data_completeness,
        n_tickers_considered=len(tickers),
        evidence=evidence,
    )


def compute_industry_breadth_score(
    industry_id: str,
    as_of: str,
    *,
    ticker_markets: Dict[str, str],
    ticker_benchmarks: Dict[str, Optional[str]],
    stock_model_config: Dict[str, Any],
    price_feature_config: Dict[str, Any],
    db_path: Path | None = None,
) -> IndustryBreadthBundle:
    """Aggregate per-ticker relative-strength/trend signals into one industry `breadth_score`.

    `ticker_markets`/`ticker_benchmarks` map each ticker to its market
    ('KR'/'US') and country-benchmark asset_id, mirroring
    `stock_scoring.compute_stock_score`'s per-ticker call signature.
    """
    evidence: List[TickerBreadthEvidence] = []
    n_positive_rs = 0
    n_with_rs_data = 0
    n_above_200ma = 0
    n_with_ma_data = 0

    for ticker, market in ticker_markets.items():
        benchmark_asset_id = ticker_benchmarks.get(ticker)
        features, _ = stock_scoring.load_price_features(
            ticker, market, benchmark_asset_id, as_of, price_feature_config, db_path
        )

        rel_return_6m = features.rel_return_6m if features is not None else None
        ma200_gap = features.ma200_gap if features is not None else None

        is_positive: Optional[bool] = None
        if rel_return_6m is not None:
            is_positive = rel_return_6m > 0
            n_with_rs_data += 1
            if is_positive:
                n_positive_rs += 1

        is_above: Optional[bool] = None
        if ma200_gap is not None:
            is_above = ma200_gap > 0
            n_with_ma_data += 1
            if is_above:
                n_above_200ma += 1

        evidence.append(
            TickerBreadthEvidence(
                ticker=ticker,
                rel_return_6m=rel_return_6m,
                ma200_gap=ma200_gap,
                is_positive_relative_strength=is_positive,
                is_above_200ma=is_above,
            )
        )

    raw = {
        "pct_positive_relative_strength": _ratio(n_positive_rs, n_with_rs_data),
        "pct_above_200ma": _ratio(n_above_200ma, n_with_ma_data),
    }
    group_config = stock_model_config["industry_breadth"]
    result: ScoreResult = weighted_logistic_score(raw, group_config)

    weight_cfg: Dict[str, float] = group_config["components"]
    total_weight = sum(weight_cfg.values())
    used_weight = sum(weight_cfg[k] for k, v in raw.items() if v is not None and k in weight_cfg)
    data_completeness = (used_weight / total_weight) if total_weight else 0.0

    return IndustryBreadthBundle(
        industry_id=industry_id,
        as_of=as_of,
        score=result.score,
        weighted_sum=result.weighted_sum,
        reason=result.reason,
        data_completeness=data_completeness,
        n_tickers_considered=len(ticker_markets),
        evidence=evidence,
    )
