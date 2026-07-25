from __future__ import annotations

"""Phase 1-B weekly price-factor run orchestration (pure logic where possible).

`scripts/run_industry_price_factors.py` is a thin CLI wrapper around
`run_factor_batch` here, mirroring the `price_backfill.py` /
`backfill_industry_prices.py` split from Phase 1-A, so the run structure and
dry-run behavior can be unit tested without touching the DB (default) or
requiring the `scripts/` folder to be importable as a package.

Point-in-time safety: this module only ever reads asset/benchmark prices
via `price_repository.get_prices_as_of(asset_id, as_of=<caller-provided
as_of>)`. Nothing here queries future data, so a signal computed for a past
`as_of` (via `--as-of` on the CLI) reproduces exactly what would have been
knowable that week (task item 8: "특정 날짜를 지정해 과거 한 주를 재현
가능").

Failure isolation: one asset's failure (bad config entry, unexpected data
shape, ...) must never stop the loop over the remaining assets, mirroring
`price_backfill.run_backfill`.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from committee.industry_cycle import factor_repository, price_repository
from committee.industry_cycle.price_features import build_weekly_features
from committee.industry_cycle.price_scoring import compute_price_score_bundle
from committee.industry_cycle.price_state_machine import apply_confirmation_rule, classify_raw_state


@dataclass(frozen=True)
class FactorTarget:
    """One (asset, industry, benchmark) tuple to compute this week's factors for."""

    asset_id: str
    market: str
    industry_id: str
    benchmark_asset_id: Optional[str]


@dataclass
class FactorRunResult:
    asset_id: str
    industry_id: str
    market: str
    benchmark_asset_id: Optional[str]
    as_of: str
    status: str  # 'planned' | 'ok' | 'failed'
    price_only_state: Optional[str] = None
    confirmation_status: Optional[str] = None
    action_signal: Optional[str] = None
    relative_strength_score: Optional[float] = None
    trend_score: Optional[float] = None
    overheat_score: Optional[float] = None
    price_risk_score: Optional[float] = None
    data_completeness: Optional[float] = None
    error: Optional[str] = None


def build_targets_from_universe(universe: Dict[str, Any]) -> List[FactorTarget]:
    """Build one `FactorTarget` per `assets[]` entry that declares an `industry_id`.

    The benchmark for each target is resolved from `universe["benchmarks"]`
    by matching `market` (design doc section 2: KR -> KOSPI, US -> S&P 500),
    so the KR/US benchmark split is entirely config-driven, never
    hardcoded (task item 9: "한국·미국 벤치마크 분리").
    """
    benchmarks_by_market = {
        str(b["market"]): str(b["asset_id"]) for b in universe.get("benchmarks", []) if b.get("market")
    }
    targets: List[FactorTarget] = []
    for entry in universe.get("assets", []):
        industry_id = entry.get("industry_id")
        if not industry_id:
            continue
        market = str(entry["market"])
        targets.append(
            FactorTarget(
                asset_id=str(entry["asset_id"]),
                market=market,
                industry_id=str(industry_id),
                benchmark_asset_id=benchmarks_by_market.get(market),
            )
        )
    return targets


def plan_factor_batch(targets: Iterable[FactorTarget], *, as_of: str) -> List[FactorRunResult]:
    """Return the no-op "what would happen" plan for `targets` (dry-run)."""
    return [
        FactorRunResult(
            asset_id=t.asset_id,
            industry_id=t.industry_id,
            market=t.market,
            benchmark_asset_id=t.benchmark_asset_id,
            as_of=as_of,
            status="planned",
        )
        for t in targets
    ]


