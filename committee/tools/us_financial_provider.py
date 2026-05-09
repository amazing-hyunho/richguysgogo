from __future__ import annotations

"""
US stock financial statements provider (yfinance-based).

Fetches and normalizes:
  - Income Statement : revenue, gross_profit, operating_income, net_income, EPS
  - Balance Sheet    : total_assets, total_liabilities, total_equity, cash, total_debt
  - Cash Flow        : operating_cashflow, capital_expenditure, free_cashflow

Supports both annual and quarterly periods.

NULL design
-----------
All numeric fields are Optional[float]. Missing = None, never 0.0 placeholder.
"""

from typing import Any


def _import_yfinance():
    try:
        import yfinance as yf  # type: ignore
        return yf
    except Exception as exc:
        print(f"[us_financial] yfinance_import_failed: {exc}")
        return None


def _float_or_none(value: Any) -> float | None:
    if value is None:
        return None
    try:
        import math
        f = float(value)
        return None if math.isnan(f) else f
    except Exception:
        return None


def _safe_get(df: Any, row_name: str, col_idx: int = 0) -> float | None:
    """Safely extract a value from a yfinance DataFrame."""
    try:
        if df is None or getattr(df, "empty", True):
            return None
        if row_name not in df.index:
            return None
        series = df.loc[row_name]
        if col_idx >= len(series):
            return None
        return _float_or_none(series.iloc[col_idx])
    except Exception:
        return None


def _col_date(df: Any, col_idx: int = 0) -> str | None:
    """Return the column date label as ISO string."""
    try:
        if df is None or getattr(df, "empty", True):
            return None
        cols = df.columns
        if col_idx >= len(cols):
            return None
        dt = cols[col_idx]
        if hasattr(dt, "isoformat"):
            return dt.isoformat()[:10]
        return str(dt)[:10]
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Public result schema
# ---------------------------------------------------------------------------


def _empty_period_result(ticker: str, period_date: str | None, period_type: str) -> dict[str, Any]:
    return {
        "ticker": ticker,
        "period_date": period_date,
        "period_type": period_type,   # "annual" or "quarterly"
        "currency": "USD",
        # Income Statement
        "revenue": None,
        "gross_profit": None,
        "operating_income": None,
        "net_income": None,
        "eps_basic": None,
        "eps_diluted": None,
        "shares_outstanding": None,
        # Balance Sheet
        "total_assets": None,
        "total_liabilities": None,
        "total_equity": None,
        "cash_and_equivalents": None,
        "total_debt": None,
        # Cash Flow
        "operating_cashflow": None,
        "capital_expenditure": None,
        "free_cashflow": None,
        # Derived (computed here, not by LLM)
        "gross_margin": None,
        "operating_margin": None,
        "net_margin": None,
        "roe": None,
        "roa": None,
        "debt_ratio": None,
    }


def _compute_derived(r: dict[str, Any]) -> None:
    """Fill derived ratio fields in-place from raw fields."""
    rev = r.get("revenue")
    gp = r.get("gross_profit")
    oi = r.get("operating_income")
    ni = r.get("net_income")
    ta = r.get("total_assets")
    tl = r.get("total_liabilities")
    te = r.get("total_equity")
    ocf = r.get("operating_cashflow")
    capex = r.get("capital_expenditure")

    if rev and rev > 0:
        if gp is not None:
            r["gross_margin"] = gp / rev * 100.0
        if oi is not None:
            r["operating_margin"] = oi / rev * 100.0
        if ni is not None:
            r["net_margin"] = ni / rev * 100.0

    if te and te > 0 and ni is not None:
        r["roe"] = ni / te * 100.0

    if ta and ta > 0 and ni is not None:
        r["roa"] = ni / ta * 100.0

    if ta and ta > 0 and tl is not None:
        r["debt_ratio"] = tl / ta * 100.0

    if ocf is not None and capex is not None:
        r["free_cashflow"] = ocf + capex  # capex is negative in yfinance


