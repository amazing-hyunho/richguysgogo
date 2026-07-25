from __future__ import annotations

"""Phase 3: ETF quality filter (design doc section 8.1 "ETF 필터").

산업 신호와 ETF 품질을 분리한다: an industry's cycle signal is computed
independently of whether any given ETF representing it is actually
investable, and vice versa. This module only answers "is this ETF good
enough to recommend", never anything about the industry's outlook.

`config/industry_etf_quality.json` holds hand-curated static attributes
(AUM, expense ratio, leverage flag, listing date, industry purity) --
these change slowly and several (expense ratio, AUM) are not reliably
available for free on every ETF/every market, so they are refreshed
manually rather than re-fetched on each scoring run. `listing_days` is
the one attribute this module computes dynamically, from
`asset_price_daily`'s own history (Phase 1-A's price table; asset-type
agnostic), rather than from the static config.
"""

import json
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any, Dict, List, Optional

from committee.industry_cycle import price_repository

ROOT_DIR = Path(__file__).resolve().parents[2]
ETF_QUALITY_CONFIG_PATH = ROOT_DIR / "config" / "industry_etf_quality.json"


class EtfQualityConfigValidationError(ValueError):
    """Raised when `industry_etf_quality.json` fails structural validation."""


def load_etf_quality_catalog_raw(path: Path | None = None) -> Dict[str, Any]:
    p = path or ETF_QUALITY_CONFIG_PATH
    if not p.exists():
        raise FileNotFoundError(f"industry_etf_quality config not found: {p}")
    return json.loads(p.read_text(encoding="utf-8"))


def validate_etf_quality_catalog(payload: Dict[str, Any]) -> List[str]:
    errors: List[str] = []
    entries = payload.get("etfs")
    if not isinstance(entries, list):
        errors.append("etfs must be a list")
        return errors
    seen = set()
    for idx, entry in enumerate(entries):
        prefix = f"etfs[{idx}]"
        if not isinstance(entry, dict):
            errors.append(f"{prefix}: must be an object")
            continue
        asset_id = entry.get("asset_id")
        if not asset_id or not isinstance(asset_id, str):
            errors.append(f"{prefix}: asset_id is required and must be a string")
        elif asset_id in seen:
            errors.append(f"{prefix}: duplicate asset_id '{asset_id}'")
        else:
            seen.add(asset_id)
        for numeric_key in ("aum_usd_equivalent", "expense_ratio", "bid_ask_spread_bp", "industry_purity_pct"):
            v = entry.get(numeric_key)
            if v is not None and not isinstance(v, (int, float)):
                errors.append(f"{prefix}.{numeric_key} must be numeric or null")
        if entry.get("is_leveraged_or_inverse") is not None and not isinstance(entry.get("is_leveraged_or_inverse"), bool):
            errors.append(f"{prefix}.is_leveraged_or_inverse must be a boolean or null")
    return errors


def load_etf_quality_catalog(path: Path | None = None) -> Dict[str, Any]:
    payload = load_etf_quality_catalog_raw(path)
    errors = validate_etf_quality_catalog(payload)
    if errors:
        raise EtfQualityConfigValidationError("; ".join(errors))
    return payload


def get_etf_attrs(asset_id: str, catalog: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    for entry in catalog.get("etfs", []):
        if entry.get("asset_id") == asset_id:
            return entry
    return None


def compute_listing_days(asset_id: str, as_of: str, *, db_path: Path | None = None) -> Optional[int]:
    """Trading days of `asset_price_daily` history on record for `asset_id` as of `as_of`."""
    rows = price_repository.get_prices_as_of(asset_id, as_of, db_path=db_path)
    return len(rows) if rows else None


@dataclass(frozen=True)
class ETFQualityCheckInputs:
    asset_id: str
    aum_usd_equivalent: Optional[float] = None
    expense_ratio: Optional[float] = None
    bid_ask_spread_bp: Optional[float] = None
    is_leveraged_or_inverse: Optional[bool] = None
    listing_days: Optional[int] = None
    industry_purity_pct: Optional[float] = None


@dataclass(frozen=True)
class ETFQualityResult:
    asset_id: str
    passed: bool
    reasons: List[str] = field(default_factory=list)
    unknown_checks: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "asset_id": self.asset_id,
            "passed": self.passed,
            "reasons": self.reasons,
            "unknown_checks": self.unknown_checks,
        }


