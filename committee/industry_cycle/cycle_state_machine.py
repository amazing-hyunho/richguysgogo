from __future__ import annotations

"""Phase 4: the FINAL industry regime state machine (design doc section 7.3).

Generalizes `price_state_machine.py`'s two-step pattern (raw classification,
then a 2-week confirmation rule) from Phase 1-B's price-only signal to the
real 5-state regime call that combines `cycle_score` (fundamentals +
earnings revision + relative strength + breadth, via `cycle_scoring`) with
its overheat/risk context and week-over-week change:

| 현재 조건                              | 후보 국면        |
|-----------------------------------------|-------------------|
| 낮은 수준에서 점수 상승                 | 회복 초입 (RECOVERY_EARLY)  |
| 높은 점수와 양의 변화율 유지            | 확장 (EXPANSION)  |
| 높은 사이클 점수 + 높은 과열 점수       | 과열 (OVERHEATED) |
| 점수 하락과 선행지표 악화               | 둔화 (SLOWING)    |
| 낮은 점수와 음의 변화율 지속            | 침체 (RECESSION)  |

Confirmed rules (section 7.3):
- 회복 초입: 2주 연속 조건 충족 -> confirmed
- 과열: 첫 주 관찰, 다음 주에도 유지되면 익절 경고
- 둔화->침체로의 하락 전환: 2주 연속 악화 -> confirmed
- 실적 쇼크·급락·정책 충격은 확인 기간 없이 즉시 긴급 경고로 처리되지만, that
  is `urgent_alerts.py`'s job (it inspects raw score/return drops directly),
  NOT this state machine -- this module only ever looks at 2-week-confirmed
  regime transitions.
"""

from dataclasses import dataclass
from typing import Any, Dict, Optional

CYCLE_RECOVERY_EARLY = "CYCLE_RECOVERY_EARLY"
CYCLE_EXPANSION = "CYCLE_EXPANSION"
CYCLE_OVERHEATED = "CYCLE_OVERHEATED"
CYCLE_SLOWING = "CYCLE_SLOWING"
CYCLE_RECESSION = "CYCLE_RECESSION"
CYCLE_INSUFFICIENT_DATA = "CYCLE_INSUFFICIENT_DATA"

VALID_CYCLE_STATES = {
    CYCLE_RECOVERY_EARLY,
    CYCLE_EXPANSION,
    CYCLE_OVERHEATED,
    CYCLE_SLOWING,
    CYCLE_RECESSION,
    CYCLE_INSUFFICIENT_DATA,
}

STATUS_HELD = "held"
STATUS_FIRST_OBSERVATION = "first_observation"
STATUS_CONFIRMED = "confirmed"
STATUS_WARNING = "warning"
STATUS_NOT_APPLICABLE = "not_applicable"

ACTION_NONE = "NONE"
ACTION_HOLD_INSUFFICIENT_DATA = "HOLD_INSUFFICIENT_DATA"
ACTION_RECOVERY_CONFIRMED = "RECOVERY_CONFIRMED"
ACTION_EXPANSION_CONFIRMED = "EXPANSION_CONFIRMED"
ACTION_OVERHEAT_WARNING = "OVERHEAT_WARNING"
ACTION_DETERIORATION_CONFIRMED = "DETERIORATION_CONFIRMED"


