from __future__ import annotations

"""Phase 5 (kickoff, price-only scope): walk-forward validation for the
Phase 1-B PRICE-ONLY signal (`committee.industry_cycle.price_state_machine`),
built entirely on the ~3.5 years of real KR/US price history already
backfilled via `scripts/backfill_industry_prices.py`.

Why price-only and not the full `industry_cycle_signal` model
----------------------------------------------------------------
As of this module's creation, the full model (fundamentals + earnings
revision + breadth + relative strength combined,
`committee.industry_cycle.cycle_scoring`) has only ONE real weekly
observation in the database. A walk-forward test needs many independent
signal events to say anything statistically meaningful; running one now
against a single week would either (a) report noise dressed up as a result,
or (b) require inventing historical `industry_cycle_signal` rows that were
never actually computed at the time -- both violate the "성과 조작 금지"
constraint. The price-only signal, by contrast, has real weekly history
across ~3.5 years for the backfilled sample assets, so it can be validated
honestly today.

Design (no parallel scoring logic)
-----------------------------------
`run_walkforward` does not reimplement scoring -- it calls the exact same
production entrypoint (`price_factor_runner.run_factor_batch`) once per
historical weekly `as_of`, so the backtest can never silently diverge from
what the live weekly job actually computes. This persists real
`industry_factor_weekly` / `industry_price_state_weekly` rows for every
historical week, exactly as if the job had been run live back then.

`evaluate_signal_events` then reads back every persisted state row with an
actionable `action_signal` and computes REAL forward returns via
`price_backtest.compute_forward_returns` (a Phase 1-B primitive that
already returns `None` per horizon whenever less trading history exists
than the horizon needs -- never a fabricated number), persisting each
result into `industry_price_signal_performance` (a table Phase 1-B already
defined for exactly this purpose).
"""

import copy
from datetime import date, timedelta
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from committee.industry_cycle import factor_repository, price_backtest, price_features, price_model_config, price_repository
from committee.industry_cycle.price_factor_runner import FactorTarget, run_factor_batch
from committee.industry_cycle.price_state_machine import (
    ACTION_DETERIORATION_CONFIRMED,
    ACTION_OVERHEAT_WARNING,
    ACTION_RECOVERY_CONFIRMED,
)

HORIZONS_TRADING_DAYS = {"1m": 21, "3m": 63, "6m": 126, "12m": 252}

ACTIONABLE_SIGNAL_STATES = {
    ACTION_RECOVERY_CONFIRMED: "recovery_confirmed",
    ACTION_OVERHEAT_WARNING: "overheat_warning",
    ACTION_DETERIORATION_CONFIRMED: "deterioration_confirmed",
}


def generate_weekly_as_of_dates(start: str, end: str, *, weekday: int = 4) -> List[str]:
    """Every calendar date matching `weekday` (0=Mon..6=Sun, default 4=Friday)
    in `[start, end]`, inclusive, ascending. Purely calendar-based -- does not
    need to land on an actual trading day, since `get_prices_as_of` already
    resolves to the latest trading day on-or-before whatever `as_of` it's
    given."""
    d0 = date.fromisoformat(start)
    d1 = date.fromisoformat(end)
    if d1 < d0:
        return []
    offset = (weekday - d0.weekday()) % 7
    current = d0 + timedelta(days=offset)
    dates: List[str] = []
    while current <= d1:
        dates.append(current.isoformat())
        current += timedelta(days=7)
    return dates


def run_walkforward(
    targets: Iterable[FactorTarget],
    *,
    as_of_dates: Iterable[str],
    model_config: Dict[str, Any],
    db_path: Path | None = None,
) -> Dict[str, int]:
    """Runs the real production weekly pipeline for every historical `as_of`
    in `as_of_dates` (ascending order matters: each week's confirmation
    streak is read from the previously-persisted week, exactly like the live
    job). Returns `{as_of: ok_count}` -- callers should query
    `factor_repository.list_price_state_weekly` directly for analysis, since
    a multi-year weekly backtest can produce thousands of rows."""
    targets = list(targets)
    tally: Dict[str, int] = {}
    for as_of in sorted(as_of_dates):
        results = run_factor_batch(targets, as_of=as_of, model_config=model_config, dry_run=False, db_path=db_path)
        tally[as_of] = sum(1 for r in results if r.status == "ok")
    return tally


