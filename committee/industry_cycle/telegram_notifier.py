from __future__ import annotations

"""Phase 4: weekly/urgent Telegram message composition + dedup-guarded dispatch
(design doc section 11.2, reusing `committee/adapters/telegram_sender.py` per
section 4.1's explicit reuse table).

Two independent concerns kept in separate functions on purpose:
- `compose_*`: PURE string-building from already-computed data (no DB, no
  network) -- fully unit-testable without a real Telegram token.
- `send_*`: DB reads (`cycle_repository`/`candidate_repository`) + the dedup
  check/record (`telegram_dispatch_repository`) + the actual
  `telegram_sender.send_report` call (or console fallback when no token is
  configured, exactly as `telegram_sender` already does).

Weekly digest groups (design doc section 11.2 "주간 메시지"):
- newly_confirmed_recovery: crossed the confirmation threshold THIS week
  (design doc: "새롭게 확정된 회복 초입 산업")
- recovery_maintained: still confirmed from an earlier week
- recovery_released: was confirmed last week, no longer holds this week
  ("기존 회복 신호의 유지·해제")
- overheat_warning / deterioration_confirmed ("과열 및 하락 전환")
- no_recommendation_or_insufficient_data: every industry not covered above,
  reported explicitly rather than silently omitted (design doc: "추천 없음
  또는 데이터 부족 여부") + task rule ("데이터가 부족하면 결과를 조작하지
  말고 INSUFFICIENT_DATA로 처리").
"""

from pathlib import Path
from typing import Any, Dict, List, Optional

from committee.adapters.telegram_sender import send_report
from committee.industry_cycle import (
    candidate_repository,
    cycle_repository,
    insight_repository,
    telegram_dispatch_repository,
)
from committee.industry_cycle.cycle_state_machine import (
    CYCLE_INSUFFICIENT_DATA,
    CYCLE_OVERHEATED,
    CYCLE_RECESSION,
    CYCLE_RECOVERY_EARLY,
    CYCLE_SLOWING,
    STATUS_CONFIRMED,
    STATUS_WARNING,
)

WEEKLY_ALERT_TYPE = telegram_dispatch_repository.WEEKLY_DIGEST_KEY


def classify_weekly_groups(
    signals: List[Dict[str, Any]], *, weeks_required_recovery: int
) -> Dict[str, List[Dict[str, Any]]]:
    """Bucket this week's `industry_cycle_signal` rows into the design doc's weekly-message groups.

    A signal can appear in at most one of the five groups (mutually
    exclusive by construction), so summing group sizes always equals
    `len(signals)`.
    """
    groups: Dict[str, List[Dict[str, Any]]] = {
        "newly_confirmed_recovery": [],
        "recovery_maintained": [],
        "recovery_released": [],
        "overheat_warning": [],
        "deterioration_confirmed": [],
        "no_recommendation_or_insufficient_data": [],
    }

    for signal in signals:
        raw_state = signal.get("raw_state")
        status = signal.get("confirmation_status")
        consecutive_weeks = signal.get("consecutive_weeks") or 0
        prev_confirmed = signal.get("previous_confirmed_state")
        confirmed = signal.get("confirmed_state")

        if status == STATUS_CONFIRMED and raw_state == CYCLE_RECOVERY_EARLY:
            if consecutive_weeks <= weeks_required_recovery:
                groups["newly_confirmed_recovery"].append(signal)
            else:
                groups["recovery_maintained"].append(signal)
            continue

        if prev_confirmed == CYCLE_RECOVERY_EARLY and confirmed != CYCLE_RECOVERY_EARLY:
            groups["recovery_released"].append(signal)
            continue

        if status == STATUS_WARNING and raw_state == CYCLE_OVERHEATED:
            groups["overheat_warning"].append(signal)
            continue

        if status == STATUS_CONFIRMED and raw_state in (CYCLE_SLOWING, CYCLE_RECESSION):
            groups["deterioration_confirmed"].append(signal)
            continue

        groups["no_recommendation_or_insufficient_data"].append(signal)

    return groups


