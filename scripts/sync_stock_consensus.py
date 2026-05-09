"""
Analyst consensus batch sync script.

Usage
-----
# Sync default watchlist (defined in DEFAULT_TICKERS below):
    python scripts/sync_stock_consensus.py

# Sync specific tickers:
    python scripts/sync_stock_consensus.py --tickers AAPL MSFT 005930 035420

# Sync tickers already stored in DB (refresh mode):
    python scripts/sync_stock_consensus.py --from-db

# Dry-run (fetch but don't save):
    python scripts/sync_stock_consensus.py --dry-run

# Show stored consensus for a ticker:
    python scripts/sync_stock_consensus.py --show 005930

Design
------
- Stores today's date as the snapshot date (one row per ticker per day).
- Uses NULL-based data integrity — no 0.0 placeholders.
- Prints a structured summary table after sync.
"""

from __future__ import annotations

import argparse
import sys
from datetime import date as dt_date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from committee.core.database import (
    get_latest_stock_consensus,
    get_stock_consensus_history,
    list_consensus_tickers,
    safe_upsert_stock_consensus,
)
from committee.tools.stock_consensus_provider import fetch_multiple_consensus, fetch_stock_consensus

# ---------------------------------------------------------------------------
# Default watchlist
# ---------------------------------------------------------------------------

DEFAULT_KR_TICKERS = [
    "005930",  # 삼성전자
    "000660",  # SK하이닉스
    "035420",  # NAVER
    "035720",  # 카카오
    "051910",  # LG화학
    "006400",  # 삼성SDI
    "068270",  # 셀트리온
    "207940",  # 삼성바이오로직스
    "005490",  # POSCO홀딩스
    "000270",  # 기아
    "005380",  # 현대차
    "373220",  # LG에너지솔루션
]

DEFAULT_US_TICKERS = [
    "AAPL",
    "MSFT",
    "NVDA",
    "GOOGL",
    "AMZN",
    "META",
    "TSLA",
    "AVGO",
    "JPM",
    "V",
]

DEFAULT_TICKERS = DEFAULT_KR_TICKERS + DEFAULT_US_TICKERS


# ---------------------------------------------------------------------------
# Formatting helpers
# ---------------------------------------------------------------------------


def _fmt_price(value: float | None, currency: str | None = None) -> str:
    if value is None:
        return "N/A"
    cur = currency or ""
    if cur == "KRW":
        return f"{value:,.0f}원"
    if cur == "USD":
        return f"${value:,.2f}"
    return f"{value:,.2f}"


def _fmt_rec(key: str | None, mean: float | None) -> str:
    parts = []
    if key:
        parts.append(key)
    if mean is not None:
        # yfinance: 1.0=strong buy, 2.0=buy, 3.0=hold, 4.0=underperform, 5.0=sell
        label = {1: "STRONG BUY", 2: "BUY", 3: "HOLD", 4: "UNDERPERFORM", 5: "SELL"}.get(
            round(mean), f"{mean:.1f}"
        )
        parts.append(f"({label})")
    return " ".join(parts) if parts else "N/A"


def _print_summary(results: list[dict]) -> None:
    print(f"\n{'TICKER':<12} {'COMPANY':<22} {'MKT':<4} {'TARGET':>12} {'RANGE':>20} {'REC':<18} {'ANALYSTS':>9} {'FWD EPS':>10} {'SOURCE':<12}")
    print("-" * 120)
    for r in results:
        ticker = r.get("ticker", "?")
        company = (r.get("company_name") or "")[:20]
        market = r.get("market", "?")
        cur = r.get("currency")
        tp = _fmt_price(r.get("target_mean_price"), cur)
        tp_hi = _fmt_price(r.get("target_high_price"), cur)
        tp_lo = _fmt_price(r.get("target_low_price"), cur)
        price_range = f"{tp_lo} ~ {tp_hi}" if (r.get("target_high_price") or r.get("target_low_price")) else "N/A"
        rec = _fmt_rec(r.get("recommendation_key"), r.get("recommendation_mean"))
        analysts = str(r.get("num_analysts") or "N/A")
        fwd_eps = _fmt_price(r.get("forward_eps"), cur)
        source = r.get("source") or "N/A"
        print(
            f"{ticker:<12} {company:<22} {market:<4} {tp:>12} {price_range:>20} {rec:<18} {analysts:>9} {fwd_eps:>10} {source:<12}"
        )


