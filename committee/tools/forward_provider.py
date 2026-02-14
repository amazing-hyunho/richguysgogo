from __future__ import annotations

"""
Forward market expectations (best-effort, yfinance-based).

Goals
-----
- Capture S&P 500 forward valuation metrics without LLM.
- Store NULL on failures (never 0.0 placeholders).

Data source
-----------
- yfinance for `^GSPC` (S&P 500 index):
  - forwardPE from `.info` when available
  - latest close from `history()`

Computation
-----------
- forward EPS is approximated as: forward_eps = price / forward_pe
  (only when both price and forward_pe are available and forward_pe > 0)
- eps_revision_3m: computed from DB history if available:
  (current_forward_eps / forward_eps_90d_ago - 1) * 100
"""

from datetime import date as dt_date

from committee.core.database import get_sp500_forward_eps_on_or_before


def _import_yfinance():
    try:
        import yfinance as yf  # type: ignore
        return yf
    except Exception as exc:  # noqa: BLE001
        print(f"forward_yfinance_import_failed: {exc}")
        return None


def fetch_sp500_forward_metrics(market_date: dt_date) -> dict[str, float | None]:
    """Fetch forward PE and derive forward EPS for S&P 500.

    Returns a dict with:
    - sp500_forward_pe: float|None
    - sp500_forward_eps: float|None
    - eps_revision_3m: float|None
    """
    yf = _import_yfinance()
    if yf is None:
        return {"sp500_forward_pe": None, "sp500_forward_eps": None, "eps_revision_3m": None}

    forward_pe: float | None = None
    price: float | None = None
    try:
        t = yf.Ticker("^GSPC")
        info = getattr(t, "info", None) or {}
        raw = info.get("forwardPE")
        if raw is not None:
            try:
                forward_pe = float(raw)
            except Exception:
                forward_pe = None

        hist = t.history(period="7d")
        if hist is not None and not getattr(hist, "empty", True):
            close_series = hist.get("Close")
            if close_series is not None and len(close_series) > 0:
                price = float(close_series.iloc[-1])
    except Exception as exc:  # noqa: BLE001
        print(f"forward_sp500_fetch_failed: {exc}")
        forward_pe = None
        price = None

    forward_eps: float | None = None
    if forward_pe is not None and forward_pe > 0 and price is not None and price > 0:
        forward_eps = price / forward_pe

    # 3-month revision: compare to historical forward EPS if present; else NULL.
    eps_revision_3m: float | None = None
    if forward_eps is not None:
        prior = get_sp500_forward_eps_on_or_before(date=market_date.isoformat(), days_back=90)
        if prior is not None and prior > 0:
            eps_revision_3m = (forward_eps / prior - 1.0) * 100.0

    return {
        "sp500_forward_pe": forward_pe,
        "sp500_forward_eps": forward_eps,
        "eps_revision_3m": eps_revision_3m,
    }

