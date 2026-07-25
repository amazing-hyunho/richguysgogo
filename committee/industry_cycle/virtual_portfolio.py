from __future__ import annotations

"""Phase 4 virtual portfolio (paper trading ledger only -- NEVER a real order).

Design doc constraints this module exists to satisfy:
- Section 1 action table: "회복 초입 확정" -> 신규 매수 후보, "둔화·하락 전환" ->
  회피 또는 가상 청산. This module encodes exactly those two transitions as a
  ledger, nothing else (no partial sizing, no rebalancing, no leverage/inverse).
- Section 2: "성과가 검증되기 전에는 실전 매매 시스템으로 취급하지 않는다.
  최소 2~3개월 동안 가상 신호를 운영하고, 6개월 성과는 데이터가 축적되는 대로
  순차 확정한다." -- `compute_forward_performance` returns None
  (INSUFFICIENT_DATA) for any horizon whose target date is still in the
  future relative to the real `today` passed in, so no performance number is
  ever reported before that much real time has actually elapsed.
- Section 14 risk table: "법적·투자 위험 | 의사결정 보조 및 모의 운용, 자동
  주문 제외" -- this module only writes rows to `industry_virtual_position`;
  it never calls a broker/order API.

Entry/exit price lookups reuse `price_repository.get_prices_as_of`, which is
already leakage-safe (never returns a price whose `available_at` is after the
`as_of` passed to it), so this ledger inherits the same point-in-time
guarantee as the rest of the pipeline.
"""

import calendar
from datetime import date, datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from committee.industry_cycle import price_repository, virtual_portfolio_repository
from committee.industry_cycle.cycle_state_machine import CYCLE_RECESSION, CYCLE_RECOVERY_EARLY, CYCLE_SLOWING

RECOVERY_STATE = CYCLE_RECOVERY_EARLY
DETERIORATION_STATES = (CYCLE_SLOWING, CYCLE_RECESSION)
FORWARD_RETURN_MONTHS = (1, 3, 6, 12)
BENCHMARK_BY_MARKET = {"KR": "KOSPI", "US": "SP500"}


def should_open_position(signal: Dict[str, Any]) -> bool:
    """새로 확정된 '회복 초입' 신호에서만 가상 매수를 연다."""
    if signal.get("confirmation_status") != "confirmed":
        return False
    if signal.get("confirmed_state") != RECOVERY_STATE:
        return False
    if signal.get("previous_confirmed_state") == RECOVERY_STATE:
        return False  # already open from an earlier week, not a new signal
    return bool(signal.get("representative_asset_id"))


def should_close_position(signal: Dict[str, Any]) -> Optional[str]:
    """열린 포지션을 이번 주에 닫아야 하면 사유 문자열을, 아니면 None을 반환.

    Urgent flags take priority (immediate risk control, matches 텔레그램
    urgent-alert semantics), then a confirmed 둔화/침체 state.
    """
    urgent_flags = signal.get("urgent_flags") or []
    if urgent_flags:
        return f"urgent_flag:{urgent_flags[0]}"
    if signal.get("confirmation_status") == "confirmed" and signal.get("confirmed_state") in DETERIORATION_STATES:
        return f"deterioration_confirmed:{signal.get('confirmed_state')}"
    return None


def _resolve_price(row: Dict[str, Any]) -> Optional[float]:
    """Adjusted-close-first, raw-close fallback -- same policy as
    `price_features.build_price_series` (design doc task item 1)."""
    for key in ("adj_close_price", "close_price"):
        value = row.get(key)
        if value is not None:
            try:
                return float(value)
            except (TypeError, ValueError):
                continue
    return None


def _price_on_or_before(
    asset_id: Optional[str], target_date: str, real_as_of: str, db_path: Path | None
) -> Optional[Dict[str, Any]]:
    """Latest row with `trade_date <= target_date`, gated by real-world
    `real_as_of` so this can never look past what has actually happened yet.
    Returns the row augmented with a `resolved_price` key, or None if no
    price at all (raw or adjusted) is available."""
    if not asset_id:
        return None
    rows = price_repository.get_prices_as_of(asset_id, real_as_of, end=target_date, db_path=db_path)
    for row in reversed(rows):
        price = _resolve_price(row)
        if price is not None:
            return {**row, "resolved_price": price}
    return None


def update_virtual_portfolio_for_signal(
    signal: Dict[str, Any], *, real_as_of: str, db_path: Path | None = None
) -> Optional[Dict[str, Any]]:
    """Apply at most one ledger transition (open XOR close) for one industry's
    weekly signal. Returns the changed ledger info, or None if nothing
    changed this week (including: no price yet available for the
    representative asset -- treated as INSUFFICIENT_DATA and simply retried
    on the next call, never fabricated).
    """
    industry_id = signal["industry_id"]
    model_version = signal["model_version"]
    as_of = signal["as_of"]

    open_position = virtual_portfolio_repository.get_open_position(industry_id, model_version, db_path=db_path)

    if open_position is None:
        if not should_open_position(signal):
            return None
        asset_id = signal["representative_asset_id"]
        market = signal.get("representative_market")
        entry_row = _price_on_or_before(asset_id, as_of, real_as_of, db_path)
        if entry_row is None:
            return None
        benchmark_asset_id = BENCHMARK_BY_MARKET.get(market)
        benchmark_row = _price_on_or_before(benchmark_asset_id, as_of, real_as_of, db_path)
        record = {
            "industry_id": industry_id,
            "model_version": model_version,
            "entry_as_of": as_of,
            "entry_trade_date": entry_row.get("trade_date"),
            "asset_id": asset_id,
            "asset_market": market,
            "entry_price": entry_row.get("resolved_price"),
            "entry_state": signal.get("confirmed_state"),
            "benchmark_asset_id": benchmark_asset_id,
            "benchmark_entry_price": benchmark_row.get("resolved_price") if benchmark_row else None,
        }
        inserted = virtual_portfolio_repository.open_position(record, db_path=db_path)
        return {**record, "status": "OPEN", "action": "opened"} if inserted else None

    reason = should_close_position(signal)
    if reason is None:
        return None
    exit_row = _price_on_or_before(open_position["asset_id"], as_of, real_as_of, db_path)
    if exit_row is None:
        return None
    benchmark_asset_id = open_position.get("benchmark_asset_id")
    benchmark_row = _price_on_or_before(benchmark_asset_id, as_of, real_as_of, db_path)
    closed = virtual_portfolio_repository.close_position(
        open_position["id"],
        exit_as_of=as_of,
        exit_trade_date=exit_row.get("trade_date"),
        exit_price=exit_row.get("resolved_price"),
        exit_reason=reason,
        benchmark_exit_price=benchmark_row.get("resolved_price") if benchmark_row else None,
        db_path=db_path,
    )
    if not closed:
        return None
    return {**open_position, "status": "CLOSED", "exit_reason": reason, "action": "closed"}


