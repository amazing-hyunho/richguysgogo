from __future__ import annotations

"""
Stock analyst consensus data provider.

Supported markets
-----------------
- US  : ticker as-is  (e.g. AAPL, MSFT, NVDA)
- KR  : ticker without suffix (e.g. 005930, 035420)
        Auto-appends .KS (KOSPI) or .KQ (KOSDAQ) via yfinance probe.

Data sources (priority order)
------------------------------
1. yfinance `.info` dict  — works for most US stocks and many KR stocks.
2. Naver Finance HTML     — KR-only fallback for target price / analyst count
                            when yfinance returns nothing useful.

NULL design
-----------
All fields are Optional[float|str]. Missing/unavailable values stay None.
Never store 0.0 as a placeholder.
"""

import re
from typing import Any

_NAVER_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Referer": "https://finance.naver.com/",
    "Accept-Language": "ko-KR,ko;q=0.9",
}


# ---------------------------------------------------------------------------
# Public result schema
# ---------------------------------------------------------------------------


def _empty_result(ticker: str, market: str) -> dict[str, Any]:
    return {
        "ticker": ticker,
        "market": market,
        "source": None,
        "target_mean_price": None,
        "target_high_price": None,
        "target_low_price": None,
        "recommendation_key": None,
        "recommendation_mean": None,
        "num_analysts": None,
        "forward_eps": None,
        "forward_pe": None,
        "revenue_estimate_avg": None,
        "currency": None,
        "company_name": None,
    }


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _float_or_none(value: Any) -> float | None:
    if value is None:
        return None
    try:
        f = float(value)
        return None if (f == 0.0 or f != f) else f  # reject 0.0 placeholder, NaN
    except Exception:
        return None


def _int_or_none(value: Any) -> int | None:
    if value is None:
        return None
    try:
        return int(value)
    except Exception:
        return None


def _is_kr_ticker(ticker: str) -> bool:
    """Return True if ticker looks like a KRX code (6-digit numeric)."""
    return bool(re.fullmatch(r"\d{6}", ticker.strip()))


def _is_us_ticker(ticker: str) -> bool:
    """Return True if ticker looks like a US stock symbol (letters, optionally dot)."""
    return bool(re.fullmatch(r"[A-Za-z.\-]{1,10}", ticker.strip()))


# ---------------------------------------------------------------------------
# yfinance fetcher
# ---------------------------------------------------------------------------


def _yf_fetch(yf_ticker: str) -> dict[str, Any] | None:
    """Return yfinance .info dict or None on failure."""
    try:
        import yfinance as yf  # type: ignore
        t = yf.Ticker(yf_ticker)
        info = getattr(t, "info", None)
        if not isinstance(info, dict) or not info:
            return None
        return info
    except Exception as exc:
        print(f"[consensus] yfinance_fetch_failed[{yf_ticker}]: {exc}")
        return None


def _parse_yf_info(info: dict[str, Any], ticker: str, market: str) -> dict[str, Any]:
    result = _empty_result(ticker, market)
    result["source"] = "yfinance"
    result["company_name"] = info.get("longName") or info.get("shortName")
    result["currency"] = info.get("currency")
    result["target_mean_price"] = _float_or_none(info.get("targetMeanPrice"))
    result["target_high_price"] = _float_or_none(info.get("targetHighPrice"))
    result["target_low_price"] = _float_or_none(info.get("targetLowPrice"))
    result["recommendation_key"] = info.get("recommendationKey") or None
    result["recommendation_mean"] = _float_or_none(info.get("recommendationMean"))
    result["num_analysts"] = _int_or_none(info.get("numberOfAnalystOpinions"))
    result["forward_eps"] = _float_or_none(info.get("forwardEps"))
    result["forward_pe"] = _float_or_none(info.get("forwardPE"))
    result["revenue_estimate_avg"] = _float_or_none(
        info.get("revenueEstimate") or info.get("revenueQuarterlyGrowth")
    )
    return result


def _has_useful_data(result: dict[str, Any]) -> bool:
    """Return True if at least target_mean_price or recommendation_key is populated."""
    return (
        result.get("target_mean_price") is not None
        or result.get("recommendation_key") is not None
        or result.get("forward_eps") is not None
    )


# ---------------------------------------------------------------------------
# KR suffix probe: try .KS first, then .KQ
# ---------------------------------------------------------------------------


def _fetch_kr_via_yfinance(ticker: str) -> dict[str, Any]:
    result = _empty_result(ticker, "KR")
    for suffix in (".KS", ".KQ"):
        yf_ticker = f"{ticker}{suffix}"
        info = _yf_fetch(yf_ticker)
        if info is None:
            continue
        candidate = _parse_yf_info(info, ticker, "KR")
        if _has_useful_data(candidate):
            return candidate
    return result


# ---------------------------------------------------------------------------
# Naver Finance HTML scraper (KR fallback)
# ---------------------------------------------------------------------------


