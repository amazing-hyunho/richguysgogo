from __future__ import annotations

"""Phase 1-B: PRICE-ONLY provisional regime classification (pure logic).

IMPORTANT -- this is explicitly NOT the final industry cycle judgment from
docs/industry_cycle_mvp_design.md section 7.3 (회복 초입/확장/과열/둔화/침체).
That final call requires fundamentals/earnings-revision/flow/macro/breadth
inputs that only arrive in Phase 2+ (`industry_cycle_signal`). Every state
value produced here is prefixed `PRICE_ONLY_` for exactly that reason: if
this string leaks into a dashboard, log, or downstream table by mistake, it
is self-evidently a provisional, price-data-only signal, not a committee
decision. See also `committee.industry_cycle.factor_repository` and the
`industry_price_state_weekly` table docstring in `committee/core/database.py`.

Two separate steps:
1. `classify_raw_state`: this week's state from this week's scores alone
   (plus last week's `relative_strength_score`, needed only to tell whether
   relative strength is currently rising -- the design doc's recovery
   condition, section 7.3: "낮은 수준에서 점수 상승").
2. `apply_confirmation_rule`: turns a run of consecutive identical raw
   states into a confirmation/warning per the task's 2-week rules (section
   7.3 / task item 5):
   - `PRICE_ONLY_RECOVERY_CANDIDATE` for 2 consecutive weeks -> confirmed
   - `PRICE_ONLY_OVERHEATED` observed first week, warning on the 2nd
     consecutive week
   - `PRICE_ONLY_DETERIORATING` for 2 consecutive weeks -> confirmed
   - `PRICE_ONLY_INSUFFICIENT_DATA` never confirms/carries forward the
     previous state -- it always resolves to `confirmation_status="held"`
     (task: "데이터 부족 시 이전 상태를 무조건 유지하지 말고 판정 보류"),
     and because the row we persist for that week IS `INSUFFICIENT_DATA`,
     the next week's streak comparison naturally restarts at 1 rather than
     silently continuing an old streak through the data gap.

Every threshold/weeks-required value comes from
`config/industry_cycle_price_model.json` (`state_thresholds`,
`confirmation`) -- never hardcoded here (task constraint).
"""

from dataclasses import dataclass
from typing import Any, Dict, Optional

from committee.industry_cycle.price_scoring import PriceScoreBundle

PRICE_ONLY_RECOVERY_CANDIDATE = "PRICE_ONLY_RECOVERY_CANDIDATE"
PRICE_ONLY_EXPANSION = "PRICE_ONLY_EXPANSION"
PRICE_ONLY_OVERHEATED = "PRICE_ONLY_OVERHEATED"
PRICE_ONLY_DETERIORATING = "PRICE_ONLY_DETERIORATING"
PRICE_ONLY_WEAK = "PRICE_ONLY_WEAK"
PRICE_ONLY_INSUFFICIENT_DATA = "PRICE_ONLY_INSUFFICIENT_DATA"

VALID_PRICE_ONLY_STATES = {
    PRICE_ONLY_RECOVERY_CANDIDATE,
    PRICE_ONLY_EXPANSION,
    PRICE_ONLY_OVERHEATED,
    PRICE_ONLY_DETERIORATING,
    PRICE_ONLY_WEAK,
    PRICE_ONLY_INSUFFICIENT_DATA,
}

# confirmation_status values
STATUS_HELD = "held"
STATUS_FIRST_OBSERVATION = "first_observation"
STATUS_CONFIRMED = "confirmed"
STATUS_WARNING = "warning"
STATUS_NOT_APPLICABLE = "not_applicable"

# action_signal values (what, if anything, a downstream consumer should act on)
ACTION_NONE = "NONE"
ACTION_HOLD_INSUFFICIENT_DATA = "HOLD_INSUFFICIENT_DATA"
ACTION_RECOVERY_CONFIRMED = "RECOVERY_CONFIRMED"
ACTION_OVERHEAT_WARNING = "OVERHEAT_WARNING"
ACTION_DETERIORATION_CONFIRMED = "DETERIORATION_CONFIRMED"


