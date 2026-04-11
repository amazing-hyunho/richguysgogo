from __future__ import annotations

from datetime import date
import os
from typing import Any
from urllib.parse import quote

import requests

_STAT_CODE = "901Y011"
_CYCLE = "M"
_NAME_PRIORITY = (
    "국별수출관세청",
    "수출총액",
    "총수출",
    "수출",
    "통관수출",
    "수출금액",
)
_EXPORT_UNIT_HINTS = ("달러", "백만", "금액")


def fetch_korea_export_yoy(market_date: date, timeout_sec: int = 7) -> float | None:
    """Fetch Korea export YoY% from ECOS table 901Y011 (monthly).

    Uses latest published month vs the same calendar month one year earlier.
    Returns None on any failure; logs a short reason (never prints API keys).
    """
    api_key = os.getenv("ECOS_API_KEY", "").strip()
    if not api_key:
        print("korea_export_yoy: skip (ECOS_API_KEY not set)")
        return None

    key_q = quote(api_key, safe="")
    base = f"https://ecos.bok.or.kr/api/StatisticSearch/{key_q}/json/kr"

    override = os.getenv("ECOS_EXPORT_ITEM_CODE", "").strip()
    item_code: str | None = override if override else None
    if item_code is None:
        try:
            item_code = _resolve_export_item_code(key_q, timeout_sec=timeout_sec)
        except Exception as exc:
            print(f"korea_export_yoy: item_list_failed ({exc})")
            item_code = None
    if item_code is None:
        item_code = _resolve_export_item_code_via_statistic_search(
            base, market_date, timeout_sec=timeout_sec
        )
    if not item_code:
        print("korea_export_yoy: no matching item code for 901Y011")
        return None

    end_anchor = date(market_date.year, market_date.month, 1)
    start_y, start_m = _add_months(end_anchor.year, end_anchor.month, -30)
    start_ym = f"{start_y:04d}{start_m:02d}"
    end_ym = f"{market_date.year:04d}{market_date.month:02d}"
    path = f"{_STAT_CODE}/{_CYCLE}/{start_ym}/{end_ym}/{item_code}"

    try:
        payload = _statistic_search_last_page(base, path, timeout_sec=timeout_sec, page_size=500)
    except Exception as exc:
        print(f"korea_export_yoy: statistic_search_failed ({exc})")
        return None

    rows = _extract_statistic_search_rows(payload)
    rows = [r for r in rows if str(r.get("ITEM_CODE1") or "").strip() == item_code]
    if not rows:
        result = payload.get("RESULT") if isinstance(payload, dict) else None
        msg = "empty_rows"
        if isinstance(result, dict):
            msg = str(result.get("MESSAGE") or result.get("CODE") or msg)
        print(f"korea_export_yoy: no rows ({msg})")
        return None

    by_time: dict[str, float] = {}
    for row in rows:
        t = str(row.get("TIME") or "").strip()
        if len(t) != 6 or not t.isdigit():
            continue
        v = _to_float(row.get("DATA_VALUE"))
        if v is None:
            continue
        by_time[t] = v

    if not by_time:
        print("korea_export_yoy: no parseable time/value pairs")
        return None

    latest_t = max(by_time, key=_ym_sort_key)
    prior_t = _prior_year_month(latest_t)
    if prior_t is None or prior_t not in by_time:
        print(f"korea_export_yoy: missing prior year value (latest={latest_t})")
        return None

    cur = by_time[latest_t]
    prev = by_time[prior_t]
    if prev == 0.0:
        print("korea_export_yoy: prior year value is zero")
        return None

    return round((cur / prev - 1.0) * 100.0, 6)


def _resolve_export_item_code(api_key_quoted: str, *, timeout_sec: int) -> str | None:
    base = f"https://ecos.bok.or.kr/api/StatisticItemList/{api_key_quoted}/json/kr"
    path = _STAT_CODE
    items = _statistic_item_list_all_rows(base, path, timeout_sec=timeout_sec, chunk_size=500)
    if not items:
        return None

    for needle in _NAME_PRIORITY:
        matches = [
            _item_code(it)
            for it in items
            if needle in _item_name(it) and _item_code(it)
        ]
        if matches:
            return sorted(set(matches))[0]

    export_named = [it for it in items if "수출" in _item_name(it) and _item_code(it)]
    if export_named:
        hinted = [
            it
            for it in export_named
            if any(h in (_item_unit(it) + _item_name(it)) for h in _EXPORT_UNIT_HINTS)
        ]
        pool = hinted if hinted else export_named
        codes = [_item_code(it) for it in pool]
        return sorted(set(codes))[0]

    all_codes = [_item_code(it) for it in items if _item_code(it)]
    if all_codes:
        return sorted(set(all_codes))[0]
    return None


def _stat_search_row_name1(row: dict[str, Any]) -> str:
    return str(row.get("ITEM_NAME1") or "")


def _stat_search_row_item_name(row: dict[str, Any]) -> str:
    return str(row.get("ITEM_NAME1") or row.get("ITEM_NAME") or "")


def _stat_search_row_item_code1(row: dict[str, Any]) -> str:
    return str(row.get("ITEM_CODE1") or "").strip()


