from __future__ import annotations

"""Phase 3: stock candidate exclusion rules (pure, no DB/network access).

Design doc section 8.2 "제외 조건" -- every listed exclusion condition maps
to one check below. Two conditions (거래정지·관리·상장폐지 위험,
국가별 유동성 하위 구간) need data this codebase does not currently source
anywhere (no trading-halt/administrative-designation feed, no cross-
sectional liquidity ranking table); rather than silently skip them, their
inputs are explicit optional fields on `ExclusionCheckInputs` that default
to `None` ("unknown") and are simply not evaluated when unknown -- callers
that DO have this data (e.g. a future `ticker_master` extension) can wire
it in without changing this module's contract. This is documented, not
hidden, in the Phase 3 completion report.

"추천 수를 채우기 위해 기준 미달 종목을 포함하지 않는다" (never backfill a
short candidate list with a sub-threshold stock) is enforced by the CALLER
(`candidate_ranking`) simply dropping any ticker with a non-empty exclusion
list, never by loosening thresholds here.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class ExclusionCheckInputs:
    """Every signal an exclusion rule might need, pre-computed by the caller.

    `None` means "unknown / not computable from current data" -- such a
    check is skipped (not treated as pass or fail), and is reported in
    `unknown_checks` for transparency (design doc: "모든 제외 사유가
    조회된다" -- exclusion reasons AND data gaps must both be inspectable).
    """

    capital_impaired: Optional[bool] = None
    sustained_loss_periods: int = 0
    fcf_margin: Optional[float] = None
    return_3m: Optional[float] = None
    ma200_gap: Optional[float] = None
    data_completeness: Optional[float] = None
    liquidity_percentile: Optional[float] = None  # 0=most illiquid in market .. 1=most liquid
    listing_days: Optional[int] = None  # trading days of price history on record
    trading_halted: Optional[bool] = None
    administrative_issue: Optional[bool] = None


@dataclass(frozen=True)
class ExclusionResult:
    excluded: bool
    reasons: List[str] = field(default_factory=list)
    unknown_checks: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "excluded": self.excluded,
            "reasons": self.reasons,
            "unknown_checks": self.unknown_checks,
        }


def evaluate_exclusions(inputs: ExclusionCheckInputs, stock_model_config: Dict[str, Any]) -> ExclusionResult:
    """Return every matching exclusion reason for one stock (never truncates at the first hit)."""
    excl_cfg: Dict[str, Any] = stock_model_config["exclusion"]
    reasons: List[str] = []
    unknown: List[str] = []

    if inputs.trading_halted is None:
        unknown.append("trading_halted_status_unknown")
    elif inputs.trading_halted:
        reasons.append("trading_halted_or_delisting_risk")

    if inputs.administrative_issue is None:
        unknown.append("administrative_designation_unknown")
    elif inputs.administrative_issue:
        reasons.append("administrative_issue_designation")

    if inputs.capital_impaired is None:
        unknown.append("capital_impairment_unknown")
    elif inputs.capital_impaired:
        reasons.append("capital_impairment")

    sustained_threshold = int(excl_cfg["sustained_loss_periods"])
    if inputs.sustained_loss_periods >= sustained_threshold:
        if inputs.fcf_margin is None:
            unknown.append("cashflow_status_unknown_for_sustained_loss_check")
        elif inputs.fcf_margin < 0:
            reasons.append(
                f"sustained_losses_with_negative_cashflow: {inputs.sustained_loss_periods} periods, "
                f"fcf_margin={inputs.fcf_margin:.3f}"
            )

    surge_threshold = float(excl_cfg["excessive_short_term_surge_pct_3m"])
    if inputs.return_3m is None:
        unknown.append("return_3m_unknown")
    elif inputs.return_3m > surge_threshold:
        reasons.append(f"excessive_short_term_surge: return_3m={inputs.return_3m:.3f} > {surge_threshold}")

    completeness_threshold = float(excl_cfg["min_data_completeness_for_score"])
    if inputs.data_completeness is None:
        unknown.append("data_completeness_unknown")
    elif inputs.data_completeness < completeness_threshold:
        reasons.append(
            f"insufficient_data_completeness: {inputs.data_completeness:.3f} < {completeness_threshold}"
        )

    liquidity_threshold = float(excl_cfg["min_liquidity_percentile"])
    if inputs.liquidity_percentile is None:
        unknown.append("liquidity_percentile_unknown")
    elif inputs.liquidity_percentile < liquidity_threshold:
        reasons.append(
            f"low_liquidity_percentile: {inputs.liquidity_percentile:.3f} < {liquidity_threshold}"
        )

    listing_threshold = int(excl_cfg["min_listing_days_stock"])
    if inputs.listing_days is None:
        unknown.append("listing_history_unknown")
    elif inputs.listing_days < listing_threshold:
        reasons.append(f"insufficient_listing_history: {inputs.listing_days} days < {listing_threshold}")

    return ExclusionResult(excluded=bool(reasons), reasons=reasons, unknown_checks=unknown)
