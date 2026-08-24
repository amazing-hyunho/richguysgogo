from __future__ import annotations

"""Deterministic lifecycle rules for 미래 경제 연구소.

The module deliberately contains no network or LLM calls. Collectors create
evidence, this module validates and scores it, and only sufficiently diverse
evidence can become an investment-committee review agenda.
"""

from datetime import date
from typing import Any, Iterable, Mapping
from urllib.parse import urlparse


REPORT_SCHEMA_VERSION = "future-economy-weekly-report-v1"
AGENDA_SCHEMA_VERSION = "future-economy-committee-agenda-v1"
EVIDENCE_SCHEMA_VERSION = "future-economy-evidence-v1"

EVIDENCE_TYPES = {
    "policy",
    "research",
    "corporate",
    "market",
    "historical_analogy",
}
ACTIVE_STATUSES = {"initial_watch", "active", "committee_review", "weakened"}
ACTIVE_RESEARCH_LIMIT = 10
NEW_RESEARCH_LIMIT = 3
AGENDA_LIMIT = 3

_SOURCE_RELIABILITY = {
    "academic_primary": 1.00,
    "academic_preprint": 0.75,
    "regulatory_filing": 1.00,
    "company_filing": 0.95,
    "company_release": 0.82,
    "official_policy": 1.00,
    "official_statistics": 0.95,
    "reputable_media": 0.72,
    "secondary_analysis": 0.55,
    "other": 0.40,
}


class FutureEconomyValidationError(ValueError):
    """Raised when research evidence violates the grounded-data contract."""


def _valid_iso_date(value: object, *, field: str) -> str:
    text = str(value or "").strip()
    try:
        return date.fromisoformat(text).isoformat()
    except ValueError as exc:
        raise FutureEconomyValidationError(f"{field}_must_be_iso_date:{text}") from exc


def _required_text(payload: Mapping[str, Any], key: str) -> str:
    value = str(payload.get(key) or "").strip()
    if not value:
        raise FutureEconomyValidationError(f"evidence_{key}_required")
    return value


def _valid_url(value: object) -> str:
    text = str(value or "").strip()
    parsed = urlparse(text)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise FutureEconomyValidationError("evidence_source_url_required")
    return text


def normalize_evidence(payload: Mapping[str, Any], *, as_of: str) -> dict[str, Any] | None:
    """Validate one evidence row and exclude look-ahead information."""

    evidence_type = _required_text(payload, "evidence_type")
    if evidence_type not in EVIDENCE_TYPES:
        raise FutureEconomyValidationError(f"unsupported_evidence_type:{evidence_type}")
    known_at = _valid_iso_date(payload.get("known_at"), field="known_at")
    if known_at > _valid_iso_date(as_of, field="as_of"):
        return None
    direction = str(payload.get("direction") or "neutral").strip()
    if direction not in {"positive", "neutral", "negative"}:
        raise FutureEconomyValidationError(f"unsupported_direction:{direction}")
    try:
        strength = float(payload.get("strength", 0.0))
    except (TypeError, ValueError) as exc:
        raise FutureEconomyValidationError("evidence_strength_must_be_number") from exc
    if not 0.0 <= strength <= 1.0:
        raise FutureEconomyValidationError("evidence_strength_out_of_range")
    source_kind = str(payload.get("source_kind") or "other").strip()
    reliability_raw = payload.get("source_reliability")
    if isinstance(reliability_raw, bool) or not isinstance(reliability_raw, (int, float)):
        reliability = _SOURCE_RELIABILITY.get(source_kind, _SOURCE_RELIABILITY["other"])
    else:
        reliability = max(0.0, min(1.0, float(reliability_raw)))
    valid_until_raw = str(payload.get("valid_until") or "").strip()
    valid_until = _valid_iso_date(valid_until_raw, field="valid_until") if valid_until_raw else ""
    if valid_until and valid_until < _valid_iso_date(as_of, field="as_of"):
        return None
    return {
        "evidence_id": _required_text(payload, "evidence_id"),
        "evidence_type": evidence_type,
        "title": _required_text(payload, "title"),
        "claim": _required_text(payload, "claim"),
        "event_date": _valid_iso_date(payload.get("event_date"), field="event_date"),
        "known_at": known_at,
        "valid_until": valid_until,
        "source_url": _valid_url(payload.get("source_url")),
        "source_name": _required_text(payload, "source_name"),
        "source_kind": source_kind,
        "source_reliability": round(reliability, 4),
        "direction": direction,
        "strength": round(strength, 4),
        "limitation": str(payload.get("limitation") or "").strip(),
        "tags": sorted({str(value).strip() for value in payload.get("tags", []) if str(value).strip()}),
    }