def evaluate_signal_events(
    model_version: str,
    *,
    horizons: Optional[Dict[str, int]] = None,
    db_path: Path | None = None,
) -> List[Dict[str, Any]]:
    """For every persisted `industry_price_state_weekly` row (any model
    version already run via `run_walkforward`) whose `action_signal` is one
    of the three actionable signals, compute real forward asset/benchmark/
    excess returns and persist them into `industry_price_signal_performance`.

    Returns the flat list of persisted event dicts (one per
    signal-event x horizon). `benchmark_asset_id` is read back from the
    matching `industry_factor_weekly` row (KR -> KOSPI / US -> S&P 500,
    already resolved by `price_factor_runner.build_targets_from_universe`
    at compute time) so this function never re-derives it.
    """
    horizons = horizons or HORIZONS_TRADING_DAYS
    state_rows = [
        r for r in factor_repository.list_price_state_weekly(db_path=db_path)
        if r.get("model_version") == model_version and r.get("action_signal") in ACTIONABLE_SIGNAL_STATES
    ]

    price_series_cache: Dict[str, List[Any]] = {}

    def _series(asset_id: str) -> List[Any]:
        if asset_id not in price_series_cache:
            rows = price_repository.get_prices(asset_id, db_path=db_path)
            price_series_cache[asset_id] = price_features.build_price_series(rows)
        return price_series_cache[asset_id]

    events: List[Dict[str, Any]] = []
    for state_row in state_rows:
        asset_id = state_row["asset_id"]
        as_of = state_row["as_of"]
        factor_row = factor_repository.get_factor_weekly(asset_id, as_of, model_version, db_path=db_path)
        if factor_row is None or not factor_row.get("price_trade_date"):
            continue  # can't locate the exact trade date the signal fired on -- skip, don't guess

        signal_at = factor_row["price_trade_date"]
        benchmark_asset_id = factor_row.get("benchmark_asset_id")
        asset_series = _series(asset_id)
        benchmark_series = _series(benchmark_asset_id) if benchmark_asset_id else None

        forward_results = price_backtest.compute_forward_returns(
            asset_series, benchmark_series, signal_at=signal_at, horizons=horizons
        )
        for result in forward_results:
            record = {
                "industry_id": state_row["industry_id"],
                "market": state_row["market"],
                "asset_id": asset_id,
                "benchmark_asset_id": benchmark_asset_id,
                "signal_at": as_of,
                "signal_state": ACTIONABLE_SIGNAL_STATES[state_row["action_signal"]],
                "model_version": model_version,
                "horizon_label": result.horizon_label,
                "horizon_trading_days": result.horizon_trading_days,
                "asset_return": result.asset_return,
                "benchmark_return": result.benchmark_return,
                "excess_return": result.excess_return,
            }
            factor_repository.upsert_price_signal_performance(record, db_path=db_path)
            events.append(record)
    return events


def summarize_by_state(model_version: str, db_path: Path | None = None) -> Dict[str, Dict[str, Dict[str, Any]]]:
    """`{signal_state: {horizon_label: price_backtest.summarize_performance(...)}}`
    over every persisted `industry_price_signal_performance` row for
    `model_version`."""
    rows = [
        r for r in factor_repository.list_price_signal_performance(db_path=db_path)
        if r.get("model_version") == model_version
    ]
    by_state: Dict[str, List[Dict[str, Any]]] = {}
    for row in rows:
        by_state.setdefault(row["signal_state"], []).append(row)

    summary: Dict[str, Dict[str, Dict[str, Any]]] = {}
    for state, events in by_state.items():
        summary[state] = {
            label: price_backtest.summarize_performance(events, horizon_label=label)
            for label in HORIZONS_TRADING_DAYS
        }
    return summary


def run_threshold_sensitivity(
    targets: Iterable[FactorTarget],
    *,
    as_of_dates: Iterable[str],
    base_model_config: Dict[str, Any],
    variants: Dict[str, Dict[str, float]],
    db_path: Path | None = None,
) -> Dict[str, Dict[str, Dict[str, Dict[str, Any]]]]:
    """Threshold sensitivity analysis: for each `variants[name]` (a partial
    `state_thresholds` override, e.g. `{"recovery_change_min": 1.0}`), runs
    the SAME `run_walkforward` -> `evaluate_signal_events` ->
    `summarize_by_state` pipeline as the baseline run, under a distinct
    `model_version` derived from the baseline's.

    This is deliberately not a separate in-memory scoring path: every
    variant is persisted to the real `industry_factor_weekly` /
    `industry_price_state_weekly` / `industry_price_signal_performance`
    tables under its own `model_version`, so results can never silently
    diverge from what `_compute_one` (the actual production scorer) would
    produce for those thresholds, and every variant run remains fully
    reproducible/inspectable later (design doc: "model_version별 결과
    재현"). Returns `{variant_name: summarize_by_state(...)}`; the caller is
    expected to also inspect the baseline's own `summarize_by_state(...)`
    for comparison.
    """
    as_of_dates = list(as_of_dates)
    results: Dict[str, Dict[str, Dict[str, Dict[str, Any]]]] = {}
    for name, overrides in variants.items():
        variant_config = copy.deepcopy(base_model_config)
        variant_config["state_thresholds"].update(overrides)
        variant_config["model_version"] = f"{base_model_config['model_version']}__sensitivity_{name}"

        errors = price_model_config.validate_price_model_config(variant_config)
        if errors:
            raise ValueError(f"variant '{name}' produced an invalid model_config: {errors}")

        run_walkforward(targets, as_of_dates=as_of_dates, model_config=variant_config, db_path=db_path)
        evaluate_signal_events(variant_config["model_version"], db_path=db_path)
        results[name] = summarize_by_state(variant_config["model_version"], db_path=db_path)
    return results