def _compute_one(
    target: FactorTarget,
    *,
    as_of: str,
    model_config: Dict[str, Any],
    db_path: Path | None,
) -> FactorRunResult:
    model_version = model_config["model_version"]

    asset_rows = price_repository.get_prices_as_of(target.asset_id, as_of, db_path=db_path)
    benchmark_rows = (
        price_repository.get_prices_as_of(target.benchmark_asset_id, as_of, db_path=db_path)
        if target.benchmark_asset_id
        else []
    )

    features = build_weekly_features(
        asset_rows,
        benchmark_rows,
        asset_id=target.asset_id,
        market=target.market,
        benchmark_asset_id=target.benchmark_asset_id,
        as_of=as_of,
        config=model_config,
    )
    scores = compute_price_score_bundle(features, model_config)

    prev_factor = factor_repository.get_latest_factor_before(
        target.asset_id, model_version, as_of, db_path=db_path
    )
    prev_rs = prev_factor.get("relative_strength_score") if prev_factor else None

    raw_state = classify_raw_state(
        scores, model_config["state_thresholds"], prev_relative_strength_score=prev_rs
    )

    prev_state_row = factor_repository.get_latest_price_state_before(
        target.asset_id, model_version, as_of, db_path=db_path
    )
    transition = apply_confirmation_rule(
        raw_state, prev_state_row, confirmation_cfg=model_config["confirmation"]
    )

    factor_record = features.to_dict()
    factor_record.update(
        {
            "industry_id": target.industry_id,
            "model_version": model_version,
            "data_cutoff_at": as_of,
            "relative_strength_score": scores.relative_strength.score,
            "trend_score": scores.trend.score,
            "overheat_score": scores.overheat.score,
            "price_risk_score": scores.price_risk.score,
            "score_breakdown": scores.to_dict(),
        }
    )
    factor_repository.upsert_industry_factor_weekly(factor_record, db_path=db_path)

    state_record = {
        "industry_id": target.industry_id,
        "market": target.market,
        "asset_id": target.asset_id,
        "as_of": as_of,
        "model_version": model_version,
        "price_only_state": transition.raw_state,
        "confirmation_status": transition.confirmation_status,
        "action_signal": transition.action_signal,
        "consecutive_weeks": transition.consecutive_weeks,
        "previous_state": prev_state_row.get("price_only_state") if prev_state_row else None,
        "data_completeness": features.data_completeness,
        "reason": (
            f"raw_state={raw_state} rs={scores.relative_strength.score} tr={scores.trend.score} "
            f"oh={scores.overheat.score} risk={scores.price_risk.score}"
        ),
        "contributing_factors": scores.to_dict(),
    }
    factor_repository.upsert_price_state_weekly(state_record, db_path=db_path)

    return FactorRunResult(
        asset_id=target.asset_id,
        industry_id=target.industry_id,
        market=target.market,
        benchmark_asset_id=target.benchmark_asset_id,
        as_of=as_of,
        status="ok",
        price_only_state=transition.raw_state,
        confirmation_status=transition.confirmation_status,
        action_signal=transition.action_signal,
        relative_strength_score=scores.relative_strength.score,
        trend_score=scores.trend.score,
        overheat_score=scores.overheat.score,
        price_risk_score=scores.price_risk.score,
        data_completeness=features.data_completeness,
    )


def run_factor_batch(
    targets: Iterable[FactorTarget],
    *,
    as_of: str,
    model_config: Dict[str, Any],
    dry_run: bool = True,
    db_path: Path | None = None,
) -> List[FactorRunResult]:
    """Compute (and, unless `dry_run`, persist) weekly price factors/state for `targets`.

    When `dry_run` is True (the default), no DB read/write happens at all --
    this returns the same plan as `plan_factor_batch` (task item 8: "기본은
    dry-run"). Real DB access only happens when a caller explicitly passes
    `dry_run=False` (`--execute` on the CLI).
    """
    targets = list(targets)
    if dry_run:
        return plan_factor_batch(targets, as_of=as_of)

    results: List[FactorRunResult] = []
    for target in targets:
        try:
            results.append(_compute_one(target, as_of=as_of, model_config=model_config, db_path=db_path))
        except Exception as exc:  # noqa: BLE001 - one asset's failure must not stop the batch
            results.append(
                FactorRunResult(
                    asset_id=target.asset_id,
                    industry_id=target.industry_id,
                    market=target.market,
                    benchmark_asset_id=target.benchmark_asset_id,
                    as_of=as_of,
                    status="failed",
                    error=str(exc),
                )
            )
            continue
    return results
