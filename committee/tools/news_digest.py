from __future__ import annotations

"""Utilities for fetching news articles and building 3-line summaries.

This module is intentionally dependency-light (requests + stdlib only) so it can
run in the current batch pipeline environment.
"""

import html
import re
import xml.etree.ElementTree as ET
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, List, Tuple
from urllib.parse import quote

import requests


def _default_headers() -> dict[str, str]:
    """Return common headers for HTTP requests."""
    return {
        "User-Agent": "DailyAIInvestmentCommittee/1.0",
        "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
    }


@dataclass(frozen=True)
class NewsDigestItem:
    """Summarized news item."""

    title: str
    link: str
    summary_lines: List[str]


@dataclass(frozen=True)
class TopicDigestArticle:
    """Top article per counted topic."""

    topic: str
    count: int
    title: str
    link: str
    summary_lines: List[str]


@dataclass(frozen=True)
class NewsTopicDigest:
    """Aggregated topic digest result for dashboard/reporting."""

    crawled_at: str
    total_collected: int
    topic_counts: List[tuple[str, int]]
    top_articles: List[TopicDigestArticle]


def recommended_topic_queries() -> Dict[str, List[str]]:
    """Recommended economy/market keywords grouped by topic."""
    return {
        "국내지수": ["코스피", "코스닥", "KOSPI", "KOSDAQ"],
        "미국지수": ["S&P 500", "NASDAQ", "Dow Jones", "미국 증시"],
        "환율/달러": ["달러 인덱스", "USD KRW", "환율", "달러 강세"],
        "금리/연준": ["FOMC", "연준 금리", "미국 국채 10년", "기준금리"],
        "인플레이션": ["CPI", "PCE", "인플레이션", "물가 상승률"],
        "경기/성장": ["세계경제", "경기침체", "GDP", "PMI"],
        "변동성/리스크": ["VIX", "시장 변동성", "리스크 오프", "신용 스프레드"],
        "반도체/AI": ["반도체", "엔비디아", "AI 투자", "메모리 업황"],
        "2차전지/전기차": ["2차전지", "전기차", "배터리", "리튬 가격"],
        "바이오/헬스케어": ["바이오", "헬스케어", "신약 승인", "의료기기"],
        "에너지/원자재": ["유가", "천연가스", "구리 가격", "원자재"],
        "중국/신흥국": ["중국 경제", "위안화", "신흥국 증시", "중국 부양책"],
        "정책/테마": ["정부 정책", "산업 정책", "수출 규제", "관세"],
    }


def fetch_google_news_items(query: str = "KOSPI", limit: int = 20, timeout: int = 7) -> List[tuple[str, str]]:
    """Fetch news titles + links from Google News RSS.

    Returns a list of (title, link) up to ``limit``.
    """
    q = quote(query)
    url = f"https://news.google.com/rss/search?q={q}"
    response = requests.get(url, timeout=timeout, headers=_default_headers())
    if response.status_code != 200:
        raise RuntimeError(f"http_status_{response.status_code}")

    root = ET.fromstring(response.text)
    items: List[tuple[str, str]] = []
    for item in root.findall(".//item"):
        title_el = item.find("title")
        link_el = item.find("link")
        title = (title_el.text or "").strip() if title_el is not None else ""
        link = (link_el.text or "").strip() if link_el is not None else ""
        if title:
            items.append((title, link))
        if len(items) >= limit:
            break
    return items


def _normalize_headline(title: str) -> str:
    """Normalize title text so near-duplicate headlines can be removed."""
    normalized = title or ""
    normalized = re.sub(r"\([^)]*\)$", "", normalized).strip()
    normalized = re.sub(r"\[[^\]]*\]", " ", normalized)
    normalized = re.sub(r"\s+-\s+[^-]+$", "", normalized)
    normalized = re.sub(r"[^\w\s]", " ", normalized)
    normalized = re.sub(r"\s+", " ", normalized).strip().lower()
    return normalized


def _deduplicate_news_items(items: List[tuple[str, str]], limit: int) -> List[tuple[str, str]]:
    """Drop duplicated/near-duplicated headlines while preserving original order."""
    unique: List[tuple[str, str]] = []
    seen: set[str] = set()
    seen_tokens: List[set[str]] = []

    for title, link in items:
        normalized = _normalize_headline(title)
        if not normalized or normalized in seen:
            continue

        current_tokens = set(normalized.split())
        is_duplicate = False
        for prior_tokens in seen_tokens:
            if not current_tokens or not prior_tokens:
                continue
            overlap = len(current_tokens & prior_tokens) / max(len(current_tokens), len(prior_tokens))
            if overlap >= 0.85:
                is_duplicate = True
                break

        if is_duplicate:
            continue

        seen.add(normalized)
        seen_tokens.append(current_tokens)
        unique.append((title, link))
        if len(unique) >= limit:
            break

    return unique


