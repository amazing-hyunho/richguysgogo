from __future__ import annotations

"""
Korean Market Flow Agent (PyKRX)
--------------------------------
Fetch investor net buying (순매수) for the Korean stock market:
- KOSPI (market total)
- KOSDAQ (market total)

Why this module exists:
- The existing architecture had `provider.get_flows()` returning "unavailable" (no free HTTP source).
- PyKRX scrapes KRX data and is the most practical free source to restore "수급" in `snapshot`/`report.md`.

Failure policy:
- This module raises exceptions for callers to handle.
- Snapshot builder/provider must catch and degrade gracefully (no pipeline crash).

Units:
- PyKRX trading value is in KRW.
- This module converts net values to "억원" integers for report readability and consistency
  with existing `flow_summary` (which is labeled "억원, 순매수").
"""

from dataclasses import dataclass
from datetime import date
from typing import Any, Dict, Tuple


EOK = 100_000_000  # 1억원 = 100,000,000 KRW


@dataclass(frozen=True)
class KoreanMarketFlow:
    """Structured KOSPI/KOSDAQ investor flow (억원, 순매수)."""

    date: str  # YYYY-MM-DD (resolved trading day)
    market: Dict[str, Dict[str, int]]  # {"KOSPI": {...}, "KOSDAQ": {...}}


def get_korean_market_flow(asof: date | None = None) -> Dict[str, Any]:
    """
    Return Korean market investor net buying values (억원, 순매수).

    Output shape (keys are intentionally stable for snapshot/report use):
    {
        "date": "YYYY-MM-DD",
        "market": {
            "KOSPI": {"individual": int, "foreign": int, "institution": int},
            "KOSDAQ": {"individual": int, "foreign": int, "institution": int},
        }
    }
    """
    trading_ymd = _resolve_trading_day_ymd(asof or date.today())
    kospi = _fetch_market_net_buy_eok(trading_ymd, market="KOSPI")
    kosdaq = _fetch_market_net_buy_eok(trading_ymd, market="KOSDAQ")
    return {
        "date": _ymd_to_iso(trading_ymd),
        "market": {"KOSPI": kospi, "KOSDAQ": kosdaq},
    }


def _resolve_trading_day_ymd(d: date) -> str:
    """
    Resolve weekends/holidays to the last available KRX business day.
    PyKRX provides a helper for this, which also handles market holidays.
    """
    try:
        from pykrx import stock  # type: ignore
    except Exception as exc:  # pragma: no cover
        raise RuntimeError(f"pykrx_import_failed: {exc}") from exc

    ymd = d.strftime("%Y%m%d")
    try:
        # "in a week" helper is commonly used to get the nearest trading day.
        return str(stock.get_nearest_business_day_in_a_week(ymd))
    except Exception as exc:
        raise RuntimeError(f"pykrx_resolve_trading_day_failed[{ymd}]: {exc}") from exc


def _fetch_market_net_buy_eok(trading_ymd: str, market: str) -> Dict[str, int]:
    """
    Fetch investor net buying (trading value) for a given market and trading day.

    We use `get_market_trading_value_by_investor` because it provides investor breakdown.
    The function returns a pandas DataFrame; its orientation can vary by version, so we normalize.
    """
    try:
        from pykrx import stock  # type: ignore
    except Exception as exc:  # pragma: no cover
        raise RuntimeError(f"pykrx_import_failed: {exc}") from exc

    try:
        df = stock.get_market_trading_value_by_investor(trading_ymd, trading_ymd, market)
    except Exception as exc:
        raise RuntimeError(f"pykrx_fetch_failed[{market},{trading_ymd}]: {exc}") from exc

    # Normalize to a mapping: {investor_label -> net_value_krw}
    values_krw = _extract_net_values_krw(df)

    # KRX investor labels in PyKRX are typically Korean.
    individual = _pick_first(values_krw, ["개인", "individual"])
    foreign = _pick_first(values_krw, ["외국인", "foreign"])
    institution = _pick_first(values_krw, ["기관합계", "기관", "institution", "기관계"])

    return {
        "individual": _to_eok_int(individual),
        "foreign": _to_eok_int(foreign),
        "institution": _to_eok_int(institution),
    }


def _extract_net_values_krw(df: Any) -> Dict[str, int]:
    """
    Extract net values in KRW from a PyKRX DataFrame.
    Supports both common shapes:
    - index: investor labels, columns include '순매수' (or similar)
    - columns: investor labels, index include '순매수'
    """
    # Defensive import: avoid hard dependency on pandas typing.
    if df is None:
        raise RuntimeError("pykrx_returned_none")

    # Try: investor in index, net in columns
    try:
        cols = [str(c) for c in getattr(df, "columns", [])]
        idx = [str(i) for i in getattr(df, "index", [])]
        # Look for a net-buying column name.
        net_col = _pick_first_existing(cols, ["순매수", "NET", "net", "Net"])
        if net_col is not None and len(idx) > 0:
            out: Dict[str, int] = {}
            for investor in idx:
                v = df.loc[investor, net_col]
                out[str(investor)] = _to_int(v)
            if out:
                return out
    except Exception:
        pass

    # Try transpose: net in index, investors in columns
    try:
        cols = [str(c) for c in getattr(df, "columns", [])]
        idx = [str(i) for i in getattr(df, "index", [])]
        net_row = _pick_first_existing(idx, ["순매수", "NET", "net", "Net"])
        if net_row is not None and len(cols) > 0:
            out = {str(c): _to_int(df.loc[net_row, c]) for c in cols}
            if out:
                return out
    except Exception:
        pass

    raise RuntimeError("pykrx_unrecognized_dataframe_shape")


def _pick_first(values: Dict[str, int], keys: list[str]) -> int:
    for k in keys:
        if k in values:
            return int(values[k])
    raise KeyError(f"missing_keys: tried={keys}, available={list(values.keys())[:20]}")


def _pick_first_existing(values: list[str], candidates: list[str]) -> str | None:
    lower = {v.lower(): v for v in values}
    for c in candidates:
        if c in values:
            return c
        if c.lower() in lower:
            return lower[c.lower()]
    return None


def _to_int(v: Any) -> int:
    try:
        # pandas scalar -> python scalar
        if hasattr(v, "item"):
            v = v.item()
        return int(float(v))
    except Exception as exc:
        raise RuntimeError(f"value_not_int: {v}") from exc


def _to_eok_int(krw_value: int) -> int:
    # Preserve sign; round to nearest integer eok for readability.
    return int(round(float(krw_value) / EOK))


def _ymd_to_iso(ymd: str) -> str:
    if len(ymd) != 8:
        return ymd
    return f"{ymd[0:4]}-{ymd[4:6]}-{ymd[6:8]}"


if __name__ == "__main__":
    # Simple manual test:
    #   python -m committee.tools.korean_market_flow_agent
    try:
        result = get_korean_market_flow()
        print(result)
    except Exception as e:
        print(f"ERROR: {e}")
