from __future__ import annotations

"""Objective two-axis industry-cycle scoring and 12-week forecast.

The model intentionally avoids hand-tuned score weights and logistic scales:

* KPI cycle = expanding, within-industry percentile of the fundamentals score.
* Market confirmation = equal mean of weekly cross-sectional RS and breadth percentiles.
* Earnings revision is an informational overlay until it has enough history.
* 12-week excess return = ridge regression trained only on outcomes fully known
  by the requested ``as_of``.  Ridge strength is selected on the latest
  time-ordered validation block, not hand-picked for the live prediction.
"""

from dataclasses import dataclass
from datetime import date, timedelta
from math import sqrt
from pathlib import Path
from statistics import NormalDist
from typing import Any, Iterable

from committee.industry_cycle import (
    candidate_repository,
    cycle_scoring,
    cycle_v2_repository,
    fundamentals_repository,
    price_repository,
    price_universe,
    repository,
)
from committee.industry_cycle.candidate_ranking import is_valid_at
from committee.industry_cycle.time_contract import is_known_by


# A chronological backfill calls ``compute_cycle_v2_batch`` once per week.
# Once a 12-week outcome has matured it is immutable, so retain it for the
# life of that process instead of repeating the same indexed price lookups
# for every later week.  The key includes the DB path and horizon to keep
# tests/configurations isolated.
_OUTCOME_CACHE: dict[tuple[str, int, str, str], float | None] = {}
_PRICE_SERIES_CACHE: dict[tuple[str, str], list[dict[str, Any]]] = {}


@dataclass(frozen=True)
class RidgeModel:
    feature_means: tuple[float, float]
    feature_scales: tuple[float, float]
    target_mean: float
    coefficients: tuple[float, float]
    ridge_lambda: float
    rmse: float

    def predict(self, cycle_score: float, market_score: float) -> float:
        features = (cycle_score, market_score)
        standardized = [
            (features[index] - self.feature_means[index]) / self.feature_scales[index]
            for index in range(2)
        ]
        return self.target_mean + sum(
            coefficient * standardized[index]
            for index, coefficient in enumerate(self.coefficients)
        )


def percentile_rank(value: float | None, population: Iterable[float | None]) -> float | None:
    """Mid-rank empirical percentile in [0, 100], stable in the presence of ties."""
    if value is None:
        return None
    values = sorted(float(item) for item in population if item is not None)
    if not values:
        return None
    below = sum(1 for item in values if item < float(value))
    equal = sum(1 for item in values if item == float(value))
    return round(100.0 * (below + 0.5 * equal) / len(values), 4)


def _mean(values: Iterable[float | None]) -> float | None:
    available = [float(value) for value in values if value is not None]
    return sum(available) / len(available) if available else None


def _sample_scale(values: list[float]) -> float:
    if len(values) < 2:
        return 1.0
    mean = sum(values) / len(values)
    variance = sum((value - mean) ** 2 for value in values) / len(values)
    scale = sqrt(variance)
    return scale if scale > 1e-12 else 1.0


def _fit_ridge(rows: list[tuple[float, float, float]], ridge_lambda: float) -> RidgeModel:
    if not rows:
        raise ValueError("ridge fit requires observations")
    x1 = [row[0] for row in rows]
    x2 = [row[1] for row in rows]
    targets = [row[2] for row in rows]
    means = (sum(x1) / len(x1), sum(x2) / len(x2))
    scales = (_sample_scale(x1), _sample_scale(x2))
    target_mean = sum(targets) / len(targets)
    z1 = [(value - means[0]) / scales[0] for value in x1]
    z2 = [(value - means[1]) / scales[1] for value in x2]
    centered_y = [value - target_mean for value in targets]

    a11 = sum(value * value for value in z1) + ridge_lambda
    a22 = sum(value * value for value in z2) + ridge_lambda
    a12 = sum(left * right for left, right in zip(z1, z2))
    b1 = sum(value * target for value, target in zip(z1, centered_y))
    b2 = sum(value * target for value, target in zip(z2, centered_y))
    determinant = a11 * a22 - a12 * a12
    if abs(determinant) < 1e-12:
        coefficients = (0.0, 0.0)
    else:
        coefficients = (
            (b1 * a22 - b2 * a12) / determinant,
            (a11 * b2 - a12 * b1) / determinant,
        )

    model = RidgeModel(means, scales, target_mean, coefficients, float(ridge_lambda), 0.0)
    residuals = [model.predict(row[0], row[1]) - row[2] for row in rows]
    rmse = sqrt(sum(value * value for value in residuals) / len(residuals))
    return RidgeModel(means, scales, target_mean, coefficients, float(ridge_lambda), rmse)