def _top_reasons_text(industry_id: str, as_of: str, model_version: str, *, db_path: Path | None, limit: int = 2) -> str:
    reasons = cycle_repository.list_signal_reasons(industry_id, as_of, model_version, db_path=db_path)[:limit]
    if not reasons:
        return ""
    parts = [f"{r['component_key']}={r['raw_value']:.1f}" for r in reasons if r.get("raw_value") is not None]
    return f" ({', '.join(parts)})" if parts else ""


def _candidate_summary_lines(
    industry_id: str, as_of: str, candidate_model_version: str, *, db_path: Path | None
) -> List[str]:
    etfs = candidate_repository.list_industry_candidates(
        industry_id, as_of, candidate_model_version, asset_type="ETF", include_excluded=False, db_path=db_path
    )
    stocks = candidate_repository.list_industry_candidates(
        industry_id, as_of, candidate_model_version, asset_type="STOCK", include_excluded=False, db_path=db_path
    )
    lines: List[str] = []
    if etfs:
        top_etfs = ", ".join(f"{c['asset_id']}({c['score']:.0f})" if c.get("score") is not None else c["asset_id"] for c in etfs[:2])
        lines.append(f"    ETF: {top_etfs}")
    else:
        lines.append("    ETF: 없음")
    if stocks:
        top_stocks = ", ".join(f"{c['asset_id']}({c['score']:.0f})" if c.get("score") is not None else c["asset_id"] for c in stocks[:3])
        lines.append(f"    종목: {top_stocks}")
    return lines


def compose_weekly_message(
    signals: List[Dict[str, Any]],
    *,
    as_of: str,
    weeks_required_recovery: int,
    candidate_model_version: Optional[str] = None,
    ai_summary: Optional[str] = None,
    db_path: Path | None = None,
) -> str:
    """Compose the one combined weekly Telegram digest (pure formatting over `signals`)."""
    groups = classify_weekly_groups(signals, weeks_required_recovery=weeks_required_recovery)
    lines = [f"[산업 사이클 주간 리포트] {as_of}"]
    if ai_summary:
        lines.extend(
            [
                "\n[AI 조건부 해설]",
                ai_summary[:700],
                "  ※ 정량 신호를 변경하지 않는 참고 해설입니다.",
            ]
        )

    def _industry_line(signal: Dict[str, Any], *, with_candidates: bool) -> List[str]:
        industry_id = signal["industry_id"]
        reason_text = _top_reasons_text(industry_id, as_of, signal["model_version"], db_path=db_path)
        out = [f"  - {industry_id}: score={signal.get('cycle_score')}{reason_text}"]
        if with_candidates and candidate_model_version:
            out.extend(_candidate_summary_lines(industry_id, as_of, candidate_model_version, db_path=db_path))
        return out

    if groups["newly_confirmed_recovery"]:
        lines.append("\n[신규 확정] 회복 초입 산업")
        for s in groups["newly_confirmed_recovery"]:
            lines.extend(_industry_line(s, with_candidates=True))

    if groups["recovery_maintained"] or groups["recovery_released"]:
        lines.append("\n[회복 신호 유지·해제]")
        for s in groups["recovery_maintained"]:
            lines.append(f"  - {s['industry_id']}: 유지 ({s.get('consecutive_weeks')}주차)")
        for s in groups["recovery_released"]:
            lines.append(f"  - {s['industry_id']}: 해제 (이전: {s.get('previous_confirmed_state')})")

    if groups["overheat_warning"]:
        lines.append("\n[과열 경고]")
        for s in groups["overheat_warning"]:
            lines.extend(_industry_line(s, with_candidates=False))

    if groups["deterioration_confirmed"]:
        lines.append("\n[하락 전환 확정]")
        for s in groups["deterioration_confirmed"]:
            lines.extend(_industry_line(s, with_candidates=False))

    insufficient = groups["no_recommendation_or_insufficient_data"]
    if insufficient:
        names = ", ".join(
            f"{s['industry_id']}"
            + ("(데이터부족)" if s.get("raw_state") == CYCLE_INSUFFICIENT_DATA else "(추천보류)")
            for s in insufficient
        )
        lines.append(f"\n[추천 없음/데이터 부족] {names}")

    if not any(groups[k] for k in ("newly_confirmed_recovery", "recovery_maintained", "overheat_warning", "deterioration_confirmed")):
        lines.append("\n(이번 주 확정된 신규 신호 없음)")

    return "\n".join(lines)


