"""
Financial statements sync script.

Supports:
  KR stocks  — DART OpenAPI (annual + quarterly)
  US stocks  — yfinance (annual + quarterly, no API key needed)

Usage
-----
# KR 연간 재무제표 (2024)
    python scripts/sync_financials.py --year 2024

# KR 분기 포함 (연간 + 1Q/2Q/3Q)
    python scripts/sync_financials.py --year 2024 --quarterly

# 특정 KR 티커만
    python scripts/sync_financials.py --year 2024 --kr-tickers 005930 000660

# US 주식 재무제표 (기본 워치리스트)
    python scripts/sync_financials.py --us

# US 특정 티커
    python scripts/sync_financials.py --us --us-tickers AAPL NVDA MSFT

# KR + US 모두
    python scripts/sync_financials.py --year 2024 --quarterly --us

# 종목 재무성과 조회
    python scripts/sync_financials.py --show 005930
    python scripts/sync_financials.py --show AAPL
"""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from committee.core.database import (
    connect,
    get_financial_metrics,
    upsert_dart_company,
    upsert_financial_metric,
    upsert_financial_statement,
)
from committee.tools.dart_client import (
    DART_REPORT_CODES,
    fetch_dart_company_codes,
    fetch_financials,
)
from committee.tools.us_financial_provider import fetch_multiple_us_financials

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

DEFAULT_US_TICKERS = [
    "AAPL", "MSFT", "NVDA", "GOOGL", "AMZN",
    "META", "TSLA", "AVGO", "JPM", "V",
]

KR_ACCOUNT_NAME_MAP = {
    "매출액": "revenue",
    "영업이익": "operating_income",
    "당기순이익": "net_income",
    "자산총계": "total_assets",
    "부채총계": "total_liabilities",
    "자본총계": "total_equity",
}

# ---------------------------------------------------------------------------
# KR helpers
# ---------------------------------------------------------------------------


def _build_ticker_to_dart_map() -> dict[str, str]:
    mapping: dict[str, str] = {}
    with connect() as conn:
        rows = conn.execute(
            """
            SELECT tm.ticker, dcc.dart_corp_code
            FROM ticker_master tm
            LEFT JOIN dart_company_code dcc ON tm.ticker = dcc.stock_code
            """
        ).fetchall()
    for row in rows:
        ticker = str(row["ticker"] or "").strip().upper()
        code = str(row["dart_corp_code"] or "").strip()
        if ticker and code:
            mapping[ticker] = code
    return mapping


def _normalize_kr_metrics(rows: list[dict]) -> dict[tuple[str, str], dict]:
    normalized: dict[tuple[str, str], dict] = {}
    for row in rows:
        report_code = str(row.get("report_code") or "11011").strip() or "11011"
        business_year = str(row.get("business_year") or "").strip()
        account_name = str(row.get("account_name") or "").strip()
        amount = row.get("amount")
        metric_key = KR_ACCOUNT_NAME_MAP.get(account_name)
        if not metric_key or not business_year:
            continue
        key = (business_year, report_code)
        if key not in normalized:
            normalized[key] = {
                "revenue": None, "operating_income": None, "net_income": None,
                "total_assets": None, "total_liabilities": None, "total_equity": None,
            }
        normalized[key][metric_key] = None if amount is None else float(amount)
    return normalized


def _compute_kr_derived(metrics: dict) -> None:
    """Compute margin/ratio fields from raw KR metrics."""
    rev = metrics.get("revenue")
    oi = metrics.get("operating_income")
    ni = metrics.get("net_income")
    ta = metrics.get("total_assets")
    tl = metrics.get("total_liabilities")
    te = metrics.get("total_equity")
    if rev and rev > 0:
        if oi is not None:
            metrics["operating_margin"] = oi / rev * 100.0
        if ni is not None:
            metrics["net_margin"] = ni / rev * 100.0
    if te and te > 0 and ni is not None:
        metrics["roe"] = ni / te * 100.0
    if ta and ta > 0 and ni is not None:
        metrics["roa"] = ni / ta * 100.0
    if ta and ta > 0 and tl is not None:
        metrics["debt_ratio"] = tl / ta * 100.0


# ---------------------------------------------------------------------------
# Sync KR
# ---------------------------------------------------------------------------