def _select_ridge_model(
    observations: list[dict[str, Any]], *, lambdas: list[float], validation_fraction: float
) -> RidgeModel:
    weeks = sorted({str(row["as_of"]) for row in observations})
    validation_week_count = max(1, int(round(len(weeks) * validation_fraction)))
    validation_weeks = set(weeks[-validation_week_count:])
    training_rows = [
        (float(row["kpi_cycle_score"]), float(row["market_confirmation_score"]), float(row["target"]))
        for row in observations
        if row["as_of"] not in validation_weeks
    ]
    validation_rows = [row for row in observations if row["as_of"] in validation_weeks]
    if not training_rows or not validation_rows:
        raise ValueError("time-ordered ridge validation requires both train and validation observations")

    best_lambda = float(lambdas[0])
    best_mse: float | None = None
    for ridge_lambda in lambdas:
        candidate = _fit_ridge(training_rows, float(ridge_lambda))
        errors = [
            candidate.predict(float(row["kpi_cycle_score"]), float(row["market_confirmation_score"]))
            - float(row["target"])
            for row in validation_rows
        ]
        mse = sum(value * value for value in errors) / len(errors)
        if best_mse is None or mse < best_mse:
            best_mse = mse
            best_lambda = float(ridge_lambda)

    all_rows = [
        (float(row["kpi_cycle_score"]), float(row["market_confirmation_score"]), float(row["target"]))
        for row in observations
    ]
    return _fit_ridge(all_rows, best_lambda)


def _price_on_or_before(asset_id: str, target_date: str, known_as_of: str, db_path: Path | None) -> float | None:
    cache_key = (str(db_path or ""), asset_id)
    if cache_key not in _PRICE_SERIES_CACHE:
        _PRICE_SERIES_CACHE[cache_key] = price_repository.get_prices(asset_id, db_path=db_path)
    for row in reversed(_PRICE_SERIES_CACHE[cache_key]):
        if str(row.get("trade_date") or "") > target_date:
            continue
        if not is_known_by(row, known_as_of, known_at_field="available_at"):
            continue
        value = row.get("adj_close_price")
        if value is None:
            value = row.get("close_price")
        if value is not None:
            return float(value)
    return None


def _basket_excess_return(
    industry_id: str,
    signal_as_of: str,
    target_as_of: str,
    *,
    known_as_of: str,
    db_path: Path | None,
) -> float | None:
    universe = price_universe.load_price_universe()
    benchmark_by_market = {
        str(row["market"]): str(row["asset_id"])
        for row in universe.get("benchmarks", [])
        if row.get("market") and row.get("asset_id")
    }
    mappings = [
        row for row in repository.list_industry_assets(industry_id, db_path=db_path)
        if is_valid_at(row, signal_as_of)
    ]
    weighted_returns: list[tuple[float, float]] = []
    for mapping in mappings:
        asset_id = str(mapping["asset_id"])
        market = str(mapping.get("market") or "")
        benchmark_id = benchmark_by_market.get(market)
        if not benchmark_id:
            continue
        asset_start = _price_on_or_before(asset_id, signal_as_of, known_as_of, db_path)
        asset_end = _price_on_or_before(asset_id, target_as_of, known_as_of, db_path)
        benchmark_start = _price_on_or_before(benchmark_id, signal_as_of, known_as_of, db_path)
        benchmark_end = _price_on_or_before(benchmark_id, target_as_of, known_as_of, db_path)
        if None in (asset_start, asset_end, benchmark_start, benchmark_end):
            continue
        if not asset_start or not benchmark_start:
            continue
        excess = asset_end / asset_start - benchmark_end / benchmark_start
        weighted_returns.append((excess, float(mapping.get("weight") or 1.0)))
    total_weight = sum(weight for _, weight in weighted_returns)
    if total_weight <= 0:
        return None
    return sum(value * weight for value, weight in weighted_returns) / total_weight


