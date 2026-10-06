"""Strict monthly ECOS histories. Never log request URLs containing credentials."""
from __future__ import annotations

import math
import os
import re
from urllib.parse import quote

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


def month_offset(period: str, offset: int) -> str:
    index = int(period[:4]) * 12 + int(period[4:]) - 1 + offset
    year, month = divmod(index, 12)
    return f"{year:04d}{month + 1:02d}"


def parse_history(payload: dict, spec: dict, start: str, end: str) -> list[dict]:
    block = payload.get("StatisticSearch", {})
    rows = block.get("row", [])
    if not rows or int(block.get("list_total_count", 0)) != len(rows):
        raise ValueError("empty_or_truncated_response")
    values = {}
    for row in rows:
        codes = [row.get(f"ITEM_CODE{i}") or "" for i in range(1, 5)]
        expected = spec["items"] + [""] * (4 - len(spec["items"]))
        if row.get("STAT_CODE") != spec["table"] or codes != expected:
            raise ValueError("series_identity_mismatch")
        if (row.get("UNIT_NAME") or "") != spec["source_unit"]:
            raise ValueError("unit_changed")
        period = row.get("TIME", "")
        if not re.fullmatch(r"\d{4}(0[1-9]|1[0-2])", period) or not start <= period <= end:
            raise ValueError("invalid_period")
        value = float(str(row.get("DATA_VALUE", "")).replace(",", ""))
        if not math.isfinite(value) or period in values:
            raise ValueError("invalid_or_duplicate_value")
        values[period] = value
    periods = sorted(values)
    if periods[0] != start or any(month_offset(a, 1) != b for a, b in zip(periods, periods[1:])):
        raise ValueError("history_gap")
    return [{"period": p, "value": values[p]} for p in periods]


def fetch_history(spec: dict, start: str, end: str) -> list[dict]:
    key = os.getenv("ECOS_API_KEY", "").strip()
    if not key:
        raise ValueError("missing_api_key")
    path = "/".join(quote(x, safe="") for x in [key, "json", "kr", "1", "1000", spec["table"], "M", start, end, *spec["items"]])
    try:
        with requests.Session() as session:
            session.mount("https://", HTTPAdapter(max_retries=Retry(total=2, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])))
            response = session.get("https://ecos.bok.or.kr/api/StatisticSearch/" + path, timeout=(5, 20))
            response.raise_for_status()
            payload = response.json()
    except (requests.RequestException, ValueError):
        raise ValueError("source_request_failed") from None
    return parse_history(payload, spec, start, end)
