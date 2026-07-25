from __future__ import annotations

"""Phase 2: fundamentals-score model config loader.

`config/industry_cycle_fundamentals_model.json` holds every weight/threshold
used by `committee.industry_cycle.fundamentals_scoring` that is NOT already
covered by `config/industry_indicators.json` (per-indicator `weight`/
`direction` live there, in `industry_indicator_map` -- see
`committee.industry_cycle.indicator_catalog`). Splitting it out like this
means:
- the scoring FUNCTION's knobs (`scale_k`, `min_components`, staleness
  policy) live here, versioned by this file's own `model_version`;
- which indicators feed which industry, and how, lives in
  `industry_indicators.json` / `industry_indicator_map`, versioned by that
  mapping's own `valid_from`/`valid_to`.

Mirrors the load-raw -> validate -> load(validated) pattern used by
`committee.industry_cycle.price_model_config`. Pure config loader: no DB or
network access.
"""

import json
from pathlib import Path
from typing import Any, Dict, List

ROOT_DIR = Path(__file__).resolve().parents[2]
FUNDAMENTALS_MODEL_CONFIG_PATH = ROOT_DIR / "config" / "industry_cycle_fundamentals_model.json"

VALID_FREQUENCIES = {"daily", "weekly", "monthly", "quarterly", "annual"}


class FundamentalsModelConfigValidationError(ValueError):
    """Raised when the fundamentals model config fails structural validation."""


def load_fundamentals_model_config_raw(path: Path | None = None) -> Dict[str, Any]:
    """Load the raw `industry_cycle_fundamentals_model.json` config without validation."""
    p = path or FUNDAMENTALS_MODEL_CONFIG_PATH
    if not p.exists():
        raise FileNotFoundError(f"industry_cycle_fundamentals_model config not found: {p}")
    return json.loads(p.read_text(encoding="utf-8"))


def validate_fundamentals_model_config(payload: Dict[str, Any]) -> List[str]:
    """Return a list of validation error messages (empty list == valid).

    Pure/non-raising so callers (tests, CLI) can decide how to react.
    """
    errors: List[str] = []

    model_version = payload.get("model_version")
    if not model_version or not isinstance(model_version, str):
        errors.append("model_version is required and must be a non-empty string")

    scale_k = payload.get("scale_k")
    if not isinstance(scale_k, (int, float)) or scale_k <= 0:
        errors.append("scale_k must be a positive number")

    min_components = payload.get("min_components")
    if not isinstance(min_components, int) or min_components <= 0:
        errors.append("min_components must be a positive int")

    staleness = payload.get("staleness_max_periods_by_frequency")
    if not isinstance(staleness, dict) or not staleness:
        errors.append("staleness_max_periods_by_frequency must be a non-empty object")
    else:
        for freq, max_periods in staleness.items():
            if freq.startswith("_"):
                continue
            if freq not in VALID_FREQUENCIES:
                errors.append(
                    f"staleness_max_periods_by_frequency has unknown frequency '{freq}' "
                    f"(expected one of {sorted(VALID_FREQUENCIES)})"
                )
            if not isinstance(max_periods, int) or max_periods <= 0:
                errors.append(
                    f"staleness_max_periods_by_frequency['{freq}'] must be a positive int"
                )

    min_completeness = payload.get("min_data_completeness_for_score")
    if not isinstance(min_completeness, (int, float)) or not (0.0 <= float(min_completeness) <= 1.0):
        errors.append("min_data_completeness_for_score must be a number between 0 and 1")

    min_evidence = payload.get("min_non_price_evidence_count_for_recovery_candidate")
    if not isinstance(min_evidence, int) or min_evidence < 0:
        errors.append("min_non_price_evidence_count_for_recovery_candidate must be a non-negative int")

    return errors


def load_fundamentals_model_config(path: Path | None = None) -> Dict[str, Any]:
    """Load and validate the fundamentals model config. Raises on failure."""
    payload = load_fundamentals_model_config_raw(path)
    errors = validate_fundamentals_model_config(payload)
    if errors:
        raise FundamentalsModelConfigValidationError("; ".join(errors))
    return payload
