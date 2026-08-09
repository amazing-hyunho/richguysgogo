from __future__ import annotations

"""Configuration loader for the objective, two-axis industry-cycle model."""

import json
from pathlib import Path
from typing import Any


ROOT_DIR = Path(__file__).resolve().parents[2]
CYCLE_V2_MODEL_CONFIG_PATH = ROOT_DIR / "config" / "industry_cycle_v2_model.json"


def load_cycle_v2_model_config(path: Path | None = None) -> dict[str, Any]:
    config_path = path or CYCLE_V2_MODEL_CONFIG_PATH
    payload = json.loads(config_path.read_text(encoding="utf-8"))
    if not str(payload.get("model_version") or "").strip():
        raise ValueError("cycle_v2 model_version is required")
    if int(payload.get("fundamentals_history_min_weeks") or 0) < 2:
        raise ValueError("fundamentals_history_min_weeks must be at least 2")
    if int(payload.get("slope_lookback_weeks") or 0) < 1:
        raise ValueError("slope_lookback_weeks must be positive")
    forecast = payload.get("forecast")
    if not isinstance(forecast, dict):
        raise ValueError("forecast config is required")
    if int(forecast.get("horizon_calendar_days") or 0) < 7:
        raise ValueError("forecast.horizon_calendar_days must be at least 7")
    if int(forecast.get("min_training_samples") or 0) < 10:
        raise ValueError("forecast.min_training_samples must be at least 10")
    lambdas = forecast.get("ridge_lambdas")
    if not isinstance(lambdas, list) or not lambdas or any(float(v) < 0 for v in lambdas):
        raise ValueError("forecast.ridge_lambdas must be a non-empty list of non-negative numbers")
    fraction = float(forecast.get("validation_fraction") or 0)
    if not 0 < fraction < 0.5:
        raise ValueError("forecast.validation_fraction must be between 0 and 0.5")
    return payload
