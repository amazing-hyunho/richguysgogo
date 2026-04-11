from __future__ import annotations

from datetime import date, timedelta
import os
from dataclasses import dataclass
from typing import Any
from urllib.parse import quote

import requests


@dataclass(frozen=True)
class BOKBaseRateResult:
    value: float | None
    status: str
    message: str


def fetch_bok_base_rate(market_date: date, timeout_sec: int = 7) -> float | None:
    """Fetch latest available BOK base rate from ECOS API."""
    result = check_bok_base_rate(market_date=market_date, timeout_sec=timeout_sec)
    return result.value


def check_bok_base_rate(market_date: date, timeout_sec: int = 7) -> BOKBaseRateResult:
    """Check ECOS integration status and return value + reason."""
    api_key = os.getenv("ECOS_API_KEY", "").strip()
    if not api_key:
        return BOKBaseRateResult(value=None, status="missing_key", message="ECOS_API_KEY_not_set")

    # Daily 722Y001/0101000 = 한국은행 기준금리 (monthly M also works; D aligns with ECOS same-day updates).
    key_q = quote(api_key, safe="")
    start_d = (market_date - timedelta(days=400)).strftime("%Y%m%d")
    end_d = market_date.strftime("%Y%m%d")
    base = f"https://ecos.bok.or.kr/api/StatisticSearch/{key_q}/json/kr"
    path = f"722Y001/D/{start_d}/{end_d}/0101000"
    try:
        payload = _statistic_search_last_page(base, path, timeout_sec=timeout_sec, page_size=500)
    except Exception as exc:
        return BOKBaseRateResult(value=None, status="request_failed", message=str(exc) or "request_failed")

    rows = _extract_rows(payload)
    rows = _filter_base_rate_rows(rows)
    if not rows:
        result = payload.get("RESULT") if isinstance(payload, dict) else None
        message = "empty_rows"
        if isinstance(result, dict):
            message = str(result.get("MESSAGE") or result.get("CODE") or message)
        return BOKBaseRateResult(value=None, status="no_data", message=message)
    latest_row = max(rows, key=_time_sort_key)
    value = _to_float(latest_row.get("DATA_VALUE"))
    if value is not None:
        return BOKBaseRateResult(value=value, status="ok", message="ok")
    return BOKBaseRateResult(value=None, status="parse_failed", message="no_numeric_data_value")


def _extract_rows(payload: dict[str, Any]) -> list[dict[str, Any]]:
    block = payload.get("StatisticSearch")
    if not isinstance(block, dict):
        return []
    rows = block.get("row")
    if isinstance(rows, list):
        return [r for r in rows if isinstance(r, dict)]
    if isinstance(rows, dict):
        return [rows]
    return []


def _to_float(value: Any) -> float | None:
    try:
        return float(value)
    except Exception:
        return None


def _filter_base_rate_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Keep only BOK base-rate item rows (defensive filtering)."""
    out: list[dict[str, Any]] = []
    for row in rows:
        item_code = str(row.get("ITEM_CODE1") or "").strip()
        if item_code != "0101000":
            continue
        out.append(row)
    return out


def _time_sort_key(row: dict[str, Any]) -> tuple[int, str]:
    """Sort key for ECOS TIME (YYYYMMDD, YYYYMM, or YYYYQn); string fallback last."""
    t = str(row.get("TIME") or "").strip()
    if len(t) == 8 and t.isdigit():
        return (0, t)
    if len(t) == 6 and t.isdigit():
        return (0, t + "00")
    if len(t) >= 6 and "Q" in t.upper():
        u = t.upper()
        try:
            year = int(u[:4])
            qi = int(u.split("Q", 1)[1])
            approx = year * 10000 + qi * 100
            return (0, f"{approx:08d}")
        except Exception:
            pass
    return (1, t)


def _statistic_search_list_total(payload: dict[str, Any]) -> int | None:
    blk = payload.get("StatisticSearch")
    if not isinstance(blk, dict):
        return None
    raw = blk.get("list_total_count")
    try:
        return int(raw)
    except Exception:
        return None


def _statistic_search_last_page(
    base_url: str, path_tail: str, *, timeout_sec: int, page_size: int
) -> dict[str, Any]:
    """Fetch StatisticSearch rows, following to the last page when list_total_count > page_size."""
    first = f"{base_url}/1/{page_size}/{path_tail}"
    r = requests.get(first, timeout=timeout_sec)
    r.raise_for_status()
    payload = r.json()
    total = _statistic_search_list_total(payload)
    if total is None or total <= page_size:
        return payload
    start = max(1, total - page_size + 1)
    last_url = f"{base_url}/{start}/{total}/{path_tail}"
    r2 = requests.get(last_url, timeout=timeout_sec)
    r2.raise_for_status()
    return r2.json()
