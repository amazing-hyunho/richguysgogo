from __future__ import annotations

"""Phase 4 weekly cycle-signal run orchestration (pure logic where possible).

Mirrors `price_factor_runner.py`'s dry-run/`--execute` split so
`scripts/run_industry_cycle_weekly.py` can be a thin CLI wrapper, run
structure/dry-run behavior stays unit-testable without touching the DB, and
one industry's failure never stops the batch (same failure-isolation
contract as every earlier phase's runner).

For each industry this:
1. Computes `cycle_score` + confidence (`cycle_scoring.compute_cycle_score`).
2. Classifies this week's raw 5-state regime and applies the 2-week
   confirmation rule (`cycle_state_machine`), using the previous week's
   `industry_cycle_signal` row (if any) for both the score-change and the
   confirmation streak.
3. Detects urgent flags (`urgent_alerts.detect_urgent_flags`) -- these are
   independent of the confirmed regime and can fire on brand-new data.
4. Determines `is_actionable` (design doc section 7.3: "신뢰도가 기준
   미만이면 국면은 표시할 수 있지만 행동 추천은 판정 보류로 제한한다") --
   only CONFIRMED/WARNING states with confidence at or above
   `min_confidence_for_action` are actionable; everything else (including
   FIRST_OBSERVATION, HELD, and low-confidence CONFIRMED) is display-only.
5. Persists `industry_cycle_signal` + per-component `industry_signal_reason`
   rows.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from committee.industry_cycle import cycle_repository, cycle_scoring, cycle_state_machine, urgent_alerts


@dataclass
class CycleRunResult:
    industry_id: str
    as_of: str
    status: str  # 'planned' | 'ok' | 'failed'
    cycle_score: Optional[float] = None
    confidence: Optional[float] = None
    raw_state: Optional[str] = None
    confirmed_state: Optional[str] = None
    confirmation_status: Optional[str] = None
    action_signal: Optional[str] = None
    is_actionable: bool = False
    urgent_flags: List[str] = field(default_factory=list)
    data_completeness: Optional[float] = None
    error: Optional[str] = None


def plan_cycle_batch(industry_ids: Iterable[str], *, as_of: str) -> List[CycleRunResult]:
    """Return the no-op "what would happen" plan for `industry_ids` (dry-run)."""
    return [CycleRunResult(industry_id=i, as_of=as_of, status="planned") for i in industry_ids]


def _is_actionable(confirmation_status: str, confidence: float, *, min_confidence_for_action: float) -> bool:
    actionable_statuses = {cycle_state_machine.STATUS_CONFIRMED, cycle_state_machine.STATUS_WARNING}
    return confirmation_status in actionable_statuses and confidence >= min_confidence_for_action


def _compute_one(
    industry_id: str,
    *,
    as_of: str,
    cycle_model_config: Dict[str, Any],
    fundamentals_model_version: str,
    candidate_model_version: str,
    price_model_version: str,
    db_path: Path | None,
) -> CycleRunResult:
    model_version = cycle_model_config["model_version"]

    bundle = cycle_scoring.compute_cycle_score(
        industry_id,
        as_of,
        cycle_model_config=cycle_model_config,
        fundamentals_model_version=fundamentals_model_version,
        candidate_model_version=candidate_model_version,
        price_model_version=price_model_version,
        db_path=db_path,
    )

    prev_signal = cycle_repository.get_latest_cycle_signal_before(industry_id, model_version, as_of, db_path=db_path)
    prev_cycle_score = prev_signal.get("cycle_score") if prev_signal else None
    prev_earnings_revision_score = prev_signal.get("earnings_revision_score") if prev_signal else None
    prev_confidence = prev_signal.get("confidence") if prev_signal else None

    raw_state = cycle_state_machine.classify_raw_cycle_state(
        bundle.score, bundle.overheat_score, cycle_model_config["state_thresholds"],
        prev_cycle_score=prev_cycle_score,
    )
    transition = cycle_state_machine.apply_cycle_confirmation_rule(
        raw_state, prev_signal, confirmation_cfg=cycle_model_config["confirmation"]
    )

    urgent_flags = urgent_alerts.detect_urgent_flags(
        earnings_revision_score=bundle.earnings_revision_score,
        breadth_score=bundle.breadth_score,
        return_1m=bundle.return_1m,
        confidence=bundle.confidence,
        prev_earnings_revision_score=prev_earnings_revision_score,
        prev_confidence=prev_confidence,
        urgent_alert_cfg=cycle_model_config["urgent_alert"],
    )

    is_actionable = _is_actionable(
        transition.confirmation_status, bundle.confidence,
        min_confidence_for_action=float(cycle_model_config["confidence"]["min_confidence_for_action"]),
    )

    signal_record = bundle.to_dict()
    signal_record.update(
        {
            "model_version": model_version,
            "data_cutoff_at": as_of,
            "raw_state": transition.raw_state,
            "confirmed_state": raw_state if transition.confirmation_status in (
                cycle_state_machine.STATUS_CONFIRMED, cycle_state_machine.STATUS_WARNING
            ) else (prev_signal.get("confirmed_state") if prev_signal else None),
            "confirmation_status": transition.confirmation_status,
            "action_signal": transition.action_signal,
            "consecutive_weeks": transition.consecutive_weeks,
            "previous_confirmed_state": prev_signal.get("confirmed_state") if prev_signal else None,
            "is_actionable": is_actionable,
            "urgent_flags": urgent_flags,
        }
    )
    cycle_repository.upsert_industry_cycle_signal(signal_record, db_path=db_path)

    reasons = [
        {
            "component_key": c["key"],
            "raw_value": c["raw_value"],
            "weight": c["weight"],
            "contribution": c["weighted_value"],
            "direction": (
                "positive" if (c["weighted_value"] or 0) > 0 else "negative" if (c["weighted_value"] or 0) < 0 else "neutral"
            ),
        }
        for c in bundle.components
        if c.get("weighted_value") is not None
    ]
    cycle_repository.replace_industry_signal_reasons(industry_id, as_of, model_version, reasons, db_path=db_path)

    return CycleRunResult(
        industry_id=industry_id,
        as_of=as_of,
        status="ok",
        cycle_score=bundle.score,
        confidence=bundle.confidence,
        raw_state=transition.raw_state,
        confirmed_state=signal_record["confirmed_state"],
        confirmation_status=transition.confirmation_status,
        action_signal=transition.action_signal,
        is_actionable=is_actionable,
        urgent_flags=urgent_flags,
        data_completeness=bundle.data_completeness,
    )


def run_cycle_batch(
    industry_ids: Iterable[str],
    *,
    as_of: str,
    cycle_model_config: Dict[str, Any],
    fundamentals_model_version: str,
    candidate_model_version: str,
    price_model_version: str,
    dry_run: bool = True,
    db_path: Path | None = None,
) -> List[CycleRunResult]:
    """Compute (and, unless `dry_run`, persist) this week's cycle signal for every industry_id.

    When `dry_run` is True (the default), no DB read/write happens at all.
    One industry's exception never stops the remaining industries.
    """
    industry_ids = list(industry_ids)
    if dry_run:
        return plan_cycle_batch(industry_ids, as_of=as_of)

    results: List[CycleRunResult] = []
    for industry_id in industry_ids:
        try:
            results.append(
                _compute_one(
                    industry_id,
                    as_of=as_of,
                    cycle_model_config=cycle_model_config,
                    fundamentals_model_version=fundamentals_model_version,
                    candidate_model_version=candidate_model_version,
                    price_model_version=price_model_version,
                    db_path=db_path,
                )
            )
        except Exception as exc:  # noqa: BLE001 - one industry's failure must not stop the batch
            results.append(CycleRunResult(industry_id=industry_id, as_of=as_of, status="failed", error=str(exc)))
            continue
    return results