def sync_kr(
    year: int,
    quarterly: bool,
    kr_tickers: list[str] | None = None,
) -> dict:
    periods = ["annual"]
    if quarterly:
        periods += ["q3", "half", "q1"]

    # Sync DART company codes first
    corp_rows = fetch_dart_company_codes()
    print(f"[sync_kr] dart_company_codes_fetched={len(corp_rows)}")
    corp_ok = corp_err = 0
    for row in corp_rows:
        try:
            upsert_dart_company(row)
            corp_ok += 1
        except Exception as exc:
            corp_err += 1
            print(f"  dart_company_upsert_failed[{row.get('dart_corp_code')}]: {exc}")

    ticker_to_dart = _build_ticker_to_dart_map()
    print(f"[sync_kr] ticker_mapped={len(ticker_to_dart)}")

    with connect() as conn:
        all_tickers = [
            str(r["ticker"]).strip().upper()
            for r in conn.execute("SELECT ticker FROM ticker_master ORDER BY ticker").fetchall()
        ]

    if kr_tickers:
        target_tickers = [t.strip().upper() for t in kr_tickers]
    else:
        target_tickers = all_tickers

    processed = skipped = stmt_ok = metric_ok = 0

    for ticker in target_tickers:
        dart_code = ticker_to_dart.get(ticker)
        if not dart_code:
            skipped += 1
            continue

        for period in periods:
            try:
                financial_rows = fetch_financials(dart_code, year, report_type=period)
            except Exception as exc:
                print(f"  fetch_failed[{ticker}][{period}][{year}]: {exc}")
                continue

            processed += 1
            period_label = period

            for fin in financial_rows:
                try:
                    upsert_financial_statement({
                        "ticker": ticker,
                        "business_year": fin.get("business_year") or str(year),
                        "report_code": fin.get("report_code") or DART_REPORT_CODES.get(period, "11011"),
                        "account_name": fin.get("account_name"),
                        "amount": fin.get("amount"),
                    })
                    stmt_ok += 1
                except Exception as exc:
                    print(f"  stmt_upsert_failed[{ticker}]: {exc}")

            metric_map = _normalize_kr_metrics(financial_rows)
            for (business_year, report_code), metric in metric_map.items():
                _compute_kr_derived(metric)
                try:
                    upsert_financial_metric({
                        "ticker": ticker,
                        "business_year": business_year,
                        "report_code": report_code,
                        "period_type": period_label,
                        "currency": "KRW",
                        **metric,
                    })
                    metric_ok += 1
                except Exception as exc:
                    print(f"  metric_upsert_failed[{ticker}][{business_year}]: {exc}")

    print(
        f"[sync_kr] done year={year} periods={periods} "
        f"processed={processed} skipped={skipped} "
        f"stmt_ok={stmt_ok} metric_ok={metric_ok}"
    )
    return {"processed": processed, "skipped": skipped, "stmt_ok": stmt_ok, "metric_ok": metric_ok}


# ---------------------------------------------------------------------------
# Sync US
# ---------------------------------------------------------------------------


def sync_us(us_tickers: list[str] | None = None) -> dict:
    tickers = us_tickers or DEFAULT_US_TICKERS
    tickers = [t.strip().upper() for t in tickers]
    print(f"[sync_us] fetching financials for {len(tickers)} tickers")

    all_data = fetch_multiple_us_financials(tickers, annual_periods=4, quarterly_periods=4)

    metric_ok = metric_err = 0
    for ticker, periods_data in all_data.items():
        for period_type, rows in periods_data.items():
            for row in rows:
                period_date = row.get("period_date")
                if not period_date:
                    continue
                # Use period_date (e.g. "2024-12-31") as business_year key
                # Use period_type as report_code for UNIQUE constraint
                try:
                    upsert_financial_metric({
                        "ticker": ticker,
                        "business_year": period_date[:7],   # "2024-12"
                        "report_code": period_type,         # "annual" | "quarterly"
                        "period_type": period_type,
                        "currency": "USD",
                        "revenue": row.get("revenue"),
                        "gross_profit": row.get("gross_profit"),
                        "operating_income": row.get("operating_income"),
                        "net_income": row.get("net_income"),
                        "total_assets": row.get("total_assets"),
                        "total_liabilities": row.get("total_liabilities"),
                        "total_equity": row.get("total_equity"),
                        "shares_outstanding": row.get("shares_outstanding"),
                        "eps_basic": row.get("eps_basic"),
                        "eps_diluted": row.get("eps_diluted"),
                        "cash_and_equivalents": row.get("cash_and_equivalents"),
                        "total_debt": row.get("total_debt"),
                        "operating_cashflow": row.get("operating_cashflow"),
                        "capital_expenditure": row.get("capital_expenditure"),
                        "free_cashflow": row.get("free_cashflow"),
                        "gross_margin": row.get("gross_margin"),
                        "operating_margin": row.get("operating_margin"),
                        "net_margin": row.get("net_margin"),
                        "roe": row.get("roe"),
                        "roa": row.get("roa"),
                        "debt_ratio": row.get("debt_ratio"),
                    })
                    metric_ok += 1
                except Exception as exc:
                    metric_err += 1
                    print(f"  us_metric_upsert_failed[{ticker}][{period_date}]: {exc}")

    print(f"[sync_us] done metric_ok={metric_ok} metric_err={metric_err}")
    return {"metric_ok": metric_ok, "metric_err": metric_err}


