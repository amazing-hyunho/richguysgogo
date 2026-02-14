from __future__ import annotations

"""
VIX data provider (best-effort).

Why this exists
---------------
- We want a single, well-documented function (`fetch_vix`) that can be called from the
  snapshot builder without coupling it to a specific DB or LLM logic.

Data source
-----------
- `yfinance` with the Yahoo Finance symbol `^VIX`.

Failure handling
----------------
- This function must NEVER crash the nightly pipeline.
- On any error, it logs a short message and returns None.
  The caller decides how to represent missing data in snapshot status and DB (NULL).
"""

from typing import Optional


def fetch_vix() -> float | None:
    """Fetch the latest VIX close price via yfinance (^VIX).

    Returns
    -------
    - float: latest close price
    - None: if the fetch fails or data is unavailable
    """
    try:
        import yfinance as yf  # type: ignore
    except Exception as exc:  # noqa: BLE001 - optional dependency at runtime
        print(f"vix_provider_import_failed: {exc}")
        return None

    try:
        ticker = yf.Ticker("^VIX")
        # Use a short window to reduce load; last available close is used.
        hist = ticker.history(period="5d")
        if hist is None or getattr(hist, "empty", True):
            return None
        close_series = hist.get("Close")
        if close_series is None or len(close_series) < 1:
            return None
        latest_close = float(close_series.iloc[-1])
        # Guard against invalid values.
        if latest_close <= 0:
            return None
        return latest_close
    except Exception as exc:  # noqa: BLE001 - fail-safe for pipeline stability
        print(f"vix_fetch_failed: {exc}")
        return None