def _strip_html_to_text(raw_html: str) -> str:
    """Extract readable plain text from HTML."""
    text = re.sub(r"<script[\s\S]*?</script>", " ", raw_html, flags=re.IGNORECASE)
    text = re.sub(r"<style[\s\S]*?</style>", " ", text, flags=re.IGNORECASE)
    text = re.sub(r"<[^>]+>", " ", text)
    text = html.unescape(text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _summarize_to_three_lines(text: str) -> List[str]:
    """Create a simple 3-line summary from article text."""
    if not text:
        return ["본문을 가져오지 못했습니다.", "핵심 내용 파악 불가.", "원문 링크를 확인하세요."]

    sentences = re.split(r"(?<=[.!?])\s+", text)
    cleaned = [s.strip() for s in sentences if len(s.strip()) >= 25]
    if not cleaned:
        cleaned = [text]

    lines = cleaned[:3]
    while len(lines) < 3:
        lines.append("추가 핵심 문장을 확보하지 못했습니다.")

    return [line[:180] for line in lines]


def _fallback_summary_from_title(title: str | None) -> List[str]:
    headline = (title or "").strip()
    if not headline:
        return ["제목 기반 요약을 생성하지 못했습니다.", "핵심 내용 파악 불가.", "원문 링크를 확인하세요."]
    return [
        f"핵심 이슈: {headline[:140]}",
        "시장 영향 가능성: 관련 자산/섹터 변동성 점검이 필요합니다.",
        "세부 근거와 수치는 원문 링크를 통해 확인하세요.",
    ]


def summarize_article(link: str, timeout: int = 7, title: str | None = None) -> List[str]:
    """Fetch article HTML and summarize into 3 lines."""
    if not link:
        return ["기사 링크가 없습니다.", "본문 수집 실패.", "RSS 제목만 참고하세요."]
    try:
        response = requests.get(link, timeout=timeout, headers=_default_headers(), allow_redirects=True)
        if response.status_code != 200:
            return _fallback_summary_from_title(title)
        plain = _strip_html_to_text(response.text)
        if "Google 뉴스" in plain or len(plain) < 120:
            return _fallback_summary_from_title(title)
        return _summarize_to_three_lines(plain)
    except Exception as exc:  # noqa: BLE001
        if str(exc):
            return _fallback_summary_from_title(title)
        return [f"본문 요청 예외: {exc}", "핵심 요약 불가.", "원문 링크를 직접 확인하세요."]


def build_news_digest(query: str = "KOSPI", limit: int = 20) -> Tuple[List[str], List[NewsDigestItem], str | None]:
    """Build title list and 3-line summaries for up to ``limit`` articles."""
    try:
        items = fetch_google_news_items(query=query, limit=max(limit * 2, 50))
        items = _deduplicate_news_items(items, limit=limit)
        if not items:
            return [], [], "no_titles"

        titles: List[str] = []
        digest: List[NewsDigestItem] = []
        for title, link in items[:limit]:
            titles.append(title)
            digest.append(
                NewsDigestItem(
                    title=title,
                    link=link,
                    summary_lines=summarize_article(link, title=title),
                )
            )
        return titles, digest, None
    except Exception as exc:  # noqa: BLE001
        return [], [], str(exc)


def build_topic_digest(
    target_total: int = 300,
    top_n: int = 5,
    timeout: int = 7,
    topic_queries: Dict[str, List[str]] | None = None,
) -> tuple[NewsTopicDigest | None, str | None]:
    """Collect ~target_total articles and return top-N topic digest."""
    topic_queries = topic_queries or recommended_topic_queries()
    if target_total < 50:
        target_total = 50
    if top_n < 1:
        top_n = 1

    query_count = sum(len(queries) for queries in topic_queries.values())
    per_query_limit = max(10, (target_total // max(query_count, 1)) + 3)

    pool: List[tuple[str, str, str]] = []
    for topic, queries in topic_queries.items():
        for query in queries:
            try:
                items = fetch_google_news_items(query=query, limit=per_query_limit, timeout=timeout)
            except Exception:
                continue
            for title, link in items:
                pool.append((title, link, topic))

    if not pool:
        return None, "no_news_pool"

    deduped: List[tuple[str, str, str]] = []
    seen: set[str] = set()
    for title, link, topic in pool:
        normalized = _normalize_headline(title)
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        deduped.append((title, link, topic))
        if len(deduped) >= target_total:
            break

    if not deduped:
        return None, "no_deduped_news"

    counter = Counter(topic for _, _, topic in deduped)
    top_topics = counter.most_common(top_n)
    top_articles: List[TopicDigestArticle] = []
    for topic, count in top_topics:
        candidate = next(((title, link) for title, link, t in deduped if t == topic), None)
        if candidate is None:
            continue
        title, link = candidate
        top_articles.append(
            TopicDigestArticle(
                topic=topic,
                count=count,
                title=title,
                link=link,
                summary_lines=summarize_article(link, timeout=timeout, title=title),
            )
        )

    digest = NewsTopicDigest(
        crawled_at=datetime.now(timezone.utc).isoformat(),
        total_collected=len(deduped),
        topic_counts=top_topics,
        top_articles=top_articles,
    )
    return digest, None
