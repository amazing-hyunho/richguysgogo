from __future__ import annotations

from datetime import date
import os
from dataclasses import dataclass
from typing import Any

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
    except Exception as exc:
        return BOKBaseRateResult(value=None, status="request_failed", message=str(exc) or "request_failed")

    rows = _extract_rows(payload)
    if not rows:
        result = payload.get("RESULT") if isinstance(payload, dict) else None
        message = "empty_rows"
        if isinstance(result, dict):
            message = str(result.get("MESSAGE") or result.get("CODE") or message)
        return BOKBaseRateResult(value=None, status="no_data", message=message)
    for row in reversed(rows):
        value = _to_float(row.get("DATA_VALUE"))
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
    return []


def _to_float(value: Any) -> float | None:
    try:
        return float(value)
    except Exception:
        return None
