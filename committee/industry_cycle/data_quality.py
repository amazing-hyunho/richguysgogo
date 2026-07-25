from __future__ import annotations

"""Phase 0: data quality check foundation for the industry cycle tracker.

These are pure functions operating on plain dicts/lists (no DB access). They
return findings shaped like `data_quality_event` rows; callers decide
whether/how to persist them via
`committee.industry_cycle.repository.record_data_quality_event`.

Covers the "데이터 테스트" checklist from the design doc (section 13):
- duplicate keys (e.g. asset_id + date, indicator_id + observed_at + vintage)
- point-in-time anomalies (future dates, published_at earlier than
  observed_at, known_at earlier than published_at)
- overlapping validity windows for industry/theme mappings
- missing (NULL) rate per provider/group

Score/threshold decisions (Phase 2+) are out of scope; this module only
detects and describes problems.
"""

from collections import defaultdict
from typing import Any, Dict, List, Sequence

from committee.industry_cycle.time_contract import validate_point_in_time_row


def check_duplicate_keys(
    rows: Sequence[Dict[str, Any]],
    key_fields: Sequence[str],
) -> List[Dict[str, Any]]:
    """Find rows that share the same composite key (e.g. asset_id + date)."""
    counts: Dict[tuple, int] = defaultdict(int)
    for row in rows:
        key = tuple(row.get(f) for f in key_fields)
        counts[key] += 1

    events: List[Dict[str, Any]] = []
    for key, count in counts.items():
        if count > 1:
            key_desc = ", ".join(f"{f}={v}" for f, v in zip(key_fields, key))
            events.append(
                {
                    "event_type": "duplicate_key",
                    "severity": "high",
                    "target": key_desc,
                    "message": f"{count} rows share key ({key_desc})",
                }
            )
    return events


def check_point_in_time_anomalies(
    rows: Sequence[Dict[str, Any]],
    *,
    today: str | None = None,
    target_field: str = "indicator_id",
) -> List[Dict[str, Any]]:
    """Run `validate_point_in_time_row` over each row and collect anomalies."""
    events: List[Dict[str, Any]] = []
    for row in rows:
        for issue in validate_point_in_time_row(row, today=today):
            events.append(
                {
                    "event_type": "point_in_time_anomaly",
                    "severity": "high",
                    "target": str(row.get(target_field, "")),
                    "message": issue,
                }
            )
    return events


def check_validity_overlap(
    rows: Sequence[Dict[str, Any]],
    *,
    group_fields: Sequence[str],
) -> List[Dict[str, Any]]:
    """Detect overlapping `valid_from`/`valid_to` windows within the same group.

    `group_fields` identifies what must stay non-overlapping over time, e.g.
    `("provider", "external_code")` for `industry_alias`, or `("asset_id",)`
    for `industry_asset_map`. A missing `valid_to` is treated as open-ended
    ("9999-12-31").
    """
    groups: Dict[tuple, List[Dict[str, Any]]] = defaultdict(list)
    for row in rows:
        key = tuple(row.get(f) for f in group_fields)
        groups[key].append(row)

    events: List[Dict[str, Any]] = []
    for key, group_rows in groups.items():
        intervals = []
        for row in group_rows:
            start = row.get("valid_from") or ""
            end = row.get("valid_to") or "9999-12-31"
            intervals.append((start, end))
        intervals.sort(key=lambda t: t[0])
        for i in range(len(intervals) - 1):
            start_a, end_a = intervals[i]
            start_b, end_b = intervals[i + 1]
            if start_b <= end_a:
                key_desc = ", ".join(f"{f}={v}" for f, v in zip(group_fields, key))
                events.append(
                    {
                        "event_type": "validity_overlap",
                        "severity": "medium",
                        "target": key_desc,
                        "message": (
                            f"overlapping validity windows for ({key_desc}): "
                            f"[{start_a}, {end_a}] overlaps [{start_b}, {end_b}]"
                        ),
                    }
                )
    return events


def compute_missing_rate(
    rows: Sequence[Dict[str, Any]],
    *,
    value_field: str,
    group_field: str | None = None,
) -> Dict[str, float]:
    """Return the missing (NULL) rate for `value_field`, optionally grouped.

    Returns e.g. `{"overall": 0.2}`, or `{"FRED": 0.1, "KOSIS": 0.4}` when
    `group_field` is given. NULL/None is what counts as "missing" — this
    module never treats 0 as missing.
    """
    if not rows:
        return {}
    if group_field is None:
        total = len(rows)
        missing = sum(1 for r in rows if r.get(value_field) is None)
        return {"overall": missing / total}

    totals: Dict[str, int] = defaultdict(int)
    missing: Dict[str, int] = defaultdict(int)
    for row in rows:
        key = str(row.get(group_field, "unknown"))
        totals[key] += 1
        if row.get(value_field) is None:
            missing[key] += 1
    return {k: missing[k] / totals[k] for k in totals}
