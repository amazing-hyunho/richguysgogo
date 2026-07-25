from __future__ import annotations

"""Phase 1-B: price-only scoring model config loader.

`config/industry_cycle_price_model.json` is the single source of truth for
every weight/threshold used by `committee.industry_cycle.price_scoring` and
`committee.industry_cycle.price_state_machine` (task constraint: "코드에
임계값을 하드코딩하지 말 것"). It also carries the `model_version` string
that every `industry_factor_weekly` / `industry_price_state_weekly` row
stores, so a later change to this file requires a new `model_version` to
keep old rows reproducible (design doc section 9: "모든 신호에는
model_version과 data_cutoff_at을 저장한다").

Mirrors the load-raw -> validate -> load(validated) pattern used by
`committee.industry_cycle.taxonomy` / `price_universe`. This module only
loads/validates the config file; it does not touch the DB or price data.
"""

import json
from pathlib import Path
from typing import Any, Dict, List

ROOT_DIR = Path(__file__).resolve().parents[2]
PRICE_MODEL_CONFIG_PATH = ROOT_DIR / "config" / "industry_cycle_price_model.json"

REQUIRED_SCORE_GROUPS = ("relative_strength", "trend", "overheat", "price_risk")

REQUIRED_STATE_THRESHOLD_KEYS = (
    "overheat_score_min",
    "risk_score_min_for_deteriorating",
    "deteriorating_trend_max",
    "expansion_relative_strength_min",
    "expansion_trend_min",
    "recovery_relative_strength_min",
    "recovery_relative_strength_max",
    "recovery_trend_min",
    "weak_relative_strength_max",
    "weak_trend_max",
    "neutral_relative_strength_midpoint",
)

REQUIRED_CONFIRMATION_KEYS = (
    "weeks_required_recovery",
    "weeks_required_overheat_warning",
    "weeks_required_deteriorating_confirmed",
)


class PriceModelConfigValidationError(ValueError):
    """Raised when the price model config fails structural validation."""


def load_price_model_config_raw(path: Path | None = None) -> Dict[str, Any]:
    """Load the raw `industry_cycle_price_model.json` config without validation."""
    p = path or PRICE_MODEL_CONFIG_PATH
    if not p.exists():
        raise FileNotFoundError(f"industry_cycle_price_model config not found: {p}")
    return json.loads(p.read_text(encoding="utf-8"))


def _validate_return_windows(payload: Dict[str, Any]) -> List[str]:
    errors: List[str] = []
    windows = payload.get("return_windows_trading_days")
    if not isinstance(windows, dict) or not windows:
        errors.append("return_windows_trading_days must be a non-empty object")
        return errors
    for label in ("1m", "3m", "6m", "12m"):
        if label not in windows:
            errors.append(f"return_windows_trading_days missing required window '{label}'")
        elif not isinstance(windows[label], int) or windows[label] <= 0:
            errors.append(f"return_windows_trading_days['{label}'] must be a positive int")
    return errors


def _validate_int_list(payload: Dict[str, Any], key: str) -> List[str]:
    errors: List[str] = []
    values = payload.get(key)
    if not isinstance(values, list) or not values:
        errors.append(f"{key} must be a non-empty list")
        return errors
    for v in values:
        if not isinstance(v, int) or v <= 0:
            errors.append(f"{key} entries must be positive ints (got {v!r})")
    return errors


def _validate_volume_change_windows(payload: Dict[str, Any]) -> List[str]:
    errors: List[str] = []
    vw = payload.get("volume_change_windows")
    if not isinstance(vw, dict):
        errors.append("volume_change_windows must be an object")
        return errors
    for key in ("recent", "prior"):
        if key not in vw or not isinstance(vw[key], int) or vw[key] <= 0:
            errors.append(f"volume_change_windows['{key}'] must be a positive int")
    return errors