def run_virtual_portfolio_batch(
    signals: List[Dict[str, Any]], *, real_as_of: str, db_path: Path | None = None
) -> List[Dict[str, Any]]:
    """Apply `update_virtual_portfolio_for_signal` to every signal, isolating
    per-industry failures (design doc operating rule: one industry's failure
    never stops the rest of the batch)."""
    results = []
    for signal in signals:
        try:
            outcome = update_virtual_portfolio_for_signal(signal, real_as_of=real_as_of, db_path=db_path)
        except Exception as exc:  # noqa: BLE001 - isolate, don't propagate
            results.append({"industry_id": signal.get("industry_id"), "action": "error", "error": str(exc)})
            continue
        if outcome is not None:
            results.append(outcome)
    return results


def _add_months(date_str: str, months: int) -> str:
    d = datetime.strptime(date_str, "%Y-%m-%d").date()
    total_month = d.month - 1 + months
    year = d.year + total_month // 12
    month = total_month % 12 + 1
    day = min(d.day, calendar.monthrange(year, month)[1])
    return date(year, month, day).isoformat()


def compute_forward_performance(
    position: Dict[str, Any], *, today: str, db_path: Path | None = None
) -> Dict[str, Optional[float]]:
    """1·3·6·12개월 절대수익률과 벤치마크 대비 초과수익률.

    `today`가 실제로 지나지 않은 구간(진입일 + N개월 > today)은 항상 None을
    반환한다 -- "실제 시간이 지나지 않은 성과를 완료했다고 보고하지 말 것"
    규칙을 이 함수 하나로 강제한다.
    """
    entry_date = position.get("entry_trade_date") or position.get("entry_as_of")
    entry_price = position.get("entry_price")
    benchmark_entry_price = position.get("benchmark_entry_price")
    benchmark_asset_id = position.get("benchmark_asset_id")

    out: Dict[str, Optional[float]] = {}
    for months in FORWARD_RETURN_MONTHS:
        key_abs = f"return_{months}m"
        key_excess = f"excess_return_{months}m"
        if entry_date is None or entry_price is None:
            out[key_abs] = None
            out[key_excess] = None
            continue
        target_date = _add_months(str(entry_date), months)
        if target_date > today:
            out[key_abs] = None
            out[key_excess] = None
            continue
        price_row = _price_on_or_before(position["asset_id"], target_date, today, db_path)
        if price_row is None:
            out[key_abs] = None
            out[key_excess] = None
            continue
        abs_return = float(price_row["resolved_price"]) / float(entry_price) - 1.0
        out[key_abs] = abs_return
        if benchmark_entry_price is not None and benchmark_asset_id:
            bench_row = _price_on_or_before(benchmark_asset_id, target_date, today, db_path)
            if bench_row is not None:
                bench_return = float(bench_row["resolved_price"]) / float(benchmark_entry_price) - 1.0
                out[key_excess] = abs_return - bench_return
            else:
                out[key_excess] = None
        else:
            out[key_excess] = None
    return out


def summarize_portfolio_performance(
    model_version: str, *, today: str, db_path: Path | None = None
) -> Dict[str, Any]:
    """Read-only rollup for the dashboard/monthly report: every ledger row plus
    its forward performance (INSUFFICIENT_DATA-safe), and a 6-month hit rate
    computed only over positions old enough to already have that data."""
    positions = virtual_portfolio_repository.list_positions(model_version=model_version, db_path=db_path)
    enriched: List[Dict[str, Any]] = []
    for pos in positions:
        perf = compute_forward_performance(pos, today=today, db_path=db_path)
        enriched.append({**pos, **perf})

    six_month_excess = [p["excess_return_6m"] for p in enriched if p.get("excess_return_6m") is not None]
    hit_rate_6m = (sum(1 for r in six_month_excess if r > 0) / len(six_month_excess)) if six_month_excess else None
    avg_excess_return_6m = (sum(six_month_excess) / len(six_month_excess)) if six_month_excess else None

    return {
        "model_version": model_version,
        "as_of": today,
        "open_count": sum(1 for p in enriched if p.get("status") == "OPEN"),
        "closed_count": sum(1 for p in enriched if p.get("status") == "CLOSED"),
        "positions": enriched,
        "hit_rate_6m": hit_rate_6m,
        "avg_excess_return_6m": avg_excess_return_6m,
        "six_month_sample_size": len(six_month_excess),
    }
