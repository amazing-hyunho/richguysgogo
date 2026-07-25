from __future__ import annotations

"""Phase 2: FRED/ALFRED industry-series provider (vintage-aware, best-effort, NULL-based).

Design rules (matching `committee/tools/fred_common.py`):
- Never crash the pipeline: every network/parse failure is caught and logged.
- On failure or missing `FRED_API_KEY`, return `None` (caller stores NULL / skips).
- Never fabricate a value: `"."`/empty/unparseable FRED values are dropped, not zero-filled.

Why a separate module from `fred_common.py`
--------------------------------------------
`fred_common.fetch_fred_last_n_values` only ever asks FRED for the *current*
(most recently revised) values, output_type=1 -- fine for a live macro
dashboard, but not point-in-time-safe for backtesting a past industry
signal: a metric revised in 2026 would silently leak into a 2024 backtest.
This module instead calls FRED's ALFRED vintage machinery so
`committee.industry_cycle.fundamentals_ingest` can store a true
`published_at`/`known_at` per observation (design doc section 5.1: "백테스트는
known_at <= signal_date인 데이터만 사용한다"; section 12 Phase 2 item 4:
"발표일·빈티지 기준 백테스트").
"""

from typing import Any, Dict, List, Optional

import requests

from committee.tools.fred_common import fred_api_key

FRED_OBSERVATIONS_BASE = "https://api.stlouisfed.org/fred/series/observations"

# ALFRED's own sentinels for "no vintage-window filtering, scan every vintage
# ever recorded" -- required for output_type=4 (initial release only) to
# work across a series' full history rather than just "today's realtime
# window" (FRED otherwise defaults realtime_start=realtime_end=today, which
# returns a 400 for output_type=4 outside narrow edge cases). Verified
# against the live API on 2026-07-25 (see Phase 2 completion notes).
_FULL_VINTAGE_REALTIME_START = "1776-07-04"
_FULL_VINTAGE_REALTIME_END = "9999-12-31"


def fetch_fred_series_initial_releases(
    series_id: str,
    *,
    observation_start: Optional[str] = None,
    timeout_sec: int = 10,
) -> Optional[List[Dict[str, Any]]]:
    """Fetch every observation's FIRST published value (ALFRED `output_type=4`).

    Each row: `{"observed_at": "YYYY-MM-DD", "value": float, "published_at": "YYYY-MM-DD"}`.
    `published_at` is ALFRED's `realtime_start` for that vintage row -- the first day the
    value was FRED's "current" figure for that period. Using the initial release (rather
    than a later revision) is the conservative, point-in-time-safe choice for backfilling
    history: it is what an observer would genuinely have known at the time, never a later
    restatement leaking backward. Returns `None` on missing API key or any failure (never
    raises, never fabricates a value).
    """
    api_key = fred_api_key()
    if not api_key:
        print("fred_industry_provider: skip (FRED_API_KEY not set)")
        return None
    params: Dict[str, Any] = {
        "series_id": series_id,
        "api_key": api_key,
        "file_type": "json",
        "output_type": 4,
        "sort_order": "asc",
        "realtime_start": _FULL_VINTAGE_REALTIME_START,
        "realtime_end": _FULL_VINTAGE_REALTIME_END,
    }
    if observation_start:
        params["observation_start"] = observation_start
    try:
        resp = requests.get(FRED_OBSERVATIONS_BASE, params=params, timeout=timeout_sec)
        if resp.status_code != 200:
            print(f"fred_industry_provider[{series_id}]: http_{resp.status_code}: {_error_snippet(resp)}")
            return None
        payload = resp.json()
        return _parse_observations(payload, default_published_at=None)
    except Exception as exc:  # noqa: BLE001
        print(f"fred_industry_provider[{series_id}]: fetch_failed ({exc})")
        return None


def fetch_fred_series_as_of(
    series_id: str,
    as_of: str,
    *,
    observation_start: Optional[str] = None,
    timeout_sec: int = 10,
) -> Optional[List[Dict[str, Any]]]:
    """Fetch the vintage of `series_id` that was CURRENT on `as_of` (ALFRED realtime window).

    Uses `realtime_start=realtime_end=as_of` so every returned row reflects exactly what a
    caller querying FRED on `as_of` would have seen then -- i.e. every row is safe to treat
    as `known_at=as_of`. This is the historical-reproduction path used when re-running a past
    week's fundamentals score (`--as-of` on the CLI); `fetch_fred_series_initial_releases` is
    used for the one-time catalog backfill. Returns `None` on missing API key or failure.
    """
    api_key = fred_api_key()
    if not api_key:
        print("fred_industry_provider: skip (FRED_API_KEY not set)")
        return None
    params: Dict[str, Any] = {
        "series_id": series_id,
        "api_key": api_key,
        "file_type": "json",
        "realtime_start": as_of,
        "realtime_end": as_of,
        "sort_order": "asc",
    }
    if observation_start:
        params["observation_start"] = observation_start
    try:
        resp = requests.get(FRED_OBSERVATIONS_BASE, params=params, timeout=timeout_sec)
        if resp.status_code != 200:
            print(f"fred_industry_provider[{series_id}]: http_{resp.status_code} (as_of={as_of}): {_error_snippet(resp)}")
            return None
        payload = resp.json()
        return _parse_observations(payload, default_published_at=as_of)
    except Exception as exc:  # noqa: BLE001
        print(f"fred_industry_provider[{series_id}]: fetch_failed ({exc})")
        return None


def _error_snippet(resp: Any) -> str:
    try:
        payload = resp.json()
        return str(payload.get("error_message") or "")[:200]
    except Exception:  # noqa: BLE001
        return str(getattr(resp, "text", ""))[:200]


def _parse_observations(
    payload: Dict[str, Any], *, default_published_at: Optional[str]
) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for item in payload.get("observations", []) or []:
        raw_value = item.get("value")
        if raw_value in (None, ".", ""):
            continue
        try:
            value = float(raw_value)
        except Exception:  # noqa: BLE001
            continue
        observed_at = str(item.get("date") or "").strip()
        if not observed_at:
            continue
        published_at = default_published_at or (str(item.get("realtime_start") or "").strip() or None)
        rows.append({"observed_at": observed_at, "value": value, "published_at": published_at})
    return rows
