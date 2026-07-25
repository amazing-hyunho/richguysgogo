from __future__ import annotations

"""Phase 2: KOSIS OpenAPI industry-statistics provider (best-effort, NULL-based).

Design rules (matching `committee/tools/bok_trade_provider.py` and
`committee/tools/fred_common.py`):
- Never crash the pipeline: every network/parse failure is caught and logged.
- On failure or missing `KOSIS_API_KEY`, return `None` (caller stores NULL / skips
  and records a `data_quality_event`, per the task constraint: "API 키가 없거나
  공급자가 실패하면 해당 기능을 격리하고 나머지 작업 계속").
- Never fabricate a value.

Scope note
----------
KOSIS (Korean Statistical Information Service) exposes each statistical table
(`tblId`) with its own item/classification codes (`itmId`, `objL1`, ...), so
there is no single well-known "industry production index" series id the way
FRED has `INDPRO`. `fetch_kosis_series` is therefore a generic, table-agnostic
fetcher: `config/industry_indicators.json` supplies the concrete
`org_id`/`tbl_id`/`item_id`/`obj_l1` for each KOSIS-backed indicator (as
`series_id` encodes `org_id:tbl_id:item_id[:obj_l1]`, parsed by
`committee.industry_cycle.fundamentals_ingest`), and this module just executes
whatever table/item it is given.

As of this implementation, no `KOSIS_API_KEY` is configured in this
environment, so this module is untested against the live API (see
`fetch_kosis_series` returning `None` immediately below) -- its parsing logic
is covered by unit tests with a mocked HTTP response shaped like KOSIS's
documented `statisticsData.do` JSON.
"""

import os
from typing import Any, Dict, List, Optional

import requests

KOSIS_STATISTICS_DATA_BASE = "https://kosis.kr/openapi/statisticsData.do"

_WARNED_NO_KEY = False


def _kosis_key() -> Optional[str]:
    raw = os.getenv("KOSIS_API_KEY", "").strip()
    return raw or None


def _warn_no_key_once() -> None:
    global _WARNED_NO_KEY  # noqa: PLW0603
    if _WARNED_NO_KEY:
        return
    _WARNED_NO_KEY = True
    print("kosis_api_key_missing")


def fetch_kosis_series(
    *,
    org_id: str,
    tbl_id: str,
    item_id: str,
    obj_l1: Optional[str] = None,
    prd_se: str = "M",
    start_prd_de: Optional[str] = None,
    end_prd_de: Optional[str] = None,
    timeout_sec: int = 10,
) -> Optional[List[Dict[str, Any]]]:
    """Fetch one KOSIS statistical table/item as `[{"observed_at": ..., "value": ...}]`.

    `prd_se`: KOSIS period code -- `M` (monthly), `Q` (quarterly), `Y` (annual).
    `observed_at` is normalized to `YYYY-MM-DD` (month/quarter/year mapped to the
    first day of the period) so it composes with
    `committee.industry_cycle.time_contract` the same way FRED/price observations do.

    KOSIS does not expose a separate "published_at" in this endpoint's response;
    the caller (`fundamentals_ingest`) is responsible for treating the collection
    time as the conservative `known_at`, exactly like `asset_price_daily` treats
    `available_at` as a deterministic function of `trade_date` (see
    `committee/core/database.py` module comment) -- NOT modeled as true
    publication-vintage data the way `fred_industry_provider` is.

    Returns `None` on missing API key or any failure; never fabricates a value.
    """
    api_key = _kosis_key()
    if not api_key:
        _warn_no_key_once()
        return None

    params: Dict[str, Any] = {
        "method": "getList",
        "apiKey": api_key,
        "itmId": item_id,
        "orgId": org_id,
        "tblId": tbl_id,
        "prdSe": prd_se,
        "format": "json",
        "jsonVD": "Y",
    }
    if obj_l1:
        params["objL1"] = obj_l1
    if start_prd_de:
        params["startPrdDe"] = start_prd_de
    if end_prd_de:
        params["endPrdDe"] = end_prd_de

    try:
        resp = requests.get(KOSIS_STATISTICS_DATA_BASE, params=params, timeout=timeout_sec)
        if resp.status_code != 200:
            print(f"kosis_industry_provider[{tbl_id}/{item_id}]: http_{resp.status_code}")
            return None
        payload = resp.json()
    except Exception as exc:  # noqa: BLE001
        print(f"kosis_industry_provider[{tbl_id}/{item_id}]: fetch_failed ({exc})")
        return None

    if isinstance(payload, dict) and ("err" in payload or "errMsg" in payload):
        msg = payload.get("errMsg") or payload.get("err")
        print(f"kosis_industry_provider[{tbl_id}/{item_id}]: api_error ({msg})")
        return None
    if not isinstance(payload, list):
        print(f"kosis_industry_provider[{tbl_id}/{item_id}]: unexpected_response_shape")
        return None

    rows: List[Dict[str, Any]] = []
    for row in payload:
        if not isinstance(row, dict):
            continue
        raw_value = row.get("DT")
        prd_de = str(row.get("PRD_DE") or "").strip()
        observed_at = _normalize_period(prd_de, prd_se)
        if observed_at is None:
            continue
        try:
            value = float(raw_value)
        except (TypeError, ValueError):
            continue
        rows.append({"observed_at": observed_at, "value": value})
    return rows


def _normalize_period(prd_de: str, prd_se: str) -> Optional[str]:
    """Normalize KOSIS's `PRD_DE` (e.g. `202406`, `2024Q2`, `2024`) to `YYYY-MM-DD`."""
    if not prd_de:
        return None
    digits = "".join(ch for ch in prd_de if ch.isdigit())
    try:
        if prd_se == "M" and len(digits) == 6:
            year, month = int(digits[:4]), int(digits[4:6])
            return f"{year:04d}-{month:02d}-01"
        if prd_se == "Q" and len(digits) in (5, 6):
            year = int(digits[:4])
            quarter = int(digits[-1])
            month = max(1, min(10, (quarter - 1) * 3 + 1))
            return f"{year:04d}-{month:02d}-01"
        if prd_se == "Y" and len(digits) == 4:
            return f"{int(digits):04d}-01-01"
    except Exception:  # noqa: BLE001
        return None
    return None
