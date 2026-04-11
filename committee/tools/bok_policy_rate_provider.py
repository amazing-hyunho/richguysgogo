from __future__ import annotations

from datetime import date
import os
from typing import Any

import requests


def fetch_bok_base_rate(market_date: date, timeout_sec: int = 7) -> float | None:
    """Fetch latest available BOK base rate from ECOS API."""
    api_key = os.getenv("ECOS_API_KEY", "").strip()
    if not api_key:
        return None

    start = date(2000, 1, 1).strftime("%Y%m")
    end = market_date.strftime("%Y%m")
    url = (
        f"https://ecos.bok.or.kr/api/StatisticSearch/{api_key}/json/kr/1/5/"
        f"722Y001/M/{start}/{end}/0101000"
    )
    try:
        response = requests.get(url, timeout=timeout_sec)
        response.raise_for_status()
        payload = response.json()
    except Exception:
        return None

    rows = _extract_rows(payload)
    if not rows:
        return None
    for row in reversed(rows):
        value = _to_float(row.get("DATA_VALUE"))
        if value is not None:
            return value
    return None


def _extract_rows(payload: dict[str, Any]) -> list[dict[str, Any]]:
    block = payload.get("StatisticSearch")
    if not isinstance(block, dict):
        return []
    rows = block.get("row")
    if isinstance(rows, list):
        return [r for r in rows if isinstance(r, dict)]
    return []


def _to_float(value: Any) -> float | None:
    try:
        return float(value)
    except Exception:
        return None
