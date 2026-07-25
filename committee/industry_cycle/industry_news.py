from __future__ import annotations

"""Best-effort industry news collection using the project's Google News RSS client."""

import re
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Callable

from committee.industry_cycle import insight_repository
from committee.tools.news_digest import (
    _canonical_link,
    _headline_similar,
    _normalize_headline,
    fetch_google_news_items,
)


@dataclass(frozen=True)
class IndustryNewsItem:
    industry_id: str
    title: str
    link: str
    source: str
    published_at: str | None
    query: str


def build_industry_news_query(industry: dict[str, object]) -> str:
    name_kr = str(industry.get("name_kr") or industry.get("industry_id") or "").strip()
    name_en = str(industry.get("name_en") or "").strip()
    terms = [f'"{name_kr}" 산업']
    if name_en:
        terms.append(f'"{name_en}" industry')
    return f"({' OR '.join(terms)}) (업황 OR 수요 OR 공급 OR 실적 OR 정책 OR outlook)"


def _source_from_title(title: str) -> str:
    parts = re.split(r"\s+-\s+", title.strip())
    return parts[-1].strip() if len(parts) > 1 else ""


def collect_industry_news(
    industry: dict[str, object],
    *,
    lookback_days: int = 14,
    limit: int = 8,
    now: datetime | None = None,
    fetcher: Callable[..., list[tuple[str, str, datetime | None]]] = fetch_google_news_items,
) -> list[IndustryNewsItem]:
    industry_id = str(industry.get("industry_id") or "").strip()
    if not industry_id:
        raise ValueError("industry_id is required")
    query = build_industry_news_query(industry)
    now_utc = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    cutoff = now_utc - timedelta(days=max(1, lookback_days))
    raw = fetcher(query=query, limit=max(limit * 3, 20))

    result: list[IndustryNewsItem] = []
    seen_links: set[str] = set()
    normalized_titles: list[str] = []
    for title, link, published_at in raw:
        if published_at is not None and published_at.astimezone(timezone.utc) < cutoff:
            continue
        canonical = _canonical_link(link)
        normalized = _normalize_headline(title)
        if not canonical or not normalized or canonical in seen_links:
            continue
        if any(_headline_similar(normalized, prior) for prior in normalized_titles):
            continue
        seen_links.add(canonical)
        normalized_titles.append(normalized)
        result.append(
            IndustryNewsItem(
                industry_id=industry_id,
                title=title.strip(),
                link=canonical,
                source=_source_from_title(title),
                published_at=published_at.astimezone(timezone.utc).isoformat() if published_at else None,
                query=query,
            )
        )
        if len(result) >= limit:
            break
    return result


def collect_and_store_industry_news(
    industries: list[dict[str, object]],
    *,
    lookback_days: int = 14,
    limit_per_industry: int = 8,
    dry_run: bool = True,
    db_path: Path | None = None,
    fetcher: Callable[..., list[tuple[str, str, datetime | None]]] = fetch_google_news_items,
) -> dict[str, object]:
    counts: dict[str, int] = {}
    errors: dict[str, str] = {}
    collected: dict[str, list[IndustryNewsItem]] = {}
    for industry in industries:
        industry_id = str(industry.get("industry_id") or "")
        try:
            items = collect_industry_news(
                industry,
                lookback_days=lookback_days,
                limit=limit_per_industry,
                fetcher=fetcher,
            )
            collected[industry_id] = items
            counts[industry_id] = len(items)
            if not dry_run:
                for item in items:
                    insight_repository.upsert_industry_news(item.__dict__, db_path=db_path)
        except Exception as exc:
            errors[industry_id] = str(exc)
            collected[industry_id] = []
            counts[industry_id] = 0
    return {"counts": counts, "errors": errors, "collected": collected}

