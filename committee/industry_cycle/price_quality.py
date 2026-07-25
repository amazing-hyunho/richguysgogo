from __future__ import annotations

"""Phase 1-A price data quality checks (asset_price_daily).

Covers the three checks explicitly required for Phase 1-A (design doc
section 13, "데이터 테스트"): duplicate dates per asset, missing values, and
adjusted-price discontinuities. Like `committee.industry_cycle.data_quality`,
these are pure functions over plain dicts (no DB access); callers decide
whether/how to persist findings via
`committee.industry_cycle.repository.record_data_quality_event`.
"""

from collections import defaultdict
from typing import Any, Dict, List, Sequence

from committee.industry_cycle.data_quality import check_duplicate_keys
from committee.industry_cycle.time_contract import validate_price_point_in_time_row


def check_price_duplicate_dates(rows: Sequence[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Find rows that share the same `(asset_id, trade_date)` key."""
    return check_duplicate_keys(rows, ["asset_id", "trade_date"])


def check_price_missing_fields(
    rows: Sequence[Dict[str, Any]],
    *,
    required_fields: Sequence[str] = ("close_price",),
) -> List[Dict[str, Any]]:
    """Flag rows missing (NULL) any of `required_fields`.

    NULL/None is what counts as missing — a real `0.0` price is never
    treated as missing (design doc 5.1: "결측치는 0으로 채우지 않고 NULL로
    유지한다").
    """
    events: List[Dict[str, Any]] = []
    for row in rows:
        missing = [f for f in required_fields if row.get(f) is None]
        if missing:
            asset_id = row.get("asset_id")
            trade_date = row.get("trade_date")
            events.append(
                {
                    "event_type": "missing_required_field",
                    "severity": "medium",
                    "target": f"asset_id={asset_id}, trade_date={trade_date}",
                    "message": f"missing fields: {missing}",
                }
            )
    return events


def check_price_point_in_time_anomalies(
    rows: Sequence[Dict[str, Any]],
    *,
    today: str | None = None,
) -> List[Dict[str, Any]]:
    """Run `validate_price_point_in_time_row` over each row and collect anomalies.

    Checks `trade_date`/`available_at` only; `collected_at` is audit-only
    and never contributes to these anomalies (see `time_contract`).
    """
    events: List[Dict[str, Any]] = []
    for row in rows:
        for issue in validate_price_point_in_time_row(row, today=today):
            asset_id = row.get("asset_id")
            trade_date = row.get("trade_date")
            events.append(
                {
                    "event_type": "point_in_time_anomaly",
                    "severity": "high",
                    "target": f"asset_id={asset_id}, trade_date={trade_date}",
                    "message": issue,
                }
            )
    return events


def check_price_discontinuities(
    rows: Sequence[Dict[str, Any]],
    *,
    threshold_pct: float = 30.0,
) -> List[Dict[str, Any]]:
    """Flag day-over-day adjusted-price moves larger than `threshold_pct`.

    Groups by `asset_id`, sorts by `trade_date`, and compares consecutive
    closes (preferring `adj_close_price`, falling back to `close_price` when
    the adjusted value is unavailable). This is a coarse discontinuity
    detector for Phase 1-A — it does not consult a corporate-action calendar,
    so a legitimate large adjusted move can still be flagged for manual
    review; it only says "look at this," not "this is wrong."
    """
    by_asset: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for row in rows:
        asset_id = row.get("asset_id")
        if asset_id is not None:
            by_asset[str(asset_id)].append(row)

    events: List[Dict[str, Any]] = []
    for asset_id, asset_rows in by_asset.items():
        ordered = sorted(asset_rows, key=lambda r: str(r.get("trade_date") or ""))
        prev_close: float | None = None
        prev_date: str | None = None
        for row in ordered:
            close = row.get("adj_close_price")
            if close is None:
                close = row.get("close_price")
            trade_date = row.get("trade_date")
            if close is None:
                prev_close, prev_date = None, trade_date
                continue
            close = float(close)
            if prev_close is not None and prev_close != 0:
                pct_change = ((close - prev_close) / prev_close) * 100.0
                if abs(pct_change) > threshold_pct:
                    events.append(
                        {
                            "event_type": "price_discontinuity",
                            "severity": "high",
                            "target": asset_id,
                            "message": (
                                f"{prev_date} -> {trade_date}: {pct_change:+.1f}% "
                                f"({prev_close} -> {close}), exceeds {threshold_pct}% threshold"
                            ),
                        }
                    )
            prev_close, prev_date = close, trade_date
    return events
