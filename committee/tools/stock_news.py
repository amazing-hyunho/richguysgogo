from __future__ import annotations

"""Per-ticker news collection for the AI stock-analysis tab.

This module reuses the market-news plumbing in ``news_digest`` (Google News RSS
fetch + dedup helpers) but scopes queries to a single stock so the result can be
stored per ticker in the ``stock_news`` table.
"""

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import List

from committee.tools.news_digest import (
    fetch_google_news_items,
    _canonical_link,
    _headline_similar,
    _normalize_headline,
)


@dataclass(frozen=True)
class StockNewsItem:
    """One collected news article scoped to a ticker."""

    ticker: str
    title: str
    link: str
    published_at: str | None
    source: str
    company_name: str
    market: str


def _build_queries(name: str, ticker: str, market: str) -> List[str]:
    """Build search queries for a stock.

    KR uses the Korean company name; US adds the symbol + ``stock`` to avoid
    unrelated same-name matches.
    """
    name = (name or "").strip()
    ticker = (ticker or "").strip()
    market = (market or "").strip().upper()
    queries: List[str] = []
    if market == "US":
        if name:
            queries.append(name)
        if ticker:
            queries.append(f"{ticker} stock")
    else:
        if name:
            queries.append(name)
        if ticker:
            queries.append(ticker)
    # Preserve order, drop blanks/dups.
    seen: set[str] = set()
    out: List[str] = []
    for q in queries:
        if q and q not in seen:
            seen.add(q)
            out.append(q)
    return out


def _extract_source(title: str, link: str) -> str:
    """Extract the outlet name from a Google News title suffix (" - Outlet")."""
    if " - " in title:
        tail = title.rsplit(" - ", 1)[-1].strip()
        if tail:
            return tail
    return ""


def fetch_stock_news(
    ticker: str,
    name: str,
    market: str,
    limit: int = 15,
    timeout: int = 7,
) -> List[StockNewsItem]:
    """Fetch and dedup recent news for one stock.

    Returns up to ``limit`` deduplicated articles (newest first by RSS order).
    """
    queries = _build_queries(name=name, ticker=ticker, market=market)
    if not queries:
        return []

    raw: List[tuple[str, str, datetime | None]] = []
    per_query = max(8, limit)
    for query in queries:
        try:
            raw.extend(fetch_google_news_items(query=query, limit=per_query, timeout=timeout))
        except Exception:
            continue

    deduped: List[StockNewsItem] = []
    seen_links: set[str] = set()
    seen_titles: List[str] = []
    for title, link, published_at in raw:
        normalized = _normalize_headline(title)
        canonical = _canonical_link(link)
        if not normalized:
            continue
        if canonical and canonical in seen_links:
            continue
        if any(_headline_similar(normalized, prior) for prior in seen_titles):
            continue
        seen_titles.append(normalized)
        if canonical:
            seen_links.add(canonical)
        deduped.append(
            StockNewsItem(
                ticker=ticker.strip().upper(),
                title=title,
                link=link,
                published_at=published_at.isoformat() if published_at else None,
                source=_extract_source(title, link),
                company_name=name,
                market=(market or "").strip().upper(),
            )
        )
        if len(deduped) >= limit:
            break
    return deduped