def radar_report_to_candidate(
    report: Mapping[str, Any],
    *,
    as_of: str,
    topic_config: Mapping[str, Any] | None = None,
) -> dict[str, Any] | None:
    """Convert a research-radar report into one future-research candidate."""

    theme = report.get("theme")
    if not isinstance(theme, Mapping):
        return None
    research_id = str(theme.get("theme_id") or "").strip()
    title = str(theme.get("name") or "").strip()
    thesis = str(theme.get("thesis") or "").strip()
    if not research_id or not title or not thesis:
        return None
    topic = dict(topic_config or {})
    evidence: list[dict[str, Any]] = []
    for row in report.get("evidence", []) if isinstance(report.get("evidence"), list) else []:
        if not isinstance(row, Mapping):
            continue
        converted = dict(row)
        converted["evidence_type"] = "research"
        try:
            normalized = normalize_evidence(converted, as_of=as_of)
        except FutureEconomyValidationError:
            continue
        if normalized is not None:
            evidence.append(normalized)
    return {
        "research_id": research_id,
        "domain_id": str(topic.get("domain_id") or research_id),
        "research_mode": str(topic.get("research_mode") or "core"),
        "title": title,
        "thesis": thesis,
        "horizon_months": int(topic.get("horizon_months") or 12),
        "transmission_chain": [
            str(value).strip() for value in topic.get("transmission_chain", []) if str(value).strip()
        ],
        "watch_industries": [
            str(value).strip() for value in topic.get("watch_industries", []) if str(value).strip()
        ],
        "watch_companies": [],
        "historical_analogues": [],
        "invalidation_conditions": [
            str(value).strip() for value in topic.get("invalidation_conditions", []) if str(value).strip()
        ],
        "evidence": evidence,
    }


def _dedupe_evidence(rows: Iterable[Mapping[str, Any]]) -> list[dict[str, Any]]:
    latest: dict[str, dict[str, Any]] = {}
    for row in rows:
        evidence_id = str(row.get("evidence_id") or "").strip()
        if not evidence_id:
            continue
        candidate = dict(row)
        previous = latest.get(evidence_id)
        if previous is None or (str(candidate.get("known_at")), str(candidate.get("source_url"))) > (
            str(previous.get("known_at")),
            str(previous.get("source_url")),
        ):
            latest[evidence_id] = candidate
    return sorted(latest.values(), key=lambda row: (str(row.get("event_date")), str(row.get("evidence_id"))))


def _score_evidence(rows: list[dict[str, Any]]) -> tuple[float, int, bool]:
    by_type: dict[str, list[float]] = {}
    positive_count = 0
    negative_count = 0
    for row in rows:
        direction = str(row.get("direction") or "neutral")
        sign = 1.0 if direction == "positive" else (-1.0 if direction == "negative" else 0.0)
        signal = sign * float(row.get("strength") or 0.0) * float(row.get("source_reliability") or 0.0)
        by_type.setdefault(str(row.get("evidence_type") or ""), []).append(signal)
        positive_count += direction == "positive"
        negative_count += direction == "negative"
    type_signals: list[float] = []
    for signals in by_type.values():
        strongest_positive = max([value for value in signals if value > 0.0], default=0.0)
        strongest_negative = min([value for value in signals if value < 0.0], default=0.0)
        type_signals.append(strongest_positive + strongest_negative)
    type_count = len([key for key in by_type if key in EVIDENCE_TYPES])
    strength_score = (sum(type_signals) / len(type_signals) * 100.0) if type_signals else 0.0
    coverage_score = type_count / len(EVIDENCE_TYPES) * 100.0
    score = max(0.0, min(100.0, 0.7 * strength_score + 0.3 * coverage_score))
    negative_only = negative_count > 0 and positive_count == 0
    return round(score, 2), type_count, negative_only


