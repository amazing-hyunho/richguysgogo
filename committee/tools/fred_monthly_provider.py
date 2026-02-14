from __future__ import annotations

"""
Phase 2: Monthly Macro Engine (FRED-based).

Design rules
------------
- Never crash the pipeline: wrap all network/parse operations in try/except.
- On failure return None (caller stores NULL in DB).
- Do not use 0.0 placeholders for missing data.

Why FRED
--------
FRED provides stable, official macro time series (unemployment, CPI, PCE, PMI, wages).
"""

import os
import re

import requests


FRED_BASE = "https://api.stlouisfed.org/fred/series/observations"
_WARNED_NO_KEY = False
_WARNED_BAD_KEY_FORMAT = False
_WARNED_MISSING_SERIES: set[str] = set()


def _fred_key() -> str | None:
    raw = os.getenv("FRED_API_KEY")
    if not raw:
        return None
    # Be forgiving: users sometimes paste keys with quotes/whitespace.
    key = raw.strip().strip('"').strip("'").strip()
    global _WARNED_BAD_KEY_FORMAT  # noqa: PLW0603
    if not _WARNED_BAD_KEY_FORMAT and not re.fullmatch(r"[a-z0-9]{32}", key):
        _WARNED_BAD_KEY_FORMAT = True
        # Don't print the key; only warn about format.
        print("fred_api_key_suspicious_format (expected 32 lowercase alnum)")
    return key


def _warn_no_key_once() -> None:
    global _WARNED_NO_KEY  # noqa: PLW0603
    if _WARNED_NO_KEY:
        return
    _WARNED_NO_KEY = True
    print("fred_api_key_missing")


def _fetch_last_n_values(series_id: str, n: int) -> list[float] | None:
    """Fetch last N numeric values (descending), filtering missing '.' values."""
    api_key = _fred_key()
    if not api_key:
        _warn_no_key_once()
        return None
    try:
        resp = requests.get(
            FRED_BASE,
            params={
                "series_id": series_id,
                "api_key": api_key,
                "file_type": "json",
                "sort_order": "desc",
                "limit": int(n) * 2,  # buffer for missing values
            },
            timeout=10,
        )
        if resp.status_code != 200:
            # Print server error message (without leaking api_key).
            msg = ""
            try:
                payload = resp.json()
                msg = str(payload.get("error_message") or "").strip()
            except Exception:
                msg = (resp.text or "").strip()
            if msg:
                # Avoid spamming known-removed series (e.g., ISM series removed from FRED).
                if "series does not exist" in msg.lower():
                    if series_id not in _WARNED_MISSING_SERIES:
                        _WARNED_MISSING_SERIES.add(series_id)
                        print(f"fred_http_error[{series_id}]: {resp.status_code} {msg}")
                else:
                    print(f"fred_http_error[{series_id}]: {resp.status_code} {msg}")
            else:
                print(f"fred_http_error[{series_id}]: {resp.status_code}")
            return None
        payload = resp.json()
        obs = payload.get("observations", [])
        values: list[float] = []
        for item in obs:
            raw = item.get("value")
            if raw in (None, ".", ""):
                continue
            try:
                values.append(float(raw))
            except Exception:
                continue
            if len(values) >= n:
                break
        return values if len(values) >= n else None
    except Exception as exc:  # noqa: BLE001
        print(f"fred_fetch_failed[{series_id}]: {exc}")
        return None


def _fetch_latest(series_id: str) -> float | None:
    """Fetch latest available numeric value for a series."""
    values = _fetch_last_n_values(series_id, 1)
    if not values:
        return None
    return values[0]


def _yoy_from_index(series_id: str) -> float | None:
    """YoY% = (current / value_12_months_ago - 1) * 100."""
    values = _fetch_last_n_values(series_id, 13)
    if not values or len(values) < 13:
        return None
    current = values[0]
    prev = values[12]
    if prev == 0:
        return None
    return (current / prev - 1.0) * 100.0


# --- Provider functions (per spec) ---


def fetch_unemployment_rate() -> float | None:
    return _fetch_latest("UNRATE")


def fetch_cpi_yoy() -> float | None:
    return _yoy_from_index("CPIAUCSL")


def fetch_core_cpi_yoy() -> float | None:
    return _yoy_from_index("CPILFESL")


def fetch_pce_yoy() -> float | None:
    return _yoy_from_index("PCEPI")


def fetch_pmi() -> float | None:
    """Fetch ISM Manufacturing PMI (best-effort).

    Important note
    --------------
    ISM series such as NAPM may be unavailable in FRED for some users/environments.
    To keep data correct, we fetch the PMI directly from ISM's public page and treat
    missing/invalid values as NULL.

    Validation
    ----------
    - A realistic PMI range is roughly 30–70.
    - If value > 70 or < 20: log a warning and treat as FAIL (return None).
    - If value is between 20–30: also treat as suspicious and return None.
    """
    value = _fetch_ism_manufacturing_pmi()
    if value is None:
        return None
    if value > 70 or value < 20:
        print(f"pmi_out_of_range: {value} (expected 30-70)")
        return None
    if value < 30:
        print(f"pmi_suspicious_low: {value} (expected 30-70)")
        return None
    return value


def pmi_series_ids_tried() -> list[str]:
    """Return the list of sources attempted for PMI fetching."""
    return ["ISM_WEB(go.weareism.org)"]


def _fetch_ism_manufacturing_pmi() -> float | None:
    """Scrape the latest ISM Manufacturing PMI value from ISM public page.

    We intentionally avoid relying on FRED series IDs for ISM PMI because they may be
    unavailable. This is best-effort scraping; on failure return None (caller stores NULL).
    """
    try:
        resp = requests.get(
            "https://go.weareism.org/ism-manufacturing-pmi",
            timeout=10,
            headers={"User-Agent": "DailyAIInvestmentCommittee/1.0"},
        )
        if resp.status_code != 200:
            print(f"ism_pmi_http_error: {resp.status_code}")
            return None
        text = resp.text or ""
        # Look for the headline "Manufacturing PMI® at 47.9%" (or similar).
        m = re.search(r"Manufacturing PMI[^0-9]{0,80}at\\s+([0-9]{1,2}(?:\\.[0-9])?)", text, re.IGNORECASE)
        if not m:
            return None
        return float(m.group(1))
    except Exception as exc:  # noqa: BLE001
        print(f"ism_pmi_fetch_failed: {exc}")
        return None


def fetch_wage_growth() -> float | None:
    # Backward compatibility: this series is a level, not a growth rate.
    return fetch_wage_level()


def fetch_wage_level() -> float | None:
    """Fetch wage level (CES0500000003, latest)."""
    return _fetch_latest("CES0500000003")


def fetch_wage_yoy() -> float | None:
    """Compute wage YoY% from CES0500000003 level series."""
    values = _fetch_last_n_values("CES0500000003", 13)
    if not values or len(values) < 13:
        return None
    current = values[0]
    prev = values[12]
    if prev == 0:
        return None
    return (current / prev - 1.0) * 100.0

