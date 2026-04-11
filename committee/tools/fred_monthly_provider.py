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

import re

import requests
from committee.tools.fred_common import fetch_fred_last_n_values


def _fetch_last_n_values(series_id: str, n: int) -> list[float] | None:
    """Fetch last N numeric values with retry and cached last-good fallback."""
    return fetch_fred_last_n_values(series_id, n)


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


def _mom_pct_from_index(series_id: str) -> float | None:
    """MoM% = (current / previous_month - 1) * 100."""
    values = _fetch_last_n_values(series_id, 2)
    if not values or len(values) < 2:
        return None
    current = values[0]
    prev = values[1]
    if prev == 0:
        return None
    return (current / prev - 1.0) * 100.0


def _mom_delta_from_level(series_id: str) -> float | None:
    """Monthly level change = current - previous_month."""
    values = _fetch_last_n_values(series_id, 2)
    if not values or len(values) < 2:
        return None
    current = values[0]
    prev = values[1]
    return current - prev


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


def fetch_retail_sales_mom() -> float | None:
    """US retail sales monthly change % (FRED: RSAFS)."""
    return _mom_pct_from_index("RSAFS")


def fetch_nfp_change() -> float | None:
    """US Nonfarm Payrolls monthly change (FRED: PAYEMS, thousands of persons)."""
    return _mom_delta_from_level("PAYEMS")

