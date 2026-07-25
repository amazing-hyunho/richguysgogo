from __future__ import annotations

"""Phase 4: urgent-alert detection (design doc section 7.3 / 11.2, pure logic).

"실적 쇼크·급락·정책 충격: 확인 기간 없이 긴급 경고" -- unlike the regular
5-state regime (`cycle_state_machine.py`), urgent alerts fire on the FIRST
week they're observed, with no 2-week confirmation wait, because by the
time a shock is confirmed twice it's too late to act on. `detect_urgent_flags`
is deliberately separate from (and runs alongside, never instead of) the
regular state machine.

Four flags, each independently config-driven
(`config/industry_cycle_model.json`'s `urgent_alert` group):
- `EARNINGS_SHOCK`: `earnings_revision_score` dropped by at least
  `earnings_shock_score_drop_min` points week-over-week (design doc:
  "실적 쇼크").
- `PRICE_CRASH`: the representative asset's 1-month return fell at or below
  `price_crash_return_1m_max` (design doc: "산업 ETF 급락").
- `BREADTH_COLLAPSE`: `breadth_score` fell at or below
  `breadth_collapse_score_max` (design doc: "시장 폭 붕괴").
- `CONFIDENCE_COLLAPSE`: `confidence` dropped by at least
  `confidence_drop_min` week-over-week (design doc: "데이터 장애로 기존
  신호 신뢰도가 크게 하락" -- a low absolute confidence alone is not urgent,
  only a *sudden drop* is, since a persistently low-confidence industry
  would otherwise re-trigger this every single week).

Every check needs both this week's and last week's value to fire (a flag
never fires on an industry's very first observed week, since there is
nothing to compare against yet -- consistent with every other "need at
least 2 data points" rule in this package).
"""

from typing import Any, Dict, List, Optional

EARNINGS_SHOCK = "EARNINGS_SHOCK"
PRICE_CRASH = "PRICE_CRASH"
BREADTH_COLLAPSE = "BREADTH_COLLAPSE"
CONFIDENCE_COLLAPSE = "CONFIDENCE_COLLAPSE"

VALID_URGENT_FLAGS = {EARNINGS_SHOCK, PRICE_CRASH, BREADTH_COLLAPSE, CONFIDENCE_COLLAPSE}


def detect_urgent_flags(
    *,
    earnings_revision_score: Optional[float],
    breadth_score: Optional[float],
    return_1m: Optional[float],
    confidence: Optional[float],
    prev_earnings_revision_score: Optional[float],
    prev_confidence: Optional[float],
    urgent_alert_cfg: Dict[str, Any],
) -> List[str]:
    """Return the (possibly empty) list of urgent flags for this week.

    All comparisons are simple, explainable threshold checks -- no
    fabricated defaults: a `None` input simply cannot trigger that flag
    (never treated as 0 or as "worse than any threshold").
    """
    flags: List[str] = []

    if earnings_revision_score is not None and prev_earnings_revision_score is not None:
        drop = prev_earnings_revision_score - earnings_revision_score
        if drop >= float(urgent_alert_cfg["earnings_shock_score_drop_min"]):
            flags.append(EARNINGS_SHOCK)

    if return_1m is not None and return_1m <= float(urgent_alert_cfg["price_crash_return_1m_max"]):
        flags.append(PRICE_CRASH)

    if breadth_score is not None and breadth_score <= float(urgent_alert_cfg["breadth_collapse_score_max"]):
        flags.append(BREADTH_COLLAPSE)

    if confidence is not None and prev_confidence is not None:
        drop = prev_confidence - confidence
        if drop >= float(urgent_alert_cfg["confidence_drop_min"]):
            flags.append(CONFIDENCE_COLLAPSE)

    return flags
