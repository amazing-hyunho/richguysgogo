from __future__ import annotations

"""Phase 4: top-level industry `cycle_score`/state-machine/confidence model config loader.

`config/industry_cycle_model.json` holds every weight/threshold used by
`committee.industry_cycle.cycle_scoring` and `cycle_state_machine`. Mirrors
the load-raw -> validate -> load(validated) pattern used by
`stock_model_config`/`fundamentals_model_config`/`price_model_config`. Pure
config loader: no DB or network access.
"""

import json
from pathlib import Path
from typing import Any, Dict, List

ROOT_DIR = Path(__file__).resolve().parents[2]
CYCLE_MODEL_CONFIG_PATH = ROOT_DIR / "config" / "industry_cycle_model.json"


class CycleModelConfigValidationError(ValueError):
    """Raised when the cycle model config fails structural validation."""


def load_cycle_model_config_raw(path: Path | None = None) -> Dict[str, Any]:
    """Load the raw `industry_cycle_model.json` config without validation."""
    p = path or CYCLE_MODEL_CONFIG_PATH
    if not p.exists():
        raise FileNotFoundError(f"industry_cycle_model config not found: {p}")
    return json.loads(p.read_text(encoding="utf-8"))


def _validate_score_group(name: str, group: Any) -> List[str]:
    errors: List[str] = []
    if not isinstance(group, dict):
        errors.append(f"{name} must be an object")
        return errors

    scale_k = group.get("scale_k")
    if not isinstance(scale_k, (int, float)) or scale_k <= 0:
        errors.append(f"{name}.scale_k must be a positive number")

    min_components = group.get("min_components")
    if not isinstance(min_components, int) or min_components <= 0:
        errors.append(f"{name}.min_components must be a positive int")

    components = group.get("components")
    if not isinstance(components, dict) or not components:
        errors.append(f"{name}.components must be a non-empty object")
    else:
        for key, weight in components.items():
            if not isinstance(weight, (int, float)) or weight < 0:
                errors.append(f"{name}.components['{key}'] must be a non-negative number")
        if isinstance(min_components, int) and min_components > len(components):
            errors.append(
                f"{name}.min_components ({min_components}) exceeds declared component count ({len(components)})"
            )

    baselines = group.get("baselines")
    if baselines is not None:
        if not isinstance(baselines, dict):
            errors.append(f"{name}.baselines must be an object when present")
        elif isinstance(components, dict):
            for key in baselines:
                if key not in components:
                    errors.append(f"{name}.baselines has unknown key '{key}' (not in components)")

    return errors


_STATE_THRESHOLD_KEYS = (
    "recovery_cycle_score_min",
    "recovery_cycle_score_max",
    "recovery_change_min",
    "expansion_cycle_score_min",
    "expansion_change_min",
    "overheat_cycle_score_min",
    "overheat_score_min",
    "deteriorating_change_max",
    "recession_cycle_score_max",
    "neutral_cycle_score_midpoint",
)

_CONFIRMATION_KEYS = (
    "weeks_required_recovery",
    "weeks_required_expansion",
    "weeks_required_overheat_warning",
    "weeks_required_deteriorating_confirmed",
)

_CONFIDENCE_KEYS = (
    "signal_strength_scale",
    "min_listing_days_full_history_reliability",
    "unknown_history_reliability_default",
    "model_agreement_conflict_penalty",
    "model_agreement_unknown_value",
    "min_confidence_for_action",
)

_URGENT_ALERT_KEYS = (
    "earnings_shock_score_drop_min",
    "price_crash_return_1m_max",
    "breadth_collapse_score_max",
    "confidence_drop_min",
)


def validate_cycle_model_config(payload: Dict[str, Any]) -> List[str]:
    """Return a list of validation error messages (empty list == valid).

    Pure/non-raising so callers (tests, CLI) can decide how to react.
    """
    errors: List[str] = []

    model_version = payload.get("model_version")
    if not model_version or not isinstance(model_version, str):
        errors.append("model_version is required and must be a non-empty string")

    cycle_score = payload.get("cycle_score")
    if cycle_score is None:
        errors.append("cycle_score group is required")
    else:
        errors.extend(_validate_score_group("cycle_score", cycle_score))

    thresholds = payload.get("state_thresholds")
    if not isinstance(thresholds, dict) or not thresholds:
        errors.append("state_thresholds must be a non-empty object")
    else:
        for key in _STATE_THRESHOLD_KEYS:
            if not isinstance(thresholds.get(key), (int, float)):
                errors.append(f"state_thresholds.{key} must be a number")

    confirmation = payload.get("confirmation")
    if not isinstance(confirmation, dict) or not confirmation:
        errors.append("confirmation must be a non-empty object")
    else:
        for key in _CONFIRMATION_KEYS:
            if not isinstance(confirmation.get(key), int) or confirmation.get(key) <= 0:
                errors.append(f"confirmation.{key} must be a positive int")

    confidence = payload.get("confidence")
    if not isinstance(confidence, dict) or not confidence:
        errors.append("confidence must be a non-empty object")
    else:
        for key in _CONFIDENCE_KEYS:
            if not isinstance(confidence.get(key), (int, float)):
                errors.append(f"confidence.{key} must be a number")
        for frac_key in ("unknown_history_reliability_default", "model_agreement_conflict_penalty",
                          "model_agreement_unknown_value", "min_confidence_for_action"):
            value = confidence.get(frac_key)
            if isinstance(value, (int, float)) and not (0.0 <= float(value) <= 1.0):
                errors.append(f"confidence.{frac_key} must be between 0 and 1")

    urgent_alert = payload.get("urgent_alert")
    if not isinstance(urgent_alert, dict) or not urgent_alert:
        errors.append("urgent_alert must be a non-empty object")
    else:
        for key in _URGENT_ALERT_KEYS:
            if not isinstance(urgent_alert.get(key), (int, float)):
                errors.append(f"urgent_alert.{key} must be a number")

    return errors


def load_cycle_model_config(path: Path | None = None) -> Dict[str, Any]:
    """Load and validate the cycle model config. Raises on failure."""
    payload = load_cycle_model_config_raw(path)
    errors = validate_cycle_model_config(payload)
    if errors:
        raise CycleModelConfigValidationError("; ".join(errors))
    return payload