def _task_from_candidate(
    candidate: Mapping[str, Any],
    *,
    as_of: str,
    previous: Mapping[str, Any] | None,
) -> dict[str, Any]:
    previous_evidence = previous.get("evidence", []) if isinstance(previous, Mapping) else []
    evidence: list[dict[str, Any]] = []
    for row in [
        *[item for item in previous_evidence if isinstance(item, Mapping)],
        *[item for item in candidate.get("evidence", []) if isinstance(item, Mapping)],
    ]:
        try:
            normalized = normalize_evidence(row, as_of=as_of)
        except FutureEconomyValidationError:
            continue
        if normalized is not None:
            evidence.append(normalized)
    evidence = _dedupe_evidence(evidence)
    score, type_count, negative_only = _score_evidence(evidence)
    if negative_only:
        status = "weakened"
    elif type_count >= 3:
        status = "committee_review"
    elif type_count >= 2:
        status = "active"
    else:
        status = "initial_watch"
    previous_score = float(previous.get("research_score") or 0.0) if isinstance(previous, Mapping) else 0.0
    previous_status = str(previous.get("status") or "") if isinstance(previous, Mapping) else ""
    status_rank = {"weakened": 0, "initial_watch": 1, "active": 2, "committee_review": 3}
    if previous is None:
        weekly_change = "new"
    elif (
        status == "weakened" and previous_status != "weakened"
    ) or score <= previous_score - 5.0 or status_rank.get(status, 0) < status_rank.get(previous_status, 0):
        weekly_change = "weakened"
    elif score >= previous_score + 5.0 or status != previous_status:
        weekly_change = "strengthened"
    else:
        weekly_change = "maintained"
    first_seen = str(previous.get("first_seen_at") or as_of) if isinstance(previous, Mapping) else as_of
    last_updated = as_of if weekly_change != "maintained" else str(previous.get("last_updated_at") or as_of)
    return {
        "research_id": str(candidate.get("research_id") or ""),
        "domain_id": str(candidate.get("domain_id") or ""),
        "research_mode": str(
            candidate.get("research_mode") or (previous or {}).get("research_mode") or "core"
        ),
        "title": str(candidate.get("title") or ""),
        "thesis": str(candidate.get("thesis") or ""),
        "horizon_months": int(candidate.get("horizon_months") or 12),
        "status": status,
        "weekly_change": weekly_change,
        "research_score": score,
        "evidence_type_count": type_count,
        "evidence_ids": [row["evidence_id"] for row in evidence],
        "evidence": evidence,
        "transmission_chain": list(candidate.get("transmission_chain") or (previous or {}).get("transmission_chain") or []),
        "historical_analogues": list(candidate.get("historical_analogues") or (previous or {}).get("historical_analogues") or []),
        "watch_industries": list(candidate.get("watch_industries") or (previous or {}).get("watch_industries") or []),
        "watch_companies": list(candidate.get("watch_companies") or (previous or {}).get("watch_companies") or []),
        "invalidation_conditions": list(candidate.get("invalidation_conditions") or (previous or {}).get("invalidation_conditions") or []),
        "first_seen_at": first_seen,
        "last_updated_at": last_updated,
        "last_committee_handoff_at": (
            as_of if status == "committee_review" else str((previous or {}).get("last_committee_handoff_at") or "")
        ),
    }


