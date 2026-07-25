from __future__ import annotations

"""Phase 1-A price universe config loader.

`config/industry_price_universe.json` declares the small set of benchmark
indices and industry ETFs that the Phase 1-A price backfill CLI operates on
(design doc section 12, Phase 1 item 1 / section 15 recommendation 4).

Mirrors the loader pattern used by `committee.industry_cycle.taxonomy` and
`committee.industry_cycle.indicator_catalog`: load raw -> validate -> load
(validated). This module only loads/validates the config file; it does not
touch the DB or any provider.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Set

from committee.industry_cycle.price_models import VALID_CURRENCIES, VALID_MARKETS

ROOT_DIR = Path(__file__).resolve().parents[2]
PRICE_UNIVERSE_PATH = ROOT_DIR / "config" / "industry_price_universe.json"


class PriceUniverseValidationError(ValueError):
    """Raised when the price universe config fails structural validation."""


def load_price_universe_raw(path: Path | None = None) -> Dict[str, Any]:
    """Load the raw `industry_price_universe.json` config without validation."""
    p = path or PRICE_UNIVERSE_PATH
    if not p.exists():
        raise FileNotFoundError(f"industry_price_universe config not found: {p}")
    return json.loads(p.read_text(encoding="utf-8"))


def _validate_entries(entries: Any, *, list_name: str, require_industry_id: bool) -> List[str]:
    errors: List[str] = []
    if not isinstance(entries, list):
        errors.append(f"{list_name} must be a list")
        return errors

    seen_ids: Set[str] = set()
    for idx, entry in enumerate(entries):
        prefix = f"{list_name}[{idx}]"
        if not isinstance(entry, dict):
            errors.append(f"{prefix}: must be an object")
            continue

        asset_id = entry.get("asset_id")
        if not asset_id or not isinstance(asset_id, str):
            errors.append(f"{prefix}: asset_id is required and must be a string")
        elif asset_id in seen_ids:
            errors.append(f"{prefix}: duplicate asset_id '{asset_id}'")
        else:
            seen_ids.add(asset_id)

        market = entry.get("market")
        if market not in VALID_MARKETS:
            errors.append(f"{prefix}: market must be one of {sorted(VALID_MARKETS)}")

        currency = entry.get("currency")
        if currency not in VALID_CURRENCIES:
            errors.append(f"{prefix}: currency must be one of {sorted(VALID_CURRENCIES)}")

        if not entry.get("provider"):
            errors.append(f"{prefix}: provider is required")
        if not entry.get("symbol"):
            errors.append(f"{prefix}: symbol is required")

        if require_industry_id and not entry.get("industry_id"):
            errors.append(f"{prefix}: industry_id is required for entries in '{list_name}'")

    return errors


def validate_price_universe(payload: Dict[str, Any]) -> List[str]:
    """Return a list of validation error messages (empty list == valid).

    Pure/non-raising so callers (tests, CLI) can decide how to react.
    Also checks `asset_id` is unique across `benchmarks` and `assets`
    combined, since both are stored in the same `asset_price_daily` table.
    """
    benchmarks = payload.get("benchmarks", [])
    assets = payload.get("assets", [])

    errors = _validate_entries(benchmarks, list_name="benchmarks", require_industry_id=False)
    errors += _validate_entries(assets, list_name="assets", require_industry_id=True)

    all_ids = [e.get("asset_id") for e in (benchmarks + assets) if isinstance(e, dict) and e.get("asset_id")]
    seen: Set[str] = set()
    for asset_id in all_ids:
        if asset_id in seen:
            errors.append(f"duplicate asset_id across benchmarks/assets: '{asset_id}'")
        seen.add(asset_id)

    return errors


def load_price_universe(path: Path | None = None) -> Dict[str, Any]:
    """Load and validate the price universe config. Raises on failure."""
    payload = load_price_universe_raw(path)
    errors = validate_price_universe(payload)
    if errors:
        raise PriceUniverseValidationError("; ".join(errors))
    return payload


def list_asset_ids(path: Path | None = None) -> List[str]:
    """Return all asset_ids declared across `benchmarks` and `assets`."""
    payload = load_price_universe(path)
    return [
        str(e["asset_id"])
        for e in (payload.get("benchmarks", []) + payload.get("assets", []))
    ]


def get_benchmark_asset_id(market: str, universe: Dict[str, Any]) -> str | None:
    """Return the `benchmarks` entry's `asset_id` for `market` (e.g. KOSPI for KR, SP500 for US).

    Used by Phase 1-B (`price_factor_runner`, `price_backtest` callers) so
    the KR/US benchmark choice comes from `industry_price_universe.json`
    data rather than being hardcoded in code (design doc section 2: 한국은
    KOSPI, 미국은 S&P 500). Returns `None` if no benchmark is declared for
    that market.
    """
    for entry in universe.get("benchmarks", []):
        if entry.get("market") == market:
            return str(entry["asset_id"])
    return None