def _naver_fetch_kr(ticker: str) -> dict[str, Any]:
    """Scrape Naver Finance consensus page for a KRX ticker.

    Target: https://finance.naver.com/item/coinfo.naver?code=005930
    Extracts: target_mean_price, num_analysts (best-effort).
    """
    result = _empty_result(ticker, "KR")
    try:
        import requests  # type: ignore

        url = f"https://finance.naver.com/item/coinfo.naver?code={ticker}&target=snv"
        resp = requests.get(url, headers=_NAVER_HEADERS, timeout=10)
        resp.raise_for_status()
        html = resp.text

        # Extract target price: look for patterns like "목표주가" followed by a number.
        # Naver renders: <em class="target_price">85,000</em> or similar.
        target_match = re.search(
            r"목표주가[^<>]*?<[^>]+>\s*([\d,]+)\s*</",
            html,
        )
        if not target_match:
            # Broader fallback for table-based layouts.
            target_match = re.search(
                r"targetPrice[^<>]*?>([\d,]+)<",
                html,
            )
        if target_match:
            raw = target_match.group(1).replace(",", "")
            result["target_mean_price"] = _float_or_none(raw)

        # Number of analysts.
        analyst_match = re.search(r"(\d+)\s*개\s*(증권사|기관|애널리스트)", html)
        if analyst_match:
            result["num_analysts"] = _int_or_none(analyst_match.group(1))

        # Company name from og:title / title tag.
        name_match = re.search(r"<title>([^<|]+)", html)
        if name_match:
            result["company_name"] = name_match.group(1).strip() or None

        if result.get("target_mean_price") is not None:
            result["source"] = "naver"

    except Exception as exc:
        print(f"[consensus] naver_fetch_failed[{ticker}]: {exc}")

    return result


def _naver_fetch_consensus_json(ticker: str) -> dict[str, Any]:
    """Try Naver Finance securities consensus JSON endpoint.

    URL: https://m.stock.naver.com/api/stock/{ticker}/consensus
    Returns structured JSON with target prices.
    """
    result = _empty_result(ticker, "KR")
    try:
        import requests  # type: ignore

        url = f"https://m.stock.naver.com/api/stock/{ticker}/consensus"
        headers = {**_NAVER_HEADERS, "Referer": f"https://m.stock.naver.com/domestic/stock/{ticker}/consensus"}
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code != 200:
            return result
        data = resp.json()

        # Expected structure varies; try common keys.
        if isinstance(data, dict):
            # targetPrice fields
            tp = (
                data.get("targetPrice")
                or data.get("consensusTargetPrice")
                or (data.get("consensus") or {}).get("targetPrice")
            )
            if tp is not None:
                result["target_mean_price"] = _float_or_none(tp)

            tp_high = data.get("targetPriceHigh") or (data.get("consensus") or {}).get("targetPriceHigh")
            tp_low = data.get("targetPriceLow") or (data.get("consensus") or {}).get("targetPriceLow")
            result["target_high_price"] = _float_or_none(tp_high)
            result["target_low_price"] = _float_or_none(tp_low)

            analyst_cnt = data.get("analystCount") or data.get("numberOfAnalysts")
            result["num_analysts"] = _int_or_none(analyst_cnt)

            opinion = data.get("opinion") or data.get("recommendationKey")
            if opinion:
                result["recommendation_key"] = str(opinion).lower()

        if result.get("target_mean_price") is not None:
            result["source"] = "naver_api"

    except Exception as exc:
        print(f"[consensus] naver_api_failed[{ticker}]: {exc}")

    return result


# ---------------------------------------------------------------------------
# Main public API
# ---------------------------------------------------------------------------


def fetch_stock_consensus(ticker: str) -> dict[str, Any]:
    """Fetch analyst consensus for a single ticker.

    Parameters
    ----------
    ticker : str
        - US ticker: "AAPL", "MSFT", "NVDA", "TSLA" etc.
        - KR ticker: 6-digit code like "005930" (Samsung), "035420" (NAVER)

    Returns
    -------
    dict with keys:
        ticker, market, source,
        target_mean_price, target_high_price, target_low_price,
        recommendation_key, recommendation_mean, num_analysts,
        forward_eps, forward_pe, revenue_estimate_avg,
        currency, company_name
    """
    ticker = ticker.strip().upper()

    if _is_kr_ticker(ticker):
        # Step 1: yfinance with .KS / .KQ suffix
        result = _fetch_kr_via_yfinance(ticker)
        if _has_useful_data(result):
            return result

        # Step 2: Naver Finance JSON API (mobile endpoint)
        result = _naver_fetch_consensus_json(ticker)
        if _has_useful_data(result):
            return result

        # Step 3: Naver Finance HTML scrape
        return _naver_fetch_kr(ticker)

    # US or other (yfinance direct)
    market = "US" if _is_us_ticker(ticker) else "UNKNOWN"
    info = _yf_fetch(ticker)
    if info is None:
        return _empty_result(ticker, market)
    return _parse_yf_info(info, ticker, market)


def fetch_multiple_consensus(tickers: list[str]) -> list[dict[str, Any]]:
    """Fetch consensus for a list of tickers, collecting all results.

    Failures per ticker are silently absorbed (NULL result returned).
    """
    results = []
    for tk in tickers:
        try:
            results.append(fetch_stock_consensus(tk))
        except Exception as exc:
            print(f"[consensus] fetch_error[{tk}]: {exc}")
            guess_market = "KR" if _is_kr_ticker(tk) else "US"
            results.append(_empty_result(tk.strip().upper(), guess_market))
    return results
