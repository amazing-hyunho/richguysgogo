from __future__ import annotations

"""
Phase 1: Daily Macro Engine providers (yfinance only).

Rules (per spec)
----------------
- Use `history(period="2d")` and take the latest Close.
- TNX scaling: if yield > 20, divide by 10.
- On any failure: return None (caller stores NULL in DB).
- Log failures but never crash the pipeline.
- Never return 0.0 placeholders from providers.
"""


def _import_yfinance():
    try:
        import yfinance as yf  # type: ignore
        return yf
    except Exception as exc:  # noqa: BLE001
        print(f"macro_yfinance_import_failed: {exc}")
        return None


def _fetch_latest_close(symbol: str) -> float | None:
    """Fetch latest Close for a Yahoo symbol via yfinance."""
    yf = _import_yfinance()
    if yf is None:
        return None
    try:
        t = yf.Ticker(symbol)
        hist = t.history(period="2d")
        if hist is None or getattr(hist, "empty", True):
            return None
        close_series = hist.get("Close")
        if close_series is None or len(close_series) < 1:
            return None
        value = float(close_series.iloc[-1])
        if value <= 0:
            return None
        return value
    except Exception as exc:  # noqa: BLE001
        print(f"macro_yfinance_fetch_failed[{symbol}]: {exc}")
        return None


def _scale_tnx(value: float) -> float:
    """TNX scaling rule: if yield > 20, divide by 10."""
    return value / 10.0 if value > 20.0 else value


def fetch_us10y() -> float | None:
    """US 10Y yield proxy from Yahoo (^TNX). Returns percent yield (e.g. 4.35)."""
    v = _fetch_latest_close("^TNX")
    return None if v is None else _scale_tnx(v)


def fetch_us2y() -> float | None:
    """US 2Y proxy per Phase 1 spec (uses ^IRX as the chosen proxy)."""
    v = _fetch_latest_close("^IRX")
    return None if v is None else _scale_tnx(v)


def fetch_vix() -> float | None:
    """VIX index level from Yahoo (^VIX)."""
    return _fetch_latest_close("^VIX")


def fetch_dxy() -> float | None:
    """Fetch DXY (US Dollar Index) latest close (best-effort).

    What it is
    ----------
    DXY tracks the USD against a basket of major currencies.

    Why we use it
    ------------
    It is a compact proxy for global USD strength/liquidity conditions and can help
    regime 판단 (risk-on/off) alongside yields, VIX, and FX.
    """
    for symbol in ["DX-Y.NYB", "^DXY"]:
        v = _fetch_latest_close(symbol)
        if v is not None:
            return v
    return None


def fetch_usdkrw() -> float | None:
    """USD/KRW spot (best-effort): KRW=X then USDKRW=X."""
    for symbol in ["KRW=X", "USDKRW=X"]:
        v = _fetch_latest_close(symbol)
        if v is not None:
            return v
    return None