# ---------------------------------------------------------------------------
# Display / show
# ---------------------------------------------------------------------------


def _fmt(v: float | None, unit: str = "", decimals: int = 1) -> str:
    if v is None:
        return "N/A"
    if unit == "%":
        return f"{v:.{decimals}f}%"
    if unit == "억" and abs(v) >= 1e8:
        return f"{v/1e8:,.0f}억"
    if unit == "$B":
        return f"${v/1e9:.2f}B"
    return f"{v:,.{decimals}f}"


def show_financials(ticker: str) -> None:
    ticker = ticker.strip().upper()
    rows = get_financial_metrics(ticker, limit=8)
    if not rows:
        print(f"[show] No financial data for {ticker}. Run sync first.")
        return

    cur = rows[0].get("currency", "?")
    unit = "억" if cur == "KRW" else "$B"
    scale = 1 if cur == "KRW" else 1e9  # already in 원/달러

    print(f"\n=== {ticker} 재무성과 ({cur}) ===")
    print(f"{'PERIOD':<14} {'TYPE':<10} {'매출':>10} {'영업이익':>10} {'순이익':>10} {'영업이익률':>10} {'ROE':>8} {'ROA':>8} {'부채비율':>10}")
    print("-" * 100)
    for r in rows:
        period = f"{r.get('business_year','?')}"
        ptype = r.get("period_type") or r.get("report_code") or "?"
        rev = _fmt(r.get("revenue"), unit) if cur == "KRW" else _fmt(r.get("revenue"), "$B")
        oi = _fmt(r.get("operating_income"), unit) if cur == "KRW" else _fmt(r.get("operating_income"), "$B")
        ni = _fmt(r.get("net_income"), unit) if cur == "KRW" else _fmt(r.get("net_income"), "$B")
        om = _fmt(r.get("operating_margin"), "%")
        roe = _fmt(r.get("roe"), "%")
        roa = _fmt(r.get("roa"), "%")
        dr = _fmt(r.get("debt_ratio"), "%")
        print(f"{period:<14} {ptype:<10} {rev:>10} {oi:>10} {ni:>10} {om:>10} {roe:>8} {roa:>8} {dr:>10}")

    # EPS / FCF if available
    eps_row = next((r for r in rows if r.get("eps_diluted") is not None), None)
    fcf_row = next((r for r in rows if r.get("free_cashflow") is not None), None)
    if eps_row:
        print(f"\nEPS (최신): Basic={_fmt(eps_row.get('eps_basic'))}  Diluted={_fmt(eps_row.get('eps_diluted'))}")
    if fcf_row:
        fcf_val = _fmt(fcf_row.get("free_cashflow"), unit) if cur == "KRW" else _fmt(fcf_row.get("free_cashflow"), "$B")
        print(f"FCF (최신): {fcf_val}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Sync financial statements (KR + US)")
    parser.add_argument("--year", type=int, default=None, help="KR business year (e.g. 2024)")
    parser.add_argument("--quarterly", action="store_true", help="Include KR quarterly reports (1Q/2Q/3Q)")
    parser.add_argument("--kr-tickers", nargs="+", metavar="TICKER", help="Sync specific KR tickers only")
    parser.add_argument("--us", action="store_true", help="Sync US stock financials (yfinance)")
    parser.add_argument("--us-tickers", nargs="+", metavar="TICKER", help="Specific US tickers")
    parser.add_argument("--show", metavar="TICKER", help="Show stored financials for a ticker and exit")
    return parser.parse_args()


def main() -> None:
    args = _parse_args()

    if args.show:
        show_financials(args.show)
        return

    if args.year:
        sync_kr(year=args.year, quarterly=args.quarterly, kr_tickers=args.kr_tickers)

    if args.us or args.us_tickers:
        sync_us(us_tickers=args.us_tickers)

    if not args.year and not args.us and not args.us_tickers:
        print("Usage: sync_financials.py --year 2024 [--quarterly] [--us] [--show TICKER]")
        print("Run with --help for full options.")


if __name__ == "__main__":
    main()
