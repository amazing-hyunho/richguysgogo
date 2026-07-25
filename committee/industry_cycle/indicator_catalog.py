from __future__ import annotations

"""Phase 0: indicator catalog + industry-indicator mapping config loader.

`config/industry_indicators.json` holds two related but separate things
(design doc section 9):
- `indicators`: indicator_catalog definitions (provider, source series id,
  unit, frequency, transform). No industry association here.
- `industry_indicator_mappings`: which indicators feed which industry's
  `fundamentals_score`, with a `direction` (does a higher indicator value
  raise or lower the industry's outlook), a `weight`, and a validity window
  so classification changes over time don't erase history. This mirrors the
  `aliases` pattern in `industry_taxonomy.json` and is synced into the
  `industry_indicator_map` table via
  `committee.industry_cycle.repository.sync_industry_indicator_map_from_config`.

This module only loads/validates the config file; it does not touch the DB
(see `committee.industry_cycle.taxonomy` for the equivalent pattern used by
`industry_taxonomy.json`).
"""

import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Set, Tuple

ROOT_DIR = Path(__file__).resolve().parents[2]
INDICATOR_CONFIG_PATH = ROOT_DIR / "config" / "industry_indicators.json"

VALID_INDICATOR_DIRECTIONS = {"positive", "negative"}


class IndicatorConfigValidationError(ValueError):
    """Raised when the indicator catalog/mapping config fails structural validation."""


def load_indicator_config_raw(path: Path | None = None) -> Dict[str, Any]:
    """Load the raw `industry_indicators.json` config without validation."""
    p = path or INDICATOR_CONFIG_PATH
    if not p.exists():
        raise FileNotFoundError(f"industry_indicators config not found: {p}")
    return json.loads(p.read_text(encoding="utf-8"))


def validate_indicator_catalog(payload: Dict[str, Any]) -> List[str]:
    """Validate the `indicators` catalog list.

    Checks: must be a list; each entry needs a unique string `indicator_id`.
    Pure/non-raising so callers can decide how to react.
    """
    errors: List[str] = []
    indicators = payload.get("indicators")
    if not isinstance(indicators, list):
        errors.append("indicators must be a list")
        return errors

    seen_ids: Set[str] = set()
    for idx, entry in enumerate(indicators):
        prefix = f"indicators[{idx}]"
        if not isinstance(entry, dict):
            errors.append(f"{prefix}: must be an object")
            continue

        indicator_id = entry.get("indicator_id")
        if not indicator_id or not isinstance(indicator_id, str):
            errors.append(f"{prefix}: indicator_id is required and must be a string")
        elif indicator_id in seen_ids:
            errors.append(f"{prefix}: duplicate indicator_id '{indicator_id}'")
        else:
            seen_ids.add(indicator_id)

        baseline = entry.get("baseline")
        if baseline is not None and not isinstance(baseline, (int, float)):
            errors.append(f"{prefix}: baseline must be numeric")

    return errors


def validate_industry_indicator_mappings(
    payload: Dict[str, Any],
    *,
    known_industry_ids: Iterable[str] | None = None,
    known_indicator_ids: Iterable[str] | None = None,
) -> List[str]:
    """Validate the `industry_indicator_mappings` list.

    `known_industry_ids` / `known_indicator_ids` are optional cross-reference
    sets (e.g. from `industry_taxonomy.json` / this config's own `indicators`
    list) — when given, mappings referencing unknown ids are flagged. Also
    checks `direction` is one of `VALID_INDICATOR_DIRECTIONS`, `weight` is
    numeric when present, and there are no duplicate
    `(industry_id, indicator_id, valid_from)` triples (mirrors the alias
    duplicate check in `industry_taxonomy.json`).
    """
    errors: List[str] = []
    mappings = payload.get("industry_indicator_mappings", [])
    if not isinstance(mappings, list):
        errors.append("industry_indicator_mappings must be a list")
        return errors

    industry_ids = set(known_industry_ids) if known_industry_ids is not None else None
    indicator_ids = set(known_indicator_ids) if known_indicator_ids is not None else None
    seen_keys: Set[Tuple[Any, Any, Any]] = set()

    for idx, entry in enumerate(mappings):
        prefix = f"industry_indicator_mappings[{idx}]"
        if not isinstance(entry, dict):
            errors.append(f"{prefix}: must be an object")
            continue

        industry_id = entry.get("industry_id")
        indicator_id = entry.get("indicator_id")

        if not industry_id or not isinstance(industry_id, str):
            errors.append(f"{prefix}: industry_id is required and must be a string")
        elif industry_ids is not None and industry_id not in industry_ids:
            errors.append(f"{prefix}: unknown industry_id '{industry_id}'")

        if not indicator_id or not isinstance(indicator_id, str):
            errors.append(f"{prefix}: indicator_id is required and must be a string")
        elif indicator_ids is not None and indicator_id not in indicator_ids:
            errors.append(f"{prefix}: unknown indicator_id '{indicator_id}'")

        direction = entry.get("direction")
        if direction is not None and direction not in VALID_INDICATOR_DIRECTIONS:
            errors.append(
                f"{prefix}: direction must be one of {sorted(VALID_INDICATOR_DIRECTIONS)}"
            )

        weight = entry.get("weight")
        if weight is not None and not isinstance(weight, (int, float)):
            errors.append(f"{prefix}: weight must be numeric")

        if industry_id and indicator_id:
            key = (industry_id, indicator_id, entry.get("valid_from"))
            if key in seen_keys:
                errors.append(
                    f"{prefix}: duplicate mapping for industry_id={industry_id}, "
                    f"indicator_id={indicator_id}, valid_from={entry.get('valid_from')!r}"
                )
            else:
                seen_keys.add(key)

    return errors


def load_indicator_config(path: Path | None = None) -> Dict[str, Any]:
    """Load and validate `industry_indicators.json`. Raises `IndicatorConfigValidationError`.

    Mappings are cross-referenced against this same config's own `indicators`
    catalog (always available). Cross-referencing against
    `industry_taxonomy.json`'s industry ids is intentionally left to callers
    that have both configs loaded (e.g. a sync CLI), to avoid a hard import
    dependency between the two config loaders.
    """
    payload = load_indicator_config_raw(path)

    catalog_errors = validate_indicator_catalog(payload)
    if catalog_errors:
        raise IndicatorConfigValidationError("; ".join(catalog_errors))

    catalog_ids = {
        str(entry["indicator_id"])
        for entry in payload.get("indicators", [])
        if isinstance(entry, dict) and entry.get("indicator_id")
    }
    mapping_errors = validate_industry_indicator_mappings(
        payload, known_indicator_ids=catalog_ids
    )
    if mapping_errors:
        raise IndicatorConfigValidationError("; ".join(mapping_errors))

    return payload


def list_indicator_ids(path: Path | None = None) -> List[str]:
    """Return all `indicator_id`s declared in the indicator catalog config."""
    payload = load_indicator_config(path)
    return [str(entry["indicator_id"]) for entry in payload["indicators"]]
