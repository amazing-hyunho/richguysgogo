from __future__ import annotations

"""
Phase 4: Structural layer providers (FRED-based).

Economic meaning
----------------
- Fed Funds Rate (FEDFUNDS): the effective/target policy rate proxy used to anchor the
  short end of the curve and a key driver of liquidity/discount rates.
- 10Y Breakeven inflation (T10YIE): market-implied long-run inflation expectation proxy.

Failure handling
----------------
- Returns None on any error (caller stores NULL, status=FAIL).
"""

from committee.tools.fred_common import fetch_fred_latest


def fetch_fed_funds_rate() -> float | None:
    """Fetch latest Fed Funds Rate (FRED: FEDFUNDS)."""
    return fetch_fred_latest("FEDFUNDS")


def fetch_breakeven_10y() -> float | None:
    """Fetch latest 10Y breakeven inflation rate (FRED: T10YIE)."""
    return fetch_fred_latest("T10YIE")



def fetch_hy_oas() -> float | None:
    """Fetch High Yield OAS (FRED: BAMLH0A0HYM2)."""
    return fetch_fred_latest("BAMLH0A0HYM2")


def fetch_ig_oas() -> float | None:
    """Fetch Investment Grade OAS (FRED: BAMLC0A0CM)."""
    return fetch_fred_latest("BAMLC0A0CM")


def fetch_fed_balance_sheet() -> float | None:
    """Fetch Fed total assets (FRED: WALCL)."""
    return fetch_fred_latest("WALCL")


def fetch_tga_balance() -> float | None:
    """US Treasury General Account balance (FRED: WDTGAL, 주간 수요일 기준, 단위: 십억달러).
    TGA가 줄면 재무부가 시장에 유동성 공급 → 위험자산에 긍정적."""
    return fetch_fred_latest("WDTGAL")


def fetch_boj_rate() -> float | None:
    """Bank of Japan 기준금리 (FRED: IRSTCB01JPM156N, 월간).
    일본 마이너스 금리 해제 이후 추이 모니터링."""
    return fetch_fred_latest("IRSTCB01JPM156N")