def classify_raw_cycle_state(
    cycle_score: Optional[float],
    overheat_score: Optional[float],
    thresholds: Dict[str, float],
    *,
    prev_cycle_score: Optional[float] = None,
) -> str:
    """Classify this week's raw regime from this week's `cycle_score` + `overheat_score`
    plus the *previous* week's `cycle_score` (only used to derive the change/direction --
    never this week's own future data)."""
    if cycle_score is None:
        return CYCLE_INSUFFICIENT_DATA

    change = None if prev_cycle_score is None else cycle_score - prev_cycle_score

    if (
        overheat_score is not None
        and overheat_score >= thresholds["overheat_score_min"]
        and cycle_score >= thresholds["overheat_cycle_score_min"]
    ):
        return CYCLE_OVERHEATED

    if change is not None and change <= thresholds["deteriorating_change_max"]:
        return CYCLE_RECESSION if cycle_score <= thresholds["recession_cycle_score_max"] else CYCLE_SLOWING

    if cycle_score <= thresholds["recession_cycle_score_max"] and (change is None or change <= 0):
        return CYCLE_RECESSION

    if cycle_score >= thresholds["expansion_cycle_score_min"] and (
        change is None or change >= thresholds["expansion_change_min"]
    ):
        return CYCLE_EXPANSION

    score_rising = prev_cycle_score is None or cycle_score > prev_cycle_score
    if (
        thresholds["recovery_cycle_score_min"] <= cycle_score < thresholds["recovery_cycle_score_max"]
        and score_rising
    ):
        return CYCLE_RECOVERY_EARLY

    midpoint = thresholds["neutral_cycle_score_midpoint"]
    return CYCLE_SLOWING if cycle_score < midpoint else CYCLE_EXPANSION


@dataclass(frozen=True)
class CycleStateTransitionResult:
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


def apply_cycle_confirmation_rule(
    raw_state: str,
    previous: Optional[Dict[str, Any]],
    *,
    confirmation_cfg: Dict[str, int],
) -> CycleStateTransitionResult:
    """Apply the 2-week confirmation rules on top of this week's raw cycle state.

    `previous` is the most recently persisted `industry_cycle_signal` row
    for the same industry/model_version (or `None`). Only its `raw_state`
    and `consecutive_weeks` fields are read -- mirrors
    `price_state_machine.apply_confirmation_rule` exactly, generalized to
    the 5 real regime states.
    """
    if raw_state == CYCLE_INSUFFICIENT_DATA:
        return CycleStateTransitionResult(
            raw_state=raw_state,
            confirmation_status=STATUS_HELD,
            consecutive_weeks=0,
            action_signal=ACTION_HOLD_INSUFFICIENT_DATA,
        )

    prev_state = previous.get("raw_state") if previous else None
    prev_streak = int(previous.get("consecutive_weeks") or 0) if previous else 0
    streak = prev_streak + 1 if (prev_state == raw_state and prev_state is not None) else 1

    if raw_state == CYCLE_RECOVERY_EARLY:
        need = confirmation_cfg["weeks_required_recovery"]
        if streak >= need:
            return CycleStateTransitionResult(raw_state, STATUS_CONFIRMED, streak, ACTION_RECOVERY_CONFIRMED)
        return CycleStateTransitionResult(raw_state, STATUS_FIRST_OBSERVATION, streak, ACTION_NONE)

    if raw_state == CYCLE_EXPANSION:
        need = confirmation_cfg["weeks_required_expansion"]
        if streak >= need:
            return CycleStateTransitionResult(raw_state, STATUS_CONFIRMED, streak, ACTION_EXPANSION_CONFIRMED)
        return CycleStateTransitionResult(raw_state, STATUS_FIRST_OBSERVATION, streak, ACTION_NONE)

    if raw_state == CYCLE_OVERHEATED:
        need = confirmation_cfg["weeks_required_overheat_warning"]
        if streak >= need:
            return CycleStateTransitionResult(raw_state, STATUS_WARNING, streak, ACTION_OVERHEAT_WARNING)
        return CycleStateTransitionResult(raw_state, STATUS_FIRST_OBSERVATION, streak, ACTION_NONE)

    if raw_state in (CYCLE_SLOWING, CYCLE_RECESSION):
        need = confirmation_cfg["weeks_required_deteriorating_confirmed"]
        if streak >= need:
            return CycleStateTransitionResult(raw_state, STATUS_CONFIRMED, streak, ACTION_DETERIORATION_CONFIRMED)
        return CycleStateTransitionResult(raw_state, STATUS_FIRST_OBSERVATION, streak, ACTION_NONE)

    return CycleStateTransitionResult(raw_state, STATUS_NOT_APPLICABLE, streak, ACTION_NONE)
