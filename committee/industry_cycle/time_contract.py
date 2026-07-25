from __future__ import annotations

"""Phase 0: point-in-time data contract helpers.

Design doc section 5.1 principles enforced here:
- Store observed date, first-publish date, collection time (known_at), and
  revision (vintage) separately instead of a single "date" column.
- Backtests/signals must only use data with `known_at <= signal_date`.
- A later revision must never silently overwrite what was knowable in the
  past (that is handled at the storage layer by keying on
  `(indicator_id, observed_at, vintage_at)`; this module only validates and
  filters).

This module is pure (no DB/network access) so it can be unit tested in
isolation and reused later by scoring/backtest code (Phase 1+).
"""

from datetime import date
from typing import Any, Dict, Iterable, List


def _parse_date(value: Any) -> date | None:
    """Best-effort parse of an ISO date or datetime string into a `date`."""
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    try:
        return date.fromisoformat(text[:10])
    except ValueError:
        return None


def is_known_by(
    row: Dict[str, Any],
    as_of: str,
    *,
    known_at_field: str = "known_at",
) -> bool:
    """Return True if `row[known_at_field] <= as_of` (leakage-safe check).

    Rows with a missing/unparseable `known_at` are treated as *not* knowable —
    the conservative default for backtesting (design doc: "백테스트는
    known_at <= signal_date인 데이터만 사용한다").
    """
    known_at = _parse_date(row.get(known_at_field))
    as_of_date = _parse_date(as_of)
    if known_at is None or as_of_date is None:
        return False
    return known_at <= as_of_date


def filter_known_as_of(
    rows: Iterable[Dict[str, Any]],
    as_of: str,
    *,
    known_at_field: str = "known_at",
) -> List[Dict[str, Any]]:
    """Return only the rows knowable at `as_of` (see `is_known_by`)."""
    return [r for r in rows if is_known_by(r, as_of, known_at_field=known_at_field)]


def validate_point_in_time_row(
    row: Dict[str, Any],
    *,
    today: str | None = None,
) -> List[str]:
    """Return a list of anomaly descriptions for one observation-like row.

    Checks (design doc section 13, "데이터 테스트"):
    - `observed_at` is required.
    - No field may be dated in the future relative to `today`.
    - `published_at` must not be earlier than `observed_at` (a publish date
      before the period it describes ended is a leakage red flag).
    - `known_at` must not be earlier than `published_at` (we cannot know a
      value before it was published).

    An empty return list means the row passed all checks.
    """
    issues: List[str] = []
    observed_at = _parse_date(row.get("observed_at"))
    published_at = _parse_date(row.get("published_at"))
    known_at = _parse_date(row.get("known_at"))
    today_date = _parse_date(today) if today else date.today()

    if row.get("observed_at") is None:
        issues.append("observed_at is required")
    elif observed_at is None:
        issues.append(f"observed_at is not a valid date: {row.get('observed_at')!r}")

    for field_name, value in (
        ("observed_at", observed_at),
        ("published_at", published_at),
        ("known_at", known_at),
    ):
        if value is not None and today_date is not None and value > today_date:
            issues.append(f"{field_name} is in the future ({value} > {today_date})")

    if observed_at is not None and published_at is not None and published_at < observed_at:
        issues.append(
            f"published_at ({published_at}) is earlier than observed_at ({observed_at})"
        )

    if published_at is not None and known_at is not None and known_at < published_at:
        issues.append(f"known_at ({known_at}) is earlier than published_at ({published_at})")

    return issues


def validate_price_point_in_time_row(
    row: Dict[str, Any],
    *,
    today: str | None = None,
) -> List[str]:
    """Return anomaly descriptions for one `asset_price_daily`-shaped row.

    Price rows use `trade_date`/`available_at` rather than the
    `observed_at`/`published_at`/`known_at` triple used by indicator
    observations (there is no separate "publish date" for a daily close: the
    price becomes available on/after its own trade date). Checks:
    - `trade_date` is required.
    - No field may be dated in the future relative to `today`.
    - `available_at` must not be earlier than `trade_date` (a price cannot
      be available before that day happened).

    `collected_at` is intentionally NOT checked here: it is audit/freshness
    metadata (when we happened to fetch the row), not a point-in-time
    contract field, so a late/backfilled collection is not an anomaly.
    """
    issues: List[str] = []
    trade_date = _parse_date(row.get("trade_date"))
    available_at = _parse_date(row.get("available_at"))
    today_date = _parse_date(today) if today else date.today()

    if row.get("trade_date") is None:
        issues.append("trade_date is required")
    elif trade_date is None:
        issues.append(f"trade_date is not a valid date: {row.get('trade_date')!r}")

    for field_name, value in (("trade_date", trade_date), ("available_at", available_at)):
        if value is not None and today_date is not None and value > today_date:
            issues.append(f"{field_name} is in the future ({value} > {today_date})")

    if trade_date is not None and available_at is not None and available_at < trade_date:
        issues.append(f"available_at ({available_at}) is earlier than trade_date ({trade_date})")

    return issues