def _print_history(ticker: str) -> None:
    rows = get_stock_consensus_history(ticker, n=10)
    if not rows:
        print(f"[show] No consensus data stored for {ticker}")
        return
    latest = rows[0]
    print(f"\n=== {ticker} ({latest.get('company_name', 'N/A')}) consensus history ===")
    print(f"{'DATE':<12} {'TARGET':>12} {'HIGH':>12} {'LOW':>12} {'REC':<18} {'ANALYSTS':>9} {'FWD EPS':>10}")
    print("-" * 90)
    for row in rows:
        cur = row.get("currency")
        print(
            f"{row['date']:<12} "
            f"{_fmt_price(row.get('target_mean_price'), cur):>12} "
            f"{_fmt_price(row.get('target_high_price'), cur):>12} "
            f"{_fmt_price(row.get('target_low_price'), cur):>12} "
            f"{_fmt_rec(row.get('recommendation_key'), row.get('recommendation_mean')):<18} "
            f"{str(row.get('num_analysts') or 'N/A'):>9} "
            f"{_fmt_price(row.get('forward_eps'), cur):>10}"
        )


# ---------------------------------------------------------------------------
# Main sync logic
# ---------------------------------------------------------------------------


def run_sync(tickers: list[str], today: str, dry_run: bool) -> list[dict]:
    print(f"[sync_consensus] fetching {len(tickers)} tickers for date={today}")
    results = fetch_multiple_consensus(tickers)

    saved = 0
    skipped = 0
    for result in results:
        ticker = result["ticker"]
        has_data = any(
            result.get(k) is not None
            for k in ("target_mean_price", "recommendation_key", "forward_eps")
        )
        if not has_data:
            print(f"  [{ticker}] no data fetched — storing NULL snapshot")

        if dry_run:
            skipped += 1
            continue

        safe_upsert_stock_consensus(
            ticker=ticker,
            date=today,
            market=result.get("market"),
            source=result.get("source"),
            company_name=result.get("company_name"),
            currency=result.get("currency"),
            current_price=result.get("current_price"),
            target_mean_price=result.get("target_mean_price"),
            target_high_price=result.get("target_high_price"),
            target_low_price=result.get("target_low_price"),
            recommendation_key=result.get("recommendation_key"),
            recommendation_mean=result.get("recommendation_mean"),
            num_analysts=result.get("num_analysts"),
            forward_eps=result.get("forward_eps"),
            forward_pe=result.get("forward_pe"),
            revenue_estimate_avg=result.get("revenue_estimate_avg"),
        )
        saved += 1

    action = "would save" if dry_run else "saved"
    print(f"\n[sync_consensus] {action} {saved + skipped}/{len(tickers)} rows for {today}")
    return results


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Sync analyst consensus data")
    parser.add_argument(
        "--tickers",
        nargs="+",
        metavar="TICKER",
        help="Specific tickers to sync (US: AAPL, KR: 005930)",
    )
    parser.add_argument(
        "--from-db",
        action="store_true",
        help="Refresh all tickers already in the stock_consensus DB table",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Fetch and display without saving to DB",
    )
    parser.add_argument(
        "--show",
        metavar="TICKER",
        help="Show stored consensus history for a ticker and exit",
    )
    parser.add_argument(
        "--date",
        default=None,
        help="Snapshot date (YYYY-MM-DD). Defaults to today.",
    )
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    today = args.date or dt_date.today().isoformat()

    if args.show:
        _print_history(args.show.strip().upper())
        return

    if args.from_db:
        stored = list_consensus_tickers()
        if not stored:
            print("[sync_consensus] No tickers stored in DB yet. Use --tickers to add some.")
            return
        tickers = stored
        print(f"[sync_consensus] refreshing {len(tickers)} tickers from DB")
    elif args.tickers:
        tickers = [t.strip().upper() for t in args.tickers]
    else:
        tickers = [t.strip().upper() for t in DEFAULT_TICKERS]
        print(f"[sync_consensus] using default watchlist ({len(tickers)} tickers)")

    results = run_sync(tickers, today=today, dry_run=args.dry_run)
    _print_summary(results)


if __name__ == "__main__":
    main()