def evaluate_etf_quality(inputs: ETFQualityCheckInputs, stock_model_config: Dict[str, Any]) -> ETFQualityResult:
    cfg = stock_model_config["etf_quality"]
    reasons: List[str] = []
    unknown: List[str] = []

    if inputs.aum_usd_equivalent is None:
        unknown.append("aum_unknown")
    elif inputs.aum_usd_equivalent < float(cfg["min_aum_usd_equivalent"]):
        reasons.append(f"aum_below_minimum: {inputs.aum_usd_equivalent} < {cfg['min_aum_usd_equivalent']}")

    if inputs.expense_ratio is None:
        unknown.append("expense_ratio_unknown")
    elif inputs.expense_ratio > float(cfg["max_expense_ratio"]):
        reasons.append(f"expense_ratio_above_maximum: {inputs.expense_ratio} > {cfg['max_expense_ratio']}")

    if inputs.bid_ask_spread_bp is None:
        unknown.append("bid_ask_spread_unknown")
    elif inputs.bid_ask_spread_bp > float(cfg["max_spread_bp"]):
        reasons.append(f"spread_above_maximum: {inputs.bid_ask_spread_bp}bp > {cfg['max_spread_bp']}bp")

    if inputs.is_leveraged_or_inverse is None:
        unknown.append("leverage_flag_unknown")
    elif inputs.is_leveraged_or_inverse and bool(cfg["exclude_leveraged_inverse"]):
        reasons.append("leveraged_or_inverse_etf_excluded")

    if inputs.listing_days is None:
        unknown.append("listing_days_unknown")
    elif inputs.listing_days < int(cfg["min_listing_days"]):
        reasons.append(f"insufficient_listing_history: {inputs.listing_days} days < {cfg['min_listing_days']}")

    if inputs.industry_purity_pct is None:
        unknown.append("industry_purity_unknown")
    elif inputs.industry_purity_pct < float(cfg["min_industry_purity_pct"]):
        reasons.append(
            f"industry_purity_below_minimum: {inputs.industry_purity_pct} < {cfg['min_industry_purity_pct']}"
        )

    return ETFQualityResult(asset_id=inputs.asset_id, passed=not reasons, reasons=reasons, unknown_checks=unknown)


def evaluate_etf_from_catalog(
    asset_id: str,
    as_of: str,
    *,
    catalog: Dict[str, Any],
    stock_model_config: Dict[str, Any],
    db_path: Path | None = None,
) -> ETFQualityResult:
    """Convenience wrapper: load an ETF's static attrs from `catalog` + dynamic listing_days, then evaluate."""
    attrs = get_etf_attrs(asset_id, catalog)
    if attrs is None:
        return ETFQualityResult(
            asset_id=asset_id, passed=False, reasons=["etf_not_in_quality_catalog"], unknown_checks=[]
        )
    inputs = ETFQualityCheckInputs(
        asset_id=asset_id,
        aum_usd_equivalent=attrs.get("aum_usd_equivalent"),
        expense_ratio=attrs.get("expense_ratio"),
        bid_ask_spread_bp=attrs.get("bid_ask_spread_bp"),
        is_leveraged_or_inverse=attrs.get("is_leveraged_or_inverse"),
        listing_days=compute_listing_days(asset_id, as_of, db_path=db_path),
        industry_purity_pct=attrs.get("industry_purity_pct"),
    )
    return evaluate_etf_quality(inputs, stock_model_config)
