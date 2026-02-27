from __future__ import annotations

"""Utilities for fetching news articles and building 3-line summaries.

This module is intentionally dependency-light (requests + stdlib only) so it can
run in the current batch pipeline environment.
"""

import html
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from typing import List, Tuple
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


def summarize_article(link: str, timeout: int = 7) -> List[str]:
    """Fetch article HTML and summarize into 3 lines."""
    if not link:
        return ["기사 링크가 없습니다.", "본문 수집 실패.", "RSS 제목만 참고하세요."]
    try:
        response = requests.get(link, timeout=timeout, headers=_default_headers(), allow_redirects=True)
        if response.status_code != 200:
            return [f"본문 요청 실패(status={response.status_code}).", "핵심 요약 불가.", "원문 링크를 직접 확인하세요."]
        plain = _strip_html_to_text(response.text)
        return _summarize_to_three_lines(plain)
    except Exception as exc:  # noqa: BLE001
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
                    summary_lines=summarize_article(link),
                )
            )
        return titles, digest, None
    except Exception as exc:  # noqa: BLE001
        return [], [], str(exc)