def _build_period(
    ticker: str,
    col_idx: int,
    period_type: str,
    income_stmt: Any,
    balance_sheet: Any,
    cashflow: Any,
    info: dict[str, Any],
) -> dict[str, Any]:
    """Build one period result dict from yfinance DataFrames."""
    period_date = (
        _col_date(income_stmt, col_idx)
        or _col_date(balance_sheet, col_idx)
        or _col_date(cashflow, col_idx)
    )
    r = _empty_period_result(ticker, period_date, period_type)

    # Income Statement
    for alt in ("Total Revenue", "TotalRevenue"):
        v = _safe_get(income_stmt, alt, col_idx)
        if v is not None:
            r["revenue"] = v
            break
    for alt in ("Gross Profit", "GrossProfit"):
        v = _safe_get(income_stmt, alt, col_idx)
        if v is not None:
            r["gross_profit"] = v
            break
    for alt in ("Operating Income", "EBIT", "OperatingIncome"):
        v = _safe_get(income_stmt, alt, col_idx)
        if v is not None:
            r["operating_income"] = v
            break
    for alt in ("Net Income", "NetIncome"):
        v = _safe_get(income_stmt, alt, col_idx)
        if v is not None:
            r["net_income"] = v
            break
    for alt in ("Basic EPS", "BasicEPS", "Diluted EPS", "DilutedEPS"):
        v = _safe_get(income_stmt, alt, col_idx)
        if v is not None:
            key = "eps_basic" if "Basic" in alt else "eps_diluted"
            r[key] = v

    # Balance Sheet
    for alt in ("Total Assets", "TotalAssets"):
        v = _safe_get(balance_sheet, alt, col_idx)
        if v is not None:
            r["total_assets"] = v
            break
    for alt in ("Total Liabilities Net Minority Interest", "Total Liab", "TotalLiab"):
        v = _safe_get(balance_sheet, alt, col_idx)
        if v is not None:
            r["total_liabilities"] = v
            break
    for alt in (
        "Stockholders Equity",
        "Total Stockholder Equity",
        "Common Stock Equity",
        "TotalStockholderEquity",
    ):
        v = _safe_get(balance_sheet, alt, col_idx)
        if v is not None:
            r["total_equity"] = v
            break
    for alt in ("Cash And Cash Equivalents", "Cash", "CashAndCashEquivalents"):
        v = _safe_get(balance_sheet, alt, col_idx)
        if v is not None:
            r["cash_and_equivalents"] = v
            break
    for alt in ("Total Debt", "Long Term Debt", "TotalDebt"):
        v = _safe_get(balance_sheet, alt, col_idx)
        if v is not None:
            r["total_debt"] = v
            break

    # Cash Flow
    for alt in ("Operating Cash Flow", "Total Cash From Operating Activities", "OperatingCashFlow"):
        v = _safe_get(cashflow, alt, col_idx)
        if v is not None:
            r["operating_cashflow"] = v
            break
    for alt in ("Capital Expenditure", "CapEx", "CapitalExpenditure"):
        v = _safe_get(cashflow, alt, col_idx)
        if v is not None:
            r["capital_expenditure"] = v
            break

    # Shares from .info (latest only, not per-period)
    if col_idx == 0:
        r["shares_outstanding"] = _float_or_none(
            info.get("sharesOutstanding") or info.get("impliedSharesOutstanding")
        )

    _compute_derived(r)
    return r


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def fetch_us_financials(
    ticker: str,
    annual_periods: int = 4,
    quarterly_periods: int = 4,
) -> dict[str, list[dict[str, Any]]]:
    """Fetch US stock financials from yfinance.

    Parameters
    ----------
    ticker : str
        US ticker (e.g. "AAPL", "NVDA")
    annual_periods : int
        Number of annual periods to return (most recent first)
    quarterly_periods : int
        Number of quarterly periods to return (most recent first)

    Returns
    -------
    dict with keys:
        "annual"    → list of period dicts (up to annual_periods)
        "quarterly" → list of period dicts (up to quarterly_periods)
    """
    yf = _import_yfinance()
    if yf is None:
        return {"annual": [], "quarterly": []}

    ticker = ticker.strip().upper()
    try:
        t = yf.Ticker(ticker)
        info = getattr(t, "info", None) or {}

        # Annual
        inc_a = getattr(t, "income_stmt", None) or getattr(t, "financials", None)
        bal_a = getattr(t, "balance_sheet", None)
        cf_a = getattr(t, "cashflow", None) or getattr(t, "cash_flow", None)

        # Quarterly
        inc_q = getattr(t, "quarterly_income_stmt", None) or getattr(t, "quarterly_financials", None)
        bal_q = getattr(t, "quarterly_balance_sheet", None)
        cf_q = getattr(t, "quarterly_cashflow", None) or getattr(t, "quarterly_cash_flow", None)

    except Exception as exc:
        print(f"[us_financial] yfinance_fetch_failed[{ticker}]: {exc}")
        return {"annual": [], "quarterly": []}

    def _n_cols(df: Any) -> int:
        try:
            return 0 if df is None or getattr(df, "empty", True) else len(df.columns)
        except Exception:
            return 0

    annual_count = min(annual_periods, max(_n_cols(inc_a), _n_cols(bal_a), _n_cols(cf_a)))
    quarterly_count = min(quarterly_periods, max(_n_cols(inc_q), _n_cols(bal_q), _n_cols(cf_q)))

    annual_results = [
        _build_period(ticker, i, "annual", inc_a, bal_a, cf_a, info)
        for i in range(annual_count)
    ]
    quarterly_results = [
        _build_period(ticker, i, "quarterly", inc_q, bal_q, cf_q, info)
        for i in range(quarterly_count)
    ]

    return {"annual": annual_results, "quarterly": quarterly_results}


def fetch_multiple_us_financials(
    tickers: list[str],
    annual_periods: int = 4,
    quarterly_periods: int = 4,
) -> dict[str, dict[str, list[dict[str, Any]]]]:
    """Fetch financials for multiple US tickers.

    Returns dict keyed by ticker → {"annual": [...], "quarterly": [...]}
    """
    results = {}
    for ticker in tickers:
        try:
            results[ticker.strip().upper()] = fetch_us_financials(
                ticker,
                annual_periods=annual_periods,
                quarterly_periods=quarterly_periods,
            )
        except Exception as exc:
            print(f"[us_financial] fetch_error[{ticker}]: {exc}")
            results[ticker.strip().upper()] = {"annual": [], "quarterly": []}
    return results