def _validate_score_weights(payload: Dict[str, Any]) -> List[str]:
    errors: List[str] = []
    score_weights = payload.get("score_weights")
    if not isinstance(score_weights, dict):
        errors.append("score_weights must be an object")
        return errors
    for group in REQUIRED_SCORE_GROUPS:
        group_cfg = score_weights.get(group)
        if not isinstance(group_cfg, dict):
            errors.append(f"score_weights['{group}'] must be an object")
            continue
        components = group_cfg.get("components")
        if not isinstance(components, dict) or not components:
            errors.append(f"score_weights['{group}'].components must be a non-empty object")
            components = {}
        else:
            for comp_key, weight in components.items():
                if not isinstance(weight, (int, float)) or weight <= 0:
                    errors.append(
                        f"score_weights['{group}'].components['{comp_key}'] must be a positive number"
                    )
        baselines = group_cfg.get("baselines")
        if baselines is not None:
            if not isinstance(baselines, dict):
                errors.append(f"score_weights['{group}'].baselines must be an object when present")
            else:
                for comp_key, baseline in baselines.items():
                    if not isinstance(baseline, (int, float)):
                        errors.append(
                            f"score_weights['{group}'].baselines['{comp_key}'] must be numeric"
                        )

        scale_k = group_cfg.get("scale_k")
        if not isinstance(scale_k, (int, float)) or scale_k <= 0:
            errors.append(f"score_weights['{group}'].scale_k must be a positive number")
        min_components = group_cfg.get("min_components")
        if not isinstance(min_components, int) or min_components <= 0:
            errors.append(f"score_weights['{group}'].min_components must be a positive int")
        elif components and min_components > len(components):
            errors.append(
                f"score_weights['{group}'].min_components ({min_components}) "
                f"exceeds the number of declared components ({len(components)})"
            )
    return errors


def _validate_state_thresholds(payload: Dict[str, Any]) -> List[str]:
    errors: List[str] = []
    thresholds = payload.get("state_thresholds")
    if not isinstance(thresholds, dict):
        errors.append("state_thresholds must be an object")
        return errors
    for key in REQUIRED_STATE_THRESHOLD_KEYS:
        if key not in thresholds:
            errors.append(f"state_thresholds missing required key '{key}'")
        elif not isinstance(thresholds[key], (int, float)):
            errors.append(f"state_thresholds['{key}'] must be numeric")
    return errors


def _validate_confirmation(payload: Dict[str, Any]) -> List[str]:
    errors: List[str] = []
    confirmation = payload.get("confirmation")
    if not isinstance(confirmation, dict):
        errors.append("confirmation must be an object")
        return errors
    for key in REQUIRED_CONFIRMATION_KEYS:
        if key not in confirmation:
            errors.append(f"confirmation missing required key '{key}'")
        elif not isinstance(confirmation[key], int) or confirmation[key] <= 0:
            errors.append(f"confirmation['{key}'] must be a positive int")
    return errors


def validate_price_model_config(payload: Dict[str, Any]) -> List[str]:
    """Return a list of validation error messages (empty list == valid).

    Pure/non-raising so callers (tests, CLI) can decide how to react.
    """
    errors: List[str] = []

    model_version = payload.get("model_version")
    if not model_version or not isinstance(model_version, str):
        errors.append("model_version is required and must be a non-empty string")

    errors += _validate_return_windows(payload)
    errors += _validate_int_list(payload, "moving_average_windows")
    errors += _validate_int_list(payload, "volatility_windows")

    week_52 = payload.get("week_52_window_trading_days")
    if not isinstance(week_52, int) or week_52 <= 0:
        errors.append("week_52_window_trading_days must be a positive int")

    errors += _validate_volume_change_windows(payload)
    errors += _validate_score_weights(payload)
    errors += _validate_state_thresholds(payload)
    errors += _validate_confirmation(payload)

    min_completeness = payload.get("min_data_completeness_for_state")
    if not isinstance(min_completeness, (int, float)) or not (0.0 <= float(min_completeness) <= 1.0):
        errors.append("min_data_completeness_for_state must be a number between 0 and 1")

    return errors


def load_price_model_config(path: Path | None = None) -> Dict[str, Any]:
    """Load and validate the price model config. Raises on failure."""
    payload = load_price_model_config_raw(path)
    errors = validate_price_model_config(payload)
    if errors:
        raise PriceModelConfigValidationError("; ".join(errors))
    return payload
