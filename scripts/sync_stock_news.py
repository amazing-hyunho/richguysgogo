from __future__ import annotations

"""Collect per-ticker news for the AI stock-analysis watchlist and store in DB.

Usage:
    python scripts/sync_stock_news.py                # all watchlist stocks
    python scripts/sync_stock_news.py --limit 20     # up to 20 articles/stock
    python scripts/sync_stock_news.py --ticker NVDA  # one ticker only
    python scripts/sync_stock_news.py --dry-run      # collect but do not write
"""

import argparse
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from committee.core.database import safe_upsert_stock_news
from committee.core.stock_watchlist import get_stocks
from committee.tools.stock_news import fetch_stock_news


def main() -> None:
    parser = argparse.ArgumentParser(description="AI 종목분석 워치리스트 뉴스 수집")
    parser.add_argument("--limit", type=int, default=15, help="종목당 저장할 최대 기사 수")
    parser.add_argument("--ticker", default=None, help="특정 티커만 수집 (예: NVDA)")
    parser.add_argument("--dry-run", action="store_true", help="수집만 하고 DB 저장 생략")
    args = parser.parse_args()

    stocks = get_stocks()
    if args.ticker:
        want = args.ticker.strip().upper()
        stocks = [s for s in stocks if str(s.get("ticker", "")).strip().upper() == want]
        if not stocks:
            print(f"[stock_news] ticker not in watchlist: {want}")
            return

    total_saved = 0
    for stock in stocks:
        ticker = str(stock.get("ticker", "")).strip()
        name = str(stock.get("name", "")).strip()
        market = str(stock.get("market", "")).strip()
        items = fetch_stock_news(ticker=ticker, name=name, market=market, limit=args.limit)
        print(f"[stock_news] {ticker} ({name}/{market}): collected {len(items)} articles")
        if args.dry_run:
            for it in items[:5]:
                print(f"    - {it.title[:70]}")
            continue
        for it in items:
            safe_upsert_stock_news(
                ticker=it.ticker,
                link=it.link,
                title=it.title,
                published_at=it.published_at,
                source=it.source,
                company_name=it.company_name,
                market=it.market,
            )
            total_saved += 1

    if args.dry_run:
        print("[stock_news] dry-run complete (no DB writes)")
    else:
        print(f"[stock_news] done: upserted {total_saved} articles for {len(stocks)} stocks")


if __name__ == "__main__":
    main()