def _matured_training_observations(
    as_of: str,
    *,
    model_version: str,
    horizon_days: int,
    db_path: Path | None,
) -> list[dict[str, Any]]:
    cutoff = date.fromisoformat(as_of) - timedelta(days=horizon_days)
    rows = cycle_v2_repository.list_cycle_v2_signals(
        model_version=model_version, before_as_of=as_of, db_path=db_path
    )
    observations: list[dict[str, Any]] = []
    for row in rows:
        if str(row["as_of"]) > cutoff.isoformat():
            continue
        if row.get("kpi_cycle_score") is None or row.get("market_confirmation_score") is None:
            continue
        target_as_of = (date.fromisoformat(str(row["as_of"])) + timedelta(days=horizon_days)).isoformat()
        cache_key = (str(db_path or ""), horizon_days, str(row["industry_id"]), str(row["as_of"]))
        if cache_key not in _OUTCOME_CACHE:
            _OUTCOME_CACHE[cache_key] = _basket_excess_return(
                str(row["industry_id"]), str(row["as_of"]), target_as_of,
                known_as_of=as_of, db_path=db_path,
            )
        target = _OUTCOME_CACHE[cache_key]
        if target is None:
            continue
        observations.append({**row, "target": target})
    return observations


def _cycle_phase(kpi_cycle_score: float | None, slope: float | None) -> str:
    if kpi_cycle_score is None or slope is None:
        return "INSUFFICIENT_DATA"
    if kpi_cycle_score < 50.0:
        return "RECOVERY_EARLY" if slope > 0 else "RECESSION"
    return "EXPANSION" if slope >= 0 else "SLOWING"


def _entry_decision(
    *,
    kpi_cycle_score: float | None,
    slope: float | None,
    market_score: float | None,
    overheat_percentile: float | None,
    expected_return: float | None,
) -> tuple[str, str]:
    if kpi_cycle_score is None or slope is None or market_score is None:
        return "INSUFFICIENT_DATA", "KPI 또는 시장확인 데이터가 부족합니다."
    if expected_return is None:
        if slope > 0 and market_score >= 50.0:
            return "WATCH", "KPI와 시장확인이 개선 중이지만 12주 학습표본이 아직 부족합니다."
        return "OBSERVE", "12주 학습표본이 쌓일 때까지 관찰합니다."
    if expected_return <= 0 and slope <= 0:
        return "AVOID", "KPI 방향과 12주 예상 초과수익이 모두 부정적입니다."
    if expected_return > 0 and overheat_percentile is not None and overheat_percentile >= 75.0:
        return "HOLD_EXTENDED", "예상수익은 양수지만 가격 과열 백분위가 상위 25%입니다."
    if expected_return > 0 and slope > 0 and kpi_cycle_score < 50.0 and market_score >= 50.0:
        return "EARLY_ENTRY", "낮은 KPI 국면에서 방향이 상승 전환했고 시장확인과 12주 예측도 양수입니다."
    if expected_return > 0 and slope >= 0 and kpi_cycle_score >= 50.0 and market_score >= 50.0:
        return "CONFIRM_ADD", "KPI 확장, 시장확인, 12주 예측이 같은 방향입니다."
    if expected_return > 0 and market_score >= 50.0:
        return "HOLD", "12주 예측과 시장확인은 양수지만 경기 진입 조건은 완전하지 않습니다."
    if slope > 0:
        return "WATCH", "KPI는 상승 중이나 시장확인 또는 12주 예측의 확인이 필요합니다."
    return "NEUTRAL", "경기와 시장 신호가 혼재합니다."


