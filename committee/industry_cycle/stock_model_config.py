from __future__ import annotations

"""Phase 3: stock/ETF candidate model config loader.

`config/industry_cycle_stock_model.json` holds every weight/threshold used
by `committee.industry_cycle.stock_scoring`, `industry_breadth_scoring`, and
`etf_quality`. Mirrors the load-raw -> validate -> load(validated) pattern
used by `price_model_config`/`fundamentals_model_config`. Pure config
loader: no DB or network access.
"""

import json
from pathlib import Path
from typing import Any, Dict, List

ROOT_DIR = Path(__file__).resolve().parents[2]
STOCK_MODEL_CONFIG_PATH = ROOT_DIR / "config" / "industry_cycle_stock_model.json"

_SCORE_GROUP_KEYS = (
    "earnings_quality",
    "estimate_revision",
    "relative_strength",
    "financial_health",
    "liquidity",
    "stock_score",
    "industry_earnings_revision",
    "industry_breadth",
)


class StockModelConfigValidationError(ValueError):
    """Raised when the stock model config fails structural validation."""


def load_stock_model_config_raw(path: Path | None = None) -> Dict[str, Any]:
    """Load the raw `industry_cycle_stock_model.json` config without validation."""
    p = path or STOCK_MODEL_CONFIG_PATH
    if not p.exists():
        raise FileNotFoundError(f"industry_cycle_stock_model config not found: {p}")
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


def validate_stock_model_config(payload: Dict[str, Any]) -> List[str]:
    """Return a list of validation error messages (empty list == valid).

    Pure/non-raising so callers (tests, CLI) can decide how to react.
    """
    errors: List[str] = []

    model_version = payload.get("model_version")
    if not model_version or not isinstance(model_version, str):
        errors.append("model_version is required and must be a non-empty string")

    for group_name in _SCORE_GROUP_KEYS:
        group = payload.get(group_name)
        if group is None:
            errors.append(f"{group_name} group is required")
            continue
        errors.extend(_validate_score_group(group_name, group))

    risk_penalty = payload.get("risk_penalty")
    if not isinstance(risk_penalty, dict) or not risk_penalty:
        errors.append("risk_penalty must be a non-empty object")
    else:
        for key in (
            "high_debt_ratio_threshold",
            "high_debt_ratio_points",
            "sustained_loss_points",
            "excessive_short_term_surge_points",
            "max_total_points",
        ):
            if key not in risk_penalty or not isinstance(risk_penalty[key], (int, float)):
                errors.append(f"risk_penalty.{key} must be a number")

    exclusion = payload.get("exclusion")
    if not isinstance(exclusion, dict) or not exclusion:
        errors.append("exclusion must be a non-empty object")
    else:
        completeness = exclusion.get("min_data_completeness_for_score")
        if not isinstance(completeness, (int, float)) or not (0.0 <= float(completeness) <= 1.0):
            errors.append("exclusion.min_data_completeness_for_score must be a number between 0 and 1")
        for key in (
            "sustained_loss_periods",
            "min_history_periods_financial",
            "min_history_snapshots_consensus",
            "min_listing_days_stock",
        ):
            if not isinstance(exclusion.get(key), int) or exclusion.get(key) < 0:
                errors.append(f"exclusion.{key} must be a non-negative int")
        surge = exclusion.get("excessive_short_term_surge_pct_3m")
        if not isinstance(surge, (int, float)) or surge <= 0:
            errors.append("exclusion.excessive_short_term_surge_pct_3m must be a positive number")
        liquidity_pct = exclusion.get("min_liquidity_percentile")
        if not isinstance(liquidity_pct, (int, float)) or not (0.0 <= float(liquidity_pct) <= 1.0):
            errors.append("exclusion.min_liquidity_percentile must be a number between 0 and 1")

    etf_quality = payload.get("etf_quality")
    if not isinstance(etf_quality, dict) or not etf_quality:
        errors.append("etf_quality must be a non-empty object")
    else:
        for key in ("min_aum_usd_equivalent", "max_expense_ratio", "max_spread_bp", "min_listing_days"):
            if key not in etf_quality or not isinstance(etf_quality[key], (int, float)) or etf_quality[key] < 0:
                errors.append(f"etf_quality.{key} must be a non-negative number")
        if not isinstance(etf_quality.get("exclude_leveraged_inverse"), bool):
            errors.append("etf_quality.exclude_leveraged_inverse must be a boolean")
        purity = etf_quality.get("min_industry_purity_pct")
        if not isinstance(purity, (int, float)) or not (0.0 <= float(purity) <= 1.0):
            errors.append("etf_quality.min_industry_purity_pct must be a number between 0 and 1")

    lookback = payload.get("consensus_revision_lookback_days")
    if not isinstance(lookback, int) or lookback <= 0:
        errors.append("consensus_revision_lookback_days must be a positive int")

    return errors


def load_stock_model_config(path: Path | None = None) -> Dict[str, Any]:
    """Load and validate the stock model config. Raises on failure."""
    payload = load_stock_model_config_raw(path)
    errors = validate_stock_model_config(payload)
    if errors:
        raise StockModelConfigValidationError("; ".join(errors))
    return payload
