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

_CYCLE_EVENT_TERMS = (
    "수요",
    "주문",
    "신규주문",
    "판매",
    "출하",
    "증설",
    "감산",
    "생산중단",
    "가동률",
    "CAPEX",
    "설비투자",
    "ASP",
    "마진",
    "스프레드",
    "재고",
    "수주",
    "수주잔고",
    "계약",
    "가이던스",
    "규제",
    "demand",
    "orders",
    "shipments",
    "capacity expansion",
    "production cut",
    "utilization",
    "capital expenditure",
    "margin",
    "inventory",
    "backlog",
    "guidance",
)

_NOISE_EXCLUSIONS = ("관련주", "테마주", "급등", "상한가", "목표주가")


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
    configured = industry.get("news_keywords")
    configured_keywords = [
        str(term).strip()
        for term in (configured if isinstance(configured, list) else [])
        if str(term).strip()
    ]
    keywords = [name_kr]
    if name_en:
        keywords.append(name_en)
    keywords.extend(configured_keywords)
    keywords = list(dict.fromkeys(term for term in keywords if term))

    def quoted(term: str) -> str:
        return '"' + term.replace('"', "") + '"'

    industry_terms = " OR ".join(quoted(term) for term in keywords)
    event_terms = " OR ".join(quoted(term) for term in _CYCLE_EVENT_TERMS)
    exclusions = " ".join(f"-{term}" for term in _NOISE_EXCLUSIONS)
    return f"({industry_terms}) ({event_terms}) {exclusions}"


def build_industry_news_fallback_query(industry: dict[str, object]) -> str:
    """Shorter query used when a detailed Google News RSS search returns nothing."""
    name_kr = str(industry.get("name_kr") or industry.get("industry_id") or "").strip()
    name_en = str(industry.get("name_en") or "").strip()
    names = [f'"{name_kr}"']
    if name_en:
        names.append(f'"{name_en}"')
    events = ("수주", "주문", "출하", "생산", "가격", "실적", "업황", "CAPEX", "demand", "orders", "sales")
    exclusions = " ".join(f"-{term}" for term in _NOISE_EXCLUSIONS)
    return f"({' OR '.join(names)}) ({' OR '.join(events)}) {exclusions}"


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

    def normalize(
        raw_items: list[tuple[str, str, datetime | None]], source_query: str
    ) -> list[IndustryNewsItem]:
        result: list[IndustryNewsItem] = []
        seen_links: set[str] = set()
        normalized_titles: list[str] = []
        for title, link, published_at in raw_items:
            if published_at is not None:
                published_utc = published_at.astimezone(timezone.utc)
                if published_utc < cutoff or published_utc > now_utc:
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
                    query=source_query,
                )
            )
            if len(result) >= limit:
                break
        return result

    result = normalize(fetcher(query=query, limit=max(limit * 3, 20)), query)
    if result:
        return result
    fallback_query = build_industry_news_fallback_query(industry)
    return normalize(
        fetcher(query=fallback_query, limit=max(limit * 3, 20)),
        fallback_query,
    )


def collect_and_store_industry_news(
    industries: list[dict[str, object]],
    *,
    lookback_days: int = 14,
    limit_per_industry: int = 8,
    dry_run: bool = True,
    now: datetime | None = None,
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
                now=now,
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