def build_weekly_report(
    *,
    as_of: str,
    candidates: Iterable[Mapping[str, Any]],
    previous_report: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a bounded, deterministic weekly research snapshot."""

    as_of = _valid_iso_date(as_of, field="as_of")
    previous_tasks = {
        str(row.get("research_id")): row
        for row in (previous_report or {}).get("research_tasks", [])
        if isinstance(row, Mapping) and str(row.get("research_id") or "")
    }
    incoming = {
        str(row.get("research_id")): row
        for row in candidates
        if isinstance(row, Mapping) and str(row.get("research_id") or "")
    }
    tasks: list[dict[str, Any]] = []
    for research_id, previous in sorted(previous_tasks.items()):
        candidate = incoming.pop(research_id, None)
        tasks.append(_task_from_candidate(candidate or previous, as_of=as_of, previous=previous))

    new_candidates = [
        _task_from_candidate(row, as_of=as_of, previous=None)
        for row in incoming.values()
    ]
    new_candidates.sort(key=lambda row: (-float(row["research_score"]), row["research_id"]))
    remaining_slots = max(0, ACTIVE_RESEARCH_LIMIT - len([row for row in tasks if row.get("status") in ACTIVE_STATUSES]))
    tasks.extend(new_candidates[: min(NEW_RESEARCH_LIMIT, remaining_slots)])
    tasks.sort(key=lambda row: (-float(row.get("research_score") or 0.0), str(row.get("research_id") or "")))
    tasks = tasks[:ACTIVE_RESEARCH_LIMIT]

    summary = {
        "new": sum(row.get("weekly_change") == "new" for row in tasks),
        "strengthened": sum(row.get("weekly_change") == "strengthened" for row in tasks),
        "maintained": sum(row.get("weekly_change") == "maintained" for row in tasks),
        "weakened": sum(row.get("weekly_change") == "weakened" for row in tasks),
        "archived": sum(row.get("status") == "archived" for row in tasks),
        "active": sum(row.get("status") in ACTIVE_STATUSES for row in tasks),
        "committee_review": sum(row.get("status") == "committee_review" for row in tasks),
    }
    return {
        "schema_version": REPORT_SCHEMA_VERSION,
        "as_of": as_of,
        "summary": summary,
        "research_tasks": tasks,
        "methodology": {
            "evidence_types": sorted(EVIDENCE_TYPES),
            "formal_research_min_types": 2,
            "committee_review_min_types": 3,
            "new_research_limit": NEW_RESEARCH_LIMIT,
            "active_research_limit": ACTIVE_RESEARCH_LIMIT,
            "agenda_limit": AGENDA_LIMIT,
            "no_source_url_no_score": True,
            "lookahead_rule": "known_at <= as_of",
            "interpretation": "Research maturity only; not an order or automatic trading signal.",
        },
    }


def build_committee_agenda(report: Mapping[str, Any]) -> dict[str, Any]:
    """Create the strictly bounded context consumed by the daily chair."""

    items: list[dict[str, Any]] = []
    eligible = [
        row for row in report.get("research_tasks", [])
        if isinstance(row, Mapping)
        and row.get("status") == "committee_review"
        and int(row.get("evidence_type_count") or 0) >= 3
    ]
    eligible.sort(key=lambda row: (-float(row.get("research_score") or 0.0), str(row.get("research_id") or "")))
    for row in eligible[:AGENDA_LIMIT]:
        ranked_evidence = sorted(
            [item for item in row.get("evidence", []) if isinstance(item, Mapping)],
            key=lambda item: (-float(item.get("strength") or 0.0), str(item.get("evidence_id") or "")),
        )
        strongest_by_type: dict[str, Mapping[str, Any]] = {}
        for item in ranked_evidence:
            strongest_by_type.setdefault(str(item.get("evidence_type") or ""), item)
        evidence = sorted(
            strongest_by_type.values(),
            key=lambda item: (-float(item.get("strength") or 0.0), str(item.get("evidence_id") or "")),
        )[:5]
        items.append({
            "research_id": row.get("research_id"),
            "title": row.get("title"),
            "horizon_months": row.get("horizon_months"),
            "thesis": row.get("thesis"),
            "weekly_change": row.get("weekly_change"),
            "evidence_type_count": row.get("evidence_type_count"),
            "top_evidence": [
                {
                    key: item.get(key)
                    for key in ("evidence_type", "title", "claim", "event_date", "source_url", "source_name", "direction")
                }
                for item in evidence
            ],
            "transmission_chain": row.get("transmission_chain", []),
            "watch_industries": row.get("watch_industries", []),
            "watch_companies": row.get("watch_companies", []),
            "historical_analogues": row.get("historical_analogues", []),
            "invalidation_conditions": row.get("invalidation_conditions", []),
            "research_score": row.get("research_score"),
        })
    return {
        "schema_version": AGENDA_SCHEMA_VERSION,
        "as_of": str(report.get("as_of") or ""),
        "items": items,
        "item_count": len(items),
        "usage_note": "Context for macro/flow review only; never an order or automatic trading instruction.",
    }


def build_evidence_artifact(report: Mapping[str, Any]) -> dict[str, Any]:
    rows = _dedupe_evidence(
        item
        for task in report.get("research_tasks", [])
        if isinstance(task, Mapping)
        for item in task.get("evidence", [])
        if isinstance(item, Mapping)
    )
    return {
        "schema_version": EVIDENCE_SCHEMA_VERSION,
        "as_of": str(report.get("as_of") or ""),
        "evidence": rows,
        "evidence_count": len(rows),
    }
