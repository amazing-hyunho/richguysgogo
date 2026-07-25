from __future__ import annotations

"""Phase 0: internal industry taxonomy config loader.

`config/industry_taxonomy.json` is the single source of truth for the
internal `industry_id` standard described in the design doc (section 6.1).
External classification codes are never used as the primary key; they are
attached as `aliases` and later synced into the `industry_alias` table via
`committee.industry_cycle.repository.sync_industry_master_from_config`.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Set

ROOT_DIR = Path(__file__).resolve().parents[2]
TAXONOMY_PATH = ROOT_DIR / "config" / "industry_taxonomy.json"

VALID_COVERAGE_STATUS = {"OK", "INSUFFICIENT"}
VALID_COUNTRY_CODES = {"KR", "US"}


class TaxonomyValidationError(ValueError):
    """Raised when the taxonomy config fails structural validation."""


def load_taxonomy_raw(path: Path | None = None) -> Dict[str, Any]:
    """Load the raw taxonomy JSON without validation."""
    p = path or TAXONOMY_PATH
    if not p.exists():
        raise FileNotFoundError(f"industry_taxonomy config not found: {p}")
    return json.loads(p.read_text(encoding="utf-8"))


def validate_taxonomy(payload: Dict[str, Any]) -> List[str]:
    """Return a list of validation error messages (empty list == valid).

    Pure/non-raising so callers (tests, CLI, repository sync) can decide how
    to react to problems.
    """
    errors: List[str] = []
    industries = payload.get("industries")
    if not isinstance(industries, list) or not industries:
        errors.append("industries must be a non-empty list")
        return errors

    seen_ids: Set[str] = set()
    for idx, entry in enumerate(industries):
        prefix = f"industries[{idx}]"
        if not isinstance(entry, dict):
            errors.append(f"{prefix}: must be an object")
            continue

        industry_id = entry.get("industry_id")
        if not industry_id or not isinstance(industry_id, str):
            errors.append(f"{prefix}: industry_id is required and must be a string")
        elif industry_id in seen_ids:
            errors.append(f"{prefix}: duplicate industry_id '{industry_id}'")
        else:
            seen_ids.add(industry_id)

        if not entry.get("name_kr"):
            errors.append(f"{prefix}: name_kr is required")

        country_scope = entry.get("country_scope")
        if not isinstance(country_scope, list) or not country_scope:
            errors.append(f"{prefix}: country_scope must be a non-empty list")
        else:
            for code in country_scope:
                if code not in VALID_COUNTRY_CODES:
                    errors.append(f"{prefix}: unsupported country_scope value '{code}'")

        coverage_status = entry.get("coverage_status")
        if coverage_status is not None and coverage_status not in VALID_COVERAGE_STATUS:
            errors.append(
                f"{prefix}: coverage_status must be one of {sorted(VALID_COVERAGE_STATUS)}"
            )

        for alias_idx, alias in enumerate(entry.get("aliases", []) or []):
            alias_prefix = f"{prefix}.aliases[{alias_idx}]"
            if not isinstance(alias, dict):
                errors.append(f"{alias_prefix}: must be an object")
                continue
            if not alias.get("provider"):
                errors.append(f"{alias_prefix}: provider is required")
            if not alias.get("external_code"):
                errors.append(f"{alias_prefix}: external_code is required")

    return errors


def load_taxonomy(path: Path | None = None) -> Dict[str, Any]:
    """Load and validate the taxonomy config. Raises `TaxonomyValidationError`."""
    payload = load_taxonomy_raw(path)
    errors = validate_taxonomy(payload)
    if errors:
        raise TaxonomyValidationError("; ".join(errors))
    return payload


def list_industry_ids(path: Path | None = None) -> List[str]:
    """Return all `industry_id`s declared in the taxonomy config."""
    payload = load_taxonomy(path)
    return [str(entry["industry_id"]) for entry in payload["industries"]]