def compute_cycle_v2_batch(
    industry_ids: Iterable[str],
    *,
    as_of: str,
    config: dict[str, Any],
    fundamentals_model_version: str,
    candidate_model_version: str,
    price_model_version: str,
    persist: bool = True,
    db_path: Path | None = None,
) -> list[dict[str, Any]]:
    """Compute one complete weekly cross-section and optionally persist it."""
    industry_ids = sorted(set(industry_ids))
    raw: dict[str, dict[str, float | None]] = {}
    fundamentals_histories: dict[str, list[dict[str, Any]]] = {}
    for industry_id in industry_ids:
        fundamentals_history = [
            row for row in fundamentals_repository.list_fundamentals_weekly(industry_id, db_path=db_path)
            if row.get("model_version") == fundamentals_model_version and str(row.get("as_of")) <= as_of
        ]
        fundamentals_histories[industry_id] = fundamentals_history
        fundamentals = next((row for row in reversed(fundamentals_history) if row.get("as_of") == as_of), None)
        breadth = candidate_repository.get_earnings_breadth_weekly(
            industry_id, as_of, candidate_model_version, db_path=db_path
        )
        prices = cycle_scoring.select_representative_price_factors(
            industry_id, as_of, price_model_version=price_model_version, db_path=db_path
        )
        raw[industry_id] = {
            "fundamentals": fundamentals.get("fundamentals_score") if fundamentals else None,
            "relative_strength": prices.relative_strength_score if prices else None,
            "breadth": breadth.get("breadth_score") if breadth else None,
            "earnings": breadth.get("earnings_revision_score") if breadth else None,
            "overheat": prices.overheat_score if prices else None,
        }

    cross_sections = {
        key: [values[key] for values in raw.values()]
        for key in ("relative_strength", "breadth", "earnings", "overheat")
    }

    provisional: list[dict[str, Any]] = []
    minimum_history = int(config["fundamentals_history_min_weeks"])
    lookback = int(config["slope_lookback_weeks"])
    for industry_id in industry_ids:
        history = fundamentals_histories[industry_id]
        history_scores = [float(row["fundamentals_score"]) for row in history if row.get("fundamentals_score") is not None]
        kpi_raw = raw[industry_id]["fundamentals"]
        kpi_cycle_score = (
            percentile_rank(float(kpi_raw), history_scores)
            if kpi_raw is not None and len(history_scores) >= minimum_history else None
        )
        slope = history_scores[-1] - history_scores[-lookback - 1] if len(history_scores) > lookback else None
        rs_percentile = percentile_rank(raw[industry_id]["relative_strength"], cross_sections["relative_strength"])
        breadth_percentile = percentile_rank(raw[industry_id]["breadth"], cross_sections["breadth"])
        market_score = (
            _mean((rs_percentile, breadth_percentile))
            if rs_percentile is not None and breadth_percentile is not None else None
        )
        earnings_percentile = percentile_rank(raw[industry_id]["earnings"], cross_sections["earnings"])
        overheat_percentile = percentile_rank(raw[industry_id]["overheat"], cross_sections["overheat"])
        coverage = sum(
            value is not None for value in (kpi_cycle_score, rs_percentile, breadth_percentile)
        ) / 3.0
        provisional.append(
            {
                "industry_id": industry_id,
                "as_of": as_of,
                "model_version": config["model_version"],
                "kpi_cycle_score": kpi_cycle_score,
                "kpi_raw_score": kpi_raw,
                "kpi_slope_4w": slope,
                "cycle_phase": _cycle_phase(kpi_cycle_score, slope),
                "market_confirmation_score": market_score,
                "relative_strength_percentile": rs_percentile,
                "breadth_percentile": breadth_percentile,
                "earnings_revision_percentile": earnings_percentile,
                "overheat_percentile": overheat_percentile,
                "data_completeness": coverage,
            }
        )

    forecast_cfg = config["forecast"]
    observations = _matured_training_observations(
        as_of,
        model_version=config["model_version"],
        horizon_days=int(forecast_cfg["horizon_calendar_days"]),
        db_path=db_path,
    )
    training_weeks = len({row["as_of"] for row in observations})
    model: RidgeModel | None = None
    if (
        len(observations) >= int(forecast_cfg["min_training_samples"])
        and training_weeks >= int(forecast_cfg["min_training_weeks"])
    ):
        model = _select_ridge_model(
            observations,
            lambdas=[float(value) for value in forecast_cfg["ridge_lambdas"]],
            validation_fraction=float(forecast_cfg["validation_fraction"]),
        )

    results: list[dict[str, Any]] = []
    for row in provisional:
        predicted: float | None = None
        probability: float | None = None
        if model and row["kpi_cycle_score"] is not None and row["market_confirmation_score"] is not None:
            predicted = model.predict(float(row["kpi_cycle_score"]), float(row["market_confirmation_score"]))
            if model.rmse > 1e-12:
                probability = NormalDist().cdf(predicted / model.rmse)
        confidence = "INSUFFICIENT"
        if model:
            confidence = "HIGH" if training_weeks >= 104 else "MEDIUM" if training_weeks >= 52 else "LOW"
        entry_signal, entry_reason = _entry_decision(
            kpi_cycle_score=row["kpi_cycle_score"],
            slope=row["kpi_slope_4w"],
            market_score=row["market_confirmation_score"],
            overheat_percentile=row["overheat_percentile"],
            expected_return=predicted,
        )
        result = {
            **row,
            "expected_excess_return_12w": predicted,
            "upside_probability_12w": probability,
            "prediction_confidence": confidence,
            "training_sample_count": len(observations),
            "training_week_count": training_weeks,
            "selected_ridge_lambda": model.ridge_lambda if model else None,
            "entry_signal": entry_signal,
            "entry_reason": entry_reason,
        }
        if persist:
            cycle_v2_repository.upsert_cycle_v2_signal(result, db_path=db_path)
        results.append(result)
    return results