def compose_urgent_message(signal: Dict[str, Any]) -> str:
    """Compose one urgent alert message for a single `industry_cycle_signal` row with urgent flags."""
    flags = signal.get("urgent_flags") or []
    header = f"[산업 사이클 긴급 경보] {signal['industry_id']} ({signal['as_of']})"
    body = [f"  - flags: {', '.join(flags)}"]
    if signal.get("cycle_score") is not None:
        body.append(f"  - cycle_score: {signal['cycle_score']:.1f} (confidence={signal.get('confidence')})")
    return "\n".join([header, *body])


def send_weekly_digest(
    as_of: str,
    model_version: str,
    *,
    weeks_required_recovery: int,
    candidate_model_version: Optional[str] = None,
    db_path: Path | None = None,
    dry_run: bool = True,
) -> Optional[str]:
    """Compose + (unless `dry_run`) dedup-guarded-send the weekly digest for `as_of`.

    Returns the composed message text, or `None` if there were no signals
    at all for this `(as_of, model_version)` (nothing to say -- never sends
    an empty message). `dry_run=True` (default) never touches
    `industry_alert_dispatch_log` or Telegram.
    """
    signals = cycle_repository.list_cycle_signals(as_of=as_of, model_version=model_version, db_path=db_path)
    if not signals:
        return None

    ai_summary = insight_repository.get_weekly_overall_summary(
        as_of, model_version, db_path=db_path
    )
    message = compose_weekly_message(
        signals, as_of=as_of, weeks_required_recovery=weeks_required_recovery,
        candidate_model_version=candidate_model_version, ai_summary=ai_summary, db_path=db_path,
    )
    if dry_run:
        return message

    is_new = telegram_dispatch_repository.record_dispatched(
        WEEKLY_ALERT_TYPE, as_of, model_version, "weekly", db_path=db_path
    )
    if not is_new:
        return message  # already sent this exact week -- composed for visibility, but not re-sent
    send_report(message)
    return message


def send_urgent_alerts(
    as_of: str,
    model_version: str,
    *,
    db_path: Path | None = None,
    dry_run: bool = True,
) -> List[str]:
    """Compose + (unless `dry_run`) dedup-guarded-send one urgent message per flagged industry.

    Returns the list of composed messages actually sent (or that WOULD be
    sent, in dry-run mode) this call -- industries whose exact
    `(industry_id, as_of, model_version, flag)` was already dispatched are
    skipped silently (already alerted, never re-alerted for the same week).
    """
    signals = cycle_repository.list_cycle_signals(as_of=as_of, model_version=model_version, db_path=db_path)
    sent: List[str] = []
    for signal in signals:
        flags = signal.get("urgent_flags") or []
        if not flags:
            continue
        new_flags = flags if dry_run else [
            f for f in flags
            if not telegram_dispatch_repository.has_been_dispatched(
                signal["industry_id"], as_of, model_version, f, db_path=db_path
            )
        ]
        if not new_flags:
            continue
        message = compose_urgent_message({**signal, "urgent_flags": new_flags})
        if dry_run:
            sent.append(message)
            continue
        for f in new_flags:
            telegram_dispatch_repository.record_dispatched(signal["industry_id"], as_of, model_version, f, db_path=db_path)
        send_report(message)
        sent.append(message)
    return sent