def classify_raw_state(
    scores: PriceScoreBundle,
    thresholds: Dict[str, float],
    *,
    prev_relative_strength_score: Optional[float] = None,
) -> str:
    """Classify this week's PRICE_ONLY_* state from this week's scores alone.

    `prev_relative_strength_score` is the *previous week's*
    `relative_strength_score` (not this week's), used only to decide
    whether relative strength is currently rising for the recovery
    candidate condition. `None` (no prior week, or prior week had no score)
    is treated as "cannot rule out rising" so a brand-new asset's first
    qualifying week isn't blocked purely for lack of history.
    """
    rs = scores.relative_strength.score
    tr = scores.trend.score
    oh = scores.overheat.score
    risk = scores.price_risk.score

    if rs is None or tr is None:
        return PRICE_ONLY_INSUFFICIENT_DATA

    if oh is not None and oh >= thresholds["overheat_score_min"]:
        return PRICE_ONLY_OVERHEATED

    if (
        risk is not None
        and risk >= thresholds["risk_score_min_for_deteriorating"]
        and tr <= thresholds["deteriorating_trend_max"]
    ):
        return PRICE_ONLY_DETERIORATING

    if rs >= thresholds["expansion_relative_strength_min"] and tr >= thresholds["expansion_trend_min"]:
        return PRICE_ONLY_EXPANSION

    rs_rising = prev_relative_strength_score is None or rs > prev_relative_strength_score
    if (
        thresholds["recovery_relative_strength_min"] <= rs < thresholds["recovery_relative_strength_max"]
        and tr >= thresholds["recovery_trend_min"]
        and rs_rising
    ):
        return PRICE_ONLY_RECOVERY_CANDIDATE

    if rs <= thresholds["weak_relative_strength_max"] and tr <= thresholds["weak_trend_max"]:
        return PRICE_ONLY_WEAK

    # Deterministic tie-break for the "mixed" zone that matches none of the
    # bands above (e.g. rising price but choppy trend, or vice versa).
    # The midpoint itself is config-driven, never a magic number in code.
    midpoint = thresholds["neutral_relative_strength_midpoint"]
    return PRICE_ONLY_WEAK if rs < midpoint else PRICE_ONLY_EXPANSION


@dataclass(frozen=True)
class StateTransitionResult:
    raw_state: str
    confirmation_status: str
    consecutive_weeks: int
    action_signal: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "raw_state": self.raw_state,
            "confirmation_status": self.confirmation_status,
            "consecutive_weeks": self.consecutive_weeks,
            "action_signal": self.action_signal,
        }


def apply_confirmation_rule(
    raw_state: str,
    previous: Optional[Dict[str, Any]],
    *,
    confirmation_cfg: Dict[str, int],
) -> StateTransitionResult:
    """Apply the 2-week confirmation rules on top of this week's `raw_state`.

    `previous` is the most recently persisted `industry_price_state_weekly`
    row for the same asset/model_version (or `None` if there isn't one).
    Only its `price_only_state` and `consecutive_weeks` fields are read.
    """
    if raw_state == PRICE_ONLY_INSUFFICIENT_DATA:
        return StateTransitionResult(
            raw_state=raw_state,
            confirmation_status=STATUS_HELD,
            consecutive_weeks=0,
            action_signal=ACTION_HOLD_INSUFFICIENT_DATA,
        )

    prev_state = previous.get("price_only_state") if previous else None
    prev_streak = int(previous.get("consecutive_weeks") or 0) if previous else 0
    streak = prev_streak + 1 if (prev_state == raw_state and prev_state is not None) else 1

    if raw_state == PRICE_ONLY_RECOVERY_CANDIDATE:
        need = confirmation_cfg["weeks_required_recovery"]
        if streak >= need:
            return StateTransitionResult(raw_state, STATUS_CONFIRMED, streak, ACTION_RECOVERY_CONFIRMED)
        return StateTransitionResult(raw_state, STATUS_FIRST_OBSERVATION, streak, ACTION_NONE)

    if raw_state == PRICE_ONLY_OVERHEATED:
        need = confirmation_cfg["weeks_required_overheat_warning"]
        if streak >= need:
            return StateTransitionResult(raw_state, STATUS_WARNING, streak, ACTION_OVERHEAT_WARNING)
        return StateTransitionResult(raw_state, STATUS_FIRST_OBSERVATION, streak, ACTION_NONE)

    if raw_state == PRICE_ONLY_DETERIORATING:
        need = confirmation_cfg["weeks_required_deteriorating_confirmed"]
        if streak >= need:
            return StateTransitionResult(raw_state, STATUS_CONFIRMED, streak, ACTION_DETERIORATION_CONFIRMED)
        return StateTransitionResult(raw_state, STATUS_FIRST_OBSERVATION, streak, ACTION_NONE)

    return StateTransitionResult(raw_state, STATUS_NOT_APPLICABLE, streak, ACTION_NONE)
