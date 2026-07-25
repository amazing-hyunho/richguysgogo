from __future__ import annotations

"""Phase 4: top-level industry `cycle_score` + confidence (pure orchestration).

Combines the sub-scores computed by every earlier phase into the design
doc's section 7.1 formula:

    cycle_score =
        0.25 * fundamentals_score      (Phase 2, industry_fundamentals_weekly)
      + 0.20 * earnings_revision_score (Phase 3, industry_earnings_breadth_weekly)
      + 0.20 * relative_strength_score (Phase 1-B, industry_factor_weekly)
      + 0.15 * flow_score              (NOT YET BUILT -- see below)
      + 0.10 * macro_fit_score         (NOT YET BUILT -- see below)
      + 0.10 * breadth_score           (Phase 3, industry_earnings_breadth_weekly)

via `scoring_common.weighted_logistic_score`, so a missing component is
excluded and the remaining weights renormalize to 1 (never fabricated as
0) -- exactly the same contract used by every other score in this package.

flow_score / macro_fit_score are why this module always passes `None` for
them today:
- flow_score (design doc: "거래대금, 기관·외국인 누적 수급, ETF 자금 흐름")
  would need PER-INDUSTRY institutional/foreign net-buying data. The only
  flow series this project has (`market_flow_daily`) is market-wide
  (KOSPI-level), not per-industry/per-asset, so it cannot distinguish one
  industry from another -- using it here would silently give every KR
  industry the same score, which is worse than reporting "unavailable".
- macro_fit_score (design doc: "금리, 달러, 유가, 신용스프레드 등과 산업의
  역사적 민감도") needs a per-industry historical-sensitivity model (e.g. a
  rolling regression of the industry ETF's returns against each macro
  series) that has not been built yet.
Both are therefore explicit, documented stubs (`_flow_score_stub`,
`_macro_fit_score_stub`) rather than silently-omitted keys, so a future
phase has one obvious place to wire in real data, and so this module's
`cycle_score` is never inflated/deflated by a fabricated neutral value --
`weighted_logistic_score`'s renormalization handles the remaining 4
components correctly in the meantime.

The industry-level relative_strength/trend/overheat/risk scores are a
weight-averaged read of `industry_factor_weekly` across every `ETF`-type
asset currently mapped to the industry (falling back to `STOCK`-type
assets if no ETF is mapped/scored yet -- design doc section 8.1: "ETF가
없는 산업은 개별 종목 바스켓을 지표로 사용할 수 있으나 ETF 추천은 없음으로
표시"; that "추천 없음" part is handled by `candidate_ranking`, not here).
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from committee.industry_cycle import (
    candidate_repository,
    etf_quality,
    factor_repository,
    fundamentals_repository,
    repository,
)
from committee.industry_cycle.candidate_ranking import is_valid_at
from committee.industry_cycle.price_state_machine import (
    PRICE_ONLY_DETERIORATING,
    PRICE_ONLY_EXPANSION,
    PRICE_ONLY_RECOVERY_CANDIDATE,
    PRICE_ONLY_WEAK,
)
from committee.industry_cycle.scoring_common import ScoreResult, weighted_logistic_score

_PRICE_FACTOR_KEYS = ("relative_strength_score", "trend_score", "overheat_score", "price_risk_score", "return_1m")


def _flow_score_stub(industry_id: str, as_of: str) -> Optional[float]:
    """Always `None` -- see module docstring. Kept as a named function (not an inline
    `None`) so a future phase can implement real per-industry flow data by
    replacing exactly this one function without touching `compute_cycle_score`."""
    return None


def _macro_fit_score_stub(industry_id: str, as_of: str) -> Optional[float]:
    """Always `None` -- see module docstring."""
    return None


@dataclass(frozen=True)
class RepresentativePriceFactors:
    relative_strength_score: Optional[float]
    trend_score: Optional[float]
    overheat_score: Optional[float]
    price_risk_score: Optional[float]
    return_1m: Optional[float] = None
    representative_asset_ids: List[str] = field(default_factory=list)
    representative_market: Optional[str] = None
    source_asset_type: Optional[str] = None  # 'ETF' or 'STOCK'


def _weighted_average_price_factors(
    mappings: List[Dict[str, Any]],
    as_of: str,
    price_model_version: str,
    db_path: Path | None,
) -> Optional[RepresentativePriceFactors]:
    sums: Dict[str, float] = {k: 0.0 for k in _PRICE_FACTOR_KEYS}
    weight_totals: Dict[str, float] = {k: 0.0 for k in _PRICE_FACTOR_KEYS}
    used_assets: List[str] = []
    market: Optional[str] = None

    for mapping in mappings:
        asset_id = str(mapping["asset_id"])
        row = factor_repository.get_factor_weekly(asset_id, as_of, price_model_version, db_path=db_path)
        if row is None:
            continue
        weight = float(mapping.get("weight") or 1.0)
        contributed = False
        for key in _PRICE_FACTOR_KEYS:
            value = row.get(key)
            if value is None:
                continue
            sums[key] += float(value) * weight
            weight_totals[key] += weight
            contributed = True
        if contributed:
            used_assets.append(asset_id)
            market = market or row.get("market") or mapping.get("market")

    if not used_assets:
        return None

    averaged = {
        key: (sums[key] / weight_totals[key] if weight_totals[key] > 0 else None) for key in _PRICE_FACTOR_KEYS
    }
    return RepresentativePriceFactors(
        relative_strength_score=averaged["relative_strength_score"],
        trend_score=averaged["trend_score"],
        overheat_score=averaged["overheat_score"],
        price_risk_score=averaged["price_risk_score"],
        return_1m=averaged["return_1m"],
        representative_asset_ids=used_assets,
        representative_market=market,
    )


def select_representative_price_factors(
    industry_id: str, as_of: str, *, price_model_version: str, db_path: Path | None = None
) -> Optional[RepresentativePriceFactors]:
    """Weight-average `industry_factor_weekly` across mapped ETFs, falling back to stocks.

    Returns `None` if neither ETF nor STOCK assets mapped to `industry_id`
    have any `industry_factor_weekly` row for this exact `(as_of,
    price_model_version)` -- e.g. the weekly price-factor CLI hasn't been
    run yet for this week, or the mapping is empty.
    """
    mappings = [m for m in repository.list_industry_assets(industry_id, db_path=db_path) if is_valid_at(m, as_of)]
    etf_mappings = [m for m in mappings if (m.get("asset_type") or "").upper() == "ETF"]
    stock_mappings = [m for m in mappings if (m.get("asset_type") or "").upper() == "STOCK"]

    result = _weighted_average_price_factors(etf_mappings, as_of, price_model_version, db_path)
    if result is not None:
        return RepresentativePriceFactors(**{**result.__dict__, "source_asset_type": "ETF"})

    result = _weighted_average_price_factors(stock_mappings, as_of, price_model_version, db_path)
    if result is not None:
        return RepresentativePriceFactors(**{**result.__dict__, "source_asset_type": "STOCK"})

    return None


def compute_history_reliability(
    representative_asset_ids: List[str],
    as_of: str,
    *,
    cycle_model_config: Dict[str, Any],
    db_path: Path | None = None,
) -> float:
    """Ratio of available price history to `min_listing_days_full_history_reliability` (capped at 1.0).

    Uses the LONGEST-listed representative asset (a basket only needs one
    sufficiently mature member to be considered reliable). Returns the
    configured `unknown_history_reliability_default` if no representative
    asset has any price history at all (never fabricated as full or zero
    confidence).
    """
    confidence_cfg = cycle_model_config["confidence"]
    if not representative_asset_ids:
        return float(confidence_cfg["unknown_history_reliability_default"])

    listing_days_values = [
        etf_quality.compute_listing_days(asset_id, as_of, db_path=db_path) for asset_id in representative_asset_ids
    ]
    known = [d for d in listing_days_values if d is not None]
    if not known:
        return float(confidence_cfg["unknown_history_reliability_default"])

    longest = max(known)
    full = float(confidence_cfg["min_listing_days_full_history_reliability"])
    return min(1.0, longest / full) if full > 0 else 1.0


def compute_model_agreement(
    cycle_score: Optional[float],
    price_only_raw_state: Optional[str],
    *,
    cycle_model_config: Dict[str, Any],
) -> float:
    """Heuristic agreement between the fundamentals-driven `cycle_score` direction and
    Phase 1-B's PRICE_ONLY_* provisional state (`price_state_machine.classify_raw_state`).

    Both `None` (no cycle_score or no PRICE_ONLY state to compare against)
    returns the configured neutral `model_agreement_unknown_value` -- an
    unknown comparison is not evidence of disagreement. A bullish
    cycle_score (>50) paired with a bearish PRICE_ONLY state (DETERIORATING/
    WEAK), or vice versa, is penalized by `model_agreement_conflict_penalty`;
    anything else (both bullish, both bearish, or the state is
    OVERHEATED/INSUFFICIENT_DATA which doesn't cleanly map to either
    direction) agrees.
    """
    confidence_cfg = cycle_model_config["confidence"]
    if cycle_score is None or price_only_raw_state is None:
        return float(confidence_cfg["model_agreement_unknown_value"])

    bearish_states = {PRICE_ONLY_DETERIORATING, PRICE_ONLY_WEAK}
    bullish_states = {PRICE_ONLY_EXPANSION, PRICE_ONLY_RECOVERY_CANDIDATE}

    cycle_bullish = cycle_score > 50.0
    cycle_bearish = cycle_score < 50.0

    if cycle_bullish and price_only_raw_state in bearish_states:
        return float(confidence_cfg["model_agreement_conflict_penalty"])
    if cycle_bearish and price_only_raw_state in bullish_states:
        return float(confidence_cfg["model_agreement_conflict_penalty"])
    return 1.0


def compute_signal_strength(weighted_sum: Optional[float], *, cycle_model_config: Dict[str, Any]) -> float:
    """Normalized magnitude of `cycle_score`'s pre-logistic weighted sum, clipped to [0, 1].

    Measures how strongly the available evidence leans one direction,
    independent of how MUCH evidence is available (that's
    `data_completeness`'s job) or how reliable it is historically (that's
    `history_reliability`'s job).
    """
    if weighted_sum is None:
        return 0.0
    scale = float(cycle_model_config["confidence"]["signal_strength_scale"])
    if scale <= 0:
        return 0.0
    return min(1.0, abs(weighted_sum) / scale)


@dataclass(frozen=True)
class CycleScoreBundle:
    industry_id: str
    as_of: str
    score: Optional[float]
    weighted_sum: Optional[float]
    reason: Optional[str]
    data_completeness: float
    fundamentals_score: Optional[float]
    earnings_revision_score: Optional[float]
    breadth_score: Optional[float]
    relative_strength_score: Optional[float]
    trend_score: Optional[float]
    overheat_score: Optional[float]
    risk_score: Optional[float]
    flow_score: Optional[float]
    macro_fit_score: Optional[float]
    return_1m: Optional[float] = None
    representative_asset_ids: List[str] = field(default_factory=list)
    representative_market: Optional[str] = None
    signal_strength: float = 0.0
    history_reliability: float = 0.0
    model_agreement: float = 1.0
    confidence: float = 0.0
    components: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "industry_id": self.industry_id,
            "as_of": self.as_of,
            "cycle_score": self.score,
            "cycle_weighted_sum": self.weighted_sum,
            "cycle_score_reason": self.reason,
            "data_completeness": self.data_completeness,
            "fundamentals_score": self.fundamentals_score,
            "earnings_revision_score": self.earnings_revision_score,
            "breadth_score": self.breadth_score,
            "relative_strength_score": self.relative_strength_score,
            "trend_score": self.trend_score,
            "overheat_score": self.overheat_score,
            "risk_score": self.risk_score,
            "flow_score": self.flow_score,
            "macro_fit_score": self.macro_fit_score,
            "representative_asset_id": ",".join(self.representative_asset_ids) or None,
            "representative_market": self.representative_market,
            "signal_strength": self.signal_strength,
            "history_reliability": self.history_reliability,
            "model_agreement": self.model_agreement,
            "confidence": self.confidence,
            "score_breakdown": self.components,
        }


def compute_cycle_score(
    industry_id: str,
    as_of: str,
    *,
    cycle_model_config: Dict[str, Any],
    fundamentals_model_version: str,
    candidate_model_version: str,
    price_model_version: str,
    price_only_raw_state: Optional[str] = None,
    db_path: Path | None = None,
) -> CycleScoreBundle:
    """Compute one industry's `cycle_score` + confidence for one `as_of` week.

    Reads (never writes):
    - `industry_fundamentals_weekly` (Phase 2, `fundamentals_model_version`)
    - `industry_earnings_breadth_weekly` (Phase 3, `candidate_model_version`)
    - `industry_factor_weekly` via `select_representative_price_factors`
      (Phase 1-B, `price_model_version`)

    `price_only_raw_state`, if given, is this week's Phase 1-B
    `PRICE_ONLY_*` classification for the representative asset (used only
    by `compute_model_agreement`) -- callers that already ran the price
    factor batch this week can pass it through instead of recomputing.
    """
    fundamentals_row = fundamentals_repository.get_fundamentals_weekly(
        industry_id, as_of, fundamentals_model_version, db_path=db_path
    )
    breadth_row = candidate_repository.get_earnings_breadth_weekly(
        industry_id, as_of, candidate_model_version, db_path=db_path
    )
    price_factors = select_representative_price_factors(
        industry_id, as_of, price_model_version=price_model_version, db_path=db_path
    )

    fundamentals_score = fundamentals_row.get("fundamentals_score") if fundamentals_row else None
    earnings_revision_score = breadth_row.get("earnings_revision_score") if breadth_row else None
    breadth_score = breadth_row.get("breadth_score") if breadth_row else None
    relative_strength_score = price_factors.relative_strength_score if price_factors else None
    trend_score = price_factors.trend_score if price_factors else None
    overheat_score = price_factors.overheat_score if price_factors else None
    risk_score = price_factors.price_risk_score if price_factors else None
    return_1m = price_factors.return_1m if price_factors else None
    flow_score = _flow_score_stub(industry_id, as_of)
    macro_fit_score = _macro_fit_score_stub(industry_id, as_of)

    raw_components = {
        "fundamentals_score": fundamentals_score,
        "earnings_revision_score": earnings_revision_score,
        "relative_strength_score": relative_strength_score,
        "flow_score": flow_score,
        "macro_fit_score": macro_fit_score,
        "breadth_score": breadth_score,
    }

    result: ScoreResult = weighted_logistic_score(raw_components, cycle_model_config["cycle_score"])

    weight_cfg = cycle_model_config["cycle_score"]["components"]
    total_weight = sum(weight_cfg.values())
    used_weight = sum(weight_cfg[k] for k, v in raw_components.items() if v is not None and k in weight_cfg)
    data_completeness = (used_weight / total_weight) if total_weight else 0.0

    representative_asset_ids = price_factors.representative_asset_ids if price_factors else []
    representative_market = price_factors.representative_market if price_factors else None

    signal_strength = compute_signal_strength(result.weighted_sum, cycle_model_config=cycle_model_config)
    history_reliability = compute_history_reliability(
        representative_asset_ids, as_of, cycle_model_config=cycle_model_config, db_path=db_path
    )
    model_agreement = compute_model_agreement(
        result.score, price_only_raw_state, cycle_model_config=cycle_model_config
    )
    confidence = signal_strength * data_completeness * history_reliability * model_agreement

    return CycleScoreBundle(
        industry_id=industry_id,
        as_of=as_of,
        score=result.score,
        weighted_sum=result.weighted_sum,
        reason=result.reason,
        data_completeness=data_completeness,
        fundamentals_score=fundamentals_score,
        earnings_revision_score=earnings_revision_score,
        breadth_score=breadth_score,
        relative_strength_score=relative_strength_score,
        trend_score=trend_score,
        overheat_score=overheat_score,
        risk_score=risk_score,
        flow_score=flow_score,
        macro_fit_score=macro_fit_score,
        return_1m=return_1m,
        representative_asset_ids=representative_asset_ids,
        representative_market=representative_market,
        signal_strength=signal_strength,
        history_reliability=history_reliability,
        model_agreement=model_agreement,
        confidence=confidence,
        components=[c.to_dict() for c in result.components],
    )
