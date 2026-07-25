from __future__ import annotations

"""Phase 3: per-industry ETF/stock candidate ranking (orchestration, DB reads + writes via repository).

Ties together every other Phase 3 module for ONE `(industry_id, as_of)`:
- `etf_quality` for every `ETF`-type asset in `industry_asset_map`.
- `stock_scoring` (+ a cross-sectional liquidity percentile computed HERE,
  since only this orchestration layer sees every candidate at once) for
  every `STOCK`-type asset.
- `industry_breadth_scoring` for the industry-level `earnings_revision_score`
  / `breadth_score`.

Design doc section 8 policy, enforced here (not by loosening any
threshold): "추천 수를 채우기 위해 기준 미달 종목을 포함하지 않는다" -- ranks
are assigned ONLY to non-excluded assets; an excluded asset always gets
`rank=None` regardless of how few candidates remain.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from committee.industry_cycle import (
    etf_quality,
    industry_breadth_scoring,
    price_repository,
    price_universe,
    repository,
    stock_scoring,
)


def is_valid_at(mapping: Dict[str, Any], as_of: str) -> bool:
    valid_from = mapping.get("valid_from")
    valid_to = mapping.get("valid_to")
    if valid_from and as_of < str(valid_from):
        return False
    if valid_to and as_of > str(valid_to):
        return False
    return True


def _liquidity_percentiles(turnover_levels: Dict[str, Optional[float]]) -> Dict[str, Optional[float]]:
    """Cross-sectional percentile (0=lowest .. 1=highest) of each ticker's turnover_level.

    `None` inputs stay `None` (never assigned a fabricated percentile). A
    single known value gets percentile 1.0 (nothing below it to rank
    against, so it cannot be flagged as "bottom of the market").
    """
    known = {k: v for k, v in turnover_levels.items() if v is not None}
    if not known:
        return {k: None for k in turnover_levels}
    ordered = sorted(known.items(), key=lambda kv: kv[1])
    n = len(ordered)
    pct_by_key: Dict[str, float] = {}
    for i, (key, _value) in enumerate(ordered):
        pct_by_key[key] = (i / (n - 1)) if n > 1 else 1.0
    return {k: pct_by_key.get(k) for k in turnover_levels}


@dataclass(frozen=True)
class CandidateRankingResult:
    industry_id: str
    as_of: str
    etf_candidates: List[Dict[str, Any]] = field(default_factory=list)
    stock_candidates: List[Dict[str, Any]] = field(default_factory=list)
    earnings_revision: Optional[industry_breadth_scoring.IndustryEarningsRevisionBundle] = None
    breadth: Optional[industry_breadth_scoring.IndustryBreadthBundle] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "industry_id": self.industry_id,
            "as_of": self.as_of,
            "etf_candidates": self.etf_candidates,
            "stock_candidates": self.stock_candidates,
            "earnings_revision": self.earnings_revision.to_dict() if self.earnings_revision else None,
            "breadth": self.breadth.to_dict() if self.breadth else None,
        }


def build_candidates_for_industry(
    industry_id: str,
    as_of: str,
    *,
    stock_model_config: Dict[str, Any],
    price_feature_config: Dict[str, Any],
    etf_quality_catalog: Dict[str, Any],
    price_universe_payload: Dict[str, Any],
    db_path: Path | None = None,
) -> CandidateRankingResult:
    """Compute (but do not persist) every ETF/stock candidate for one industry as of `as_of`."""
    mappings = [m for m in repository.list_industry_assets(industry_id, db_path=db_path) if is_valid_at(m, as_of)]
    etf_mappings = [m for m in mappings if (m.get("asset_type") or "").upper() == "ETF"]
    stock_mappings = [m for m in mappings if (m.get("asset_type") or "").upper() == "STOCK"]

    # --- ETF candidates: quality filter only, ranked by declared representativeness weight ---
    etf_candidates: List[Dict[str, Any]] = []
    for m in etf_mappings:
        asset_id = m["asset_id"]
        quality = etf_quality.evaluate_etf_from_catalog(
            asset_id, as_of, catalog=etf_quality_catalog, stock_model_config=stock_model_config, db_path=db_path
        )
        etf_candidates.append(
            {
                "asset_id": asset_id,
                "asset_type": "ETF",
                "market": m.get("market"),
                "weight": m.get("weight"),
                "score": None,
                "rank": None,
                "excluded": not quality.passed,
                "exclusion_reasons": quality.reasons,
                "unknown_checks": quality.unknown_checks,
                "data_completeness": None,
            }
        )
    passing_etfs = sorted(
        (e for e in etf_candidates if not e["excluded"]),
        key=lambda e: -(e.get("weight") or 0.0),
    )
    for rank, e in enumerate(passing_etfs, start=1):
        e["rank"] = rank

    # --- STOCK candidates: cross-sectional liquidity percentile, then per-stock scoring ---
    turnover_levels: Dict[str, Optional[float]] = {}
    for m in stock_mappings:
        asset_id = m["asset_id"]
        asset_rows = price_repository.get_prices_as_of(asset_id, as_of, db_path=db_path)
        turnover_levels[asset_id] = stock_scoring.turnover_level(asset_rows) if asset_rows else None
    liquidity_percentiles = _liquidity_percentiles(turnover_levels)

    stock_candidates: List[Dict[str, Any]] = []
    for m in stock_mappings:
        asset_id = m["asset_id"]
        market = m.get("market") or "US"
        benchmark_asset_id = price_universe.get_benchmark_asset_id(market, price_universe_payload)
        bundle = stock_scoring.compute_stock_score(
            asset_id,
            industry_id,
            as_of,
            market=market,
            benchmark_asset_id=benchmark_asset_id,
            stock_model_config=stock_model_config,
            price_feature_config=price_feature_config,
            liquidity_percentile=liquidity_percentiles.get(asset_id),
            db_path=db_path,
        )
        stock_candidates.append(
            {
                "asset_id": asset_id,
                "asset_type": "STOCK",
                "market": market,
                "score": bundle.score,
                "rank": None,
                "excluded": bundle.exclusion.excluded if bundle.exclusion else False,
                "exclusion_reasons": bundle.exclusion.reasons if bundle.exclusion else [],
                "unknown_checks": bundle.exclusion.unknown_checks if bundle.exclusion else [],
                "sub_scores": {k: v.to_dict() for k, v in bundle.sub_scores.items()},
                "data_completeness": bundle.data_completeness,
            }
        )
    passing_stocks = sorted(
        (s for s in stock_candidates if not s["excluded"] and s["score"] is not None),
        key=lambda s: -s["score"],
    )
    for rank, s in enumerate(passing_stocks, start=1):
        s["rank"] = rank

    # --- industry-level earnings_revision_score / breadth_score ---
    tickers = [m["asset_id"] for m in stock_mappings]
    earnings_revision = industry_breadth_scoring.compute_industry_earnings_revision_score(
        industry_id, as_of, tickers=tickers, stock_model_config=stock_model_config, db_path=db_path
    )
    ticker_markets = {m["asset_id"]: (m.get("market") or "US") for m in stock_mappings}
    ticker_benchmarks = {t: price_universe.get_benchmark_asset_id(mk, price_universe_payload) for t, mk in ticker_markets.items()}
    breadth = industry_breadth_scoring.compute_industry_breadth_score(
        industry_id,
        as_of,
        ticker_markets=ticker_markets,
        ticker_benchmarks=ticker_benchmarks,
        stock_model_config=stock_model_config,
        price_feature_config=price_feature_config,
        db_path=db_path,
    )

    return CandidateRankingResult(
        industry_id=industry_id,
        as_of=as_of,
        etf_candidates=etf_candidates,
        stock_candidates=stock_candidates,
        earnings_revision=earnings_revision,
        breadth=breadth,
    )


def persist_candidate_ranking(
    result: CandidateRankingResult,
    *,
    model_version: str,
    data_cutoff_at: str,
    db_path: Path | None = None,
) -> int:
    """Write every candidate + the industry earnings-revision/breadth row via `candidate_repository`.

    Returns the number of `industry_candidate` rows written. Import is
    local to avoid a module-load-time dependency cycle risk between this
    orchestration module and the repository.
    """
    from committee.industry_cycle import candidate_repository

    count = 0
    for candidate in (*result.etf_candidates, *result.stock_candidates):
        candidate_repository.upsert_industry_candidate(
            {
                "industry_id": result.industry_id,
                "as_of": result.as_of,
                "model_version": model_version,
                "data_cutoff_at": data_cutoff_at,
                "asset_id": candidate["asset_id"],
                "asset_type": candidate["asset_type"],
                "market": candidate.get("market"),
                "score": candidate.get("score"),
                "rank": candidate.get("rank"),
                "excluded": candidate.get("excluded", False),
                "exclusion_reasons": candidate.get("exclusion_reasons"),
                "unknown_checks": candidate.get("unknown_checks"),
                "sub_scores": candidate.get("sub_scores"),
                "data_completeness": candidate.get("data_completeness"),
            },
            db_path=db_path,
        )
        count += 1

    if result.earnings_revision is not None or result.breadth is not None:
        er = result.earnings_revision
        br = result.breadth
        candidate_repository.upsert_industry_earnings_breadth_weekly(
            {
                "industry_id": result.industry_id,
                "as_of": result.as_of,
                "model_version": model_version,
                "data_cutoff_at": data_cutoff_at,
                "earnings_revision_score": er.score if er else None,
                "earnings_revision_weighted_sum": er.weighted_sum if er else None,
                "earnings_revision_reason": er.reason if er else None,
                "earnings_revision_data_completeness": er.data_completeness if er else None,
                "earnings_revision_evidence": [e.to_dict() for e in er.evidence] if er else None,
                "breadth_score": br.score if br else None,
                "breadth_weighted_sum": br.weighted_sum if br else None,
                "breadth_reason": br.reason if br else None,
                "breadth_data_completeness": br.data_completeness if br else None,
                "breadth_evidence": [e.to_dict() for e in br.evidence] if br else None,
                "n_tickers_considered": er.n_tickers_considered if er else (br.n_tickers_considered if br else None),
            },
            db_path=db_path,
        )

    return count