def _resolve_export_item_code_via_statistic_search(
    statistic_search_base: str,
    market_date: date,
    *,
    timeout_sec: int,
) -> str | None:
    """Resolve export item code from StatisticSearch when StatisticItemList is empty or unusable.

    Queries 901Y011/M over the last 24 months without ITEM_CODE1 in the path, then picks
    ITEM_CODE1 using the same name priority as the item list, with a deterministic 수출 fallback.
    """
    end_anchor = date(market_date.year, market_date.month, 1)
    start_y, start_m = _add_months(end_anchor.year, end_anchor.month, -23)
    start_ym = f"{start_y:04d}{start_m:02d}"
    end_ym = f"{market_date.year:04d}{market_date.month:02d}"
    path = f"{_STAT_CODE}/{_CYCLE}/{start_ym}/{end_ym}"
    try:
        payload = _statistic_search_last_page(
            statistic_search_base, path, timeout_sec=timeout_sec, page_size=500
        )
    except Exception:
        return None
    rows = _extract_statistic_search_rows(payload)
    if not rows:
        return None

    for needle in _NAME_PRIORITY:
        codes = [
            c
            for r in rows
            if (c := _stat_search_row_item_code1(r)) and needle in _stat_search_row_name1(r)
        ]
        if codes:
            return sorted(set(codes))[0]

    stable = sorted(
        rows,
        key=lambda r: (_stat_search_row_item_code1(r), str(r.get("TIME") or "").strip()),
    )
    for r in stable:
        if "수출" in _stat_search_row_item_name(r):
            c = _stat_search_row_item_code1(r)
            if c:
                return c
    return None


def _item_name(item: dict[str, Any]) -> str:
    return str(item.get("ITEM_NAME1") or item.get("ITEM_NAME") or "")


def _item_code(item: dict[str, Any]) -> str:
    return str(item.get("ITEM_CODE1") or item.get("ITEM_CODE") or "").strip()


def _item_unit(item: dict[str, Any]) -> str:
    return str(item.get("UNIT_NAME") or item.get("UNIT") or "")


def _add_months(year: int, month: int, delta: int) -> tuple[int, int]:
    m = month + delta
    y = year
    while m > 12:
        m -= 12
        y += 1
    while m < 1:
        m += 12
        y -= 1
    return y, m


def _prior_year_month(ym: str) -> str | None:
    if len(ym) != 6 or not ym.isdigit():
        return None
    y = int(ym[:4])
    m = int(ym[4:6])
    return f"{y - 1:04d}{m:02d}"


def _ym_sort_key(ym: str) -> str:
    return ym if len(ym) == 6 and ym.isdigit() else "000000"


def _to_float(value: Any) -> float | None:
    try:
        return float(value)
    except Exception:
        return None


def _extract_statistic_search_rows(payload: dict[str, Any]) -> list[dict[str, Any]]:
    block = payload.get("StatisticSearch")
    if not isinstance(block, dict):
        return []
    rows = block.get("row")
    if isinstance(rows, list):
        return [r for r in rows if isinstance(r, dict)]
    if isinstance(rows, dict):
        return [rows]
    return []


def _extract_statistic_item_list_rows(payload: dict[str, Any]) -> list[dict[str, Any]]:
    block = payload.get("StatisticItemList")
    if not isinstance(block, dict):
        return []
    rows = block.get("row")
    if isinstance(rows, list):
        return [r for r in rows if isinstance(r, dict)]
    if isinstance(rows, dict):
        return [rows]
    return []


def _list_block_total(payload: dict[str, Any], block_key: str) -> int | None:
    blk = payload.get(block_key)
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
    """Fetch StatisticSearch rows; when paginated, request the last page (latest observations)."""
    first = f"{base_url}/1/{page_size}/{path_tail}"
    r = requests.get(first, timeout=timeout_sec)
    r.raise_for_status()
    payload = r.json()
    total = _list_block_total(payload, "StatisticSearch")
    if total is None or total <= page_size:
        return payload
    start = max(1, total - page_size + 1)
    last_url = f"{base_url}/{start}/{total}/{path_tail}"
    r2 = requests.get(last_url, timeout=timeout_sec)
    r2.raise_for_status()
    return r2.json()


def _statistic_item_list_all_rows(
    base_url: str, path_tail: str, *, timeout_sec: int, chunk_size: int = 500
) -> list[dict[str, Any]]:
    """Fetch every StatisticItemList row (ECOS uses start/end indices in the URL path)."""
    first = f"{base_url}/1/{chunk_size}/{path_tail}"
    r = requests.get(first, timeout=timeout_sec)
    r.raise_for_status()
    payload = r.json()
    out = _extract_statistic_item_list_rows(payload)
    total = _list_block_total(payload, "StatisticItemList")
    if total is None:
        return out
    pos = len(out) + 1
    while pos <= total:
        end = min(pos + chunk_size - 1, total)
        url = f"{base_url}/{pos}/{end}/{path_tail}"
        r2 = requests.get(url, timeout=timeout_sec)
        r2.raise_for_status()
        p2 = r2.json()
        chunk = _extract_statistic_item_list_rows(p2)
        if not chunk:
            break
        out.extend(chunk)
        pos = end + 1
    return out
