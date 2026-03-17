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
from datetime import datetime, timedelta, timezone
from math import log1p
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
    news_date: str
    total_collected: int
    topic_counts: List[tuple[str, int]]
    top_articles: List[TopicDigestArticle]
    sector_hot_topics: List[dict[str, object]]


SOURCE_WEIGHT_BY_KEYWORD: Dict[str, float] = {
    "reuters": 1.6,
    "bloomberg": 1.5,
    "wsj": 1.4,
    "ft": 1.4,
    "연합뉴스": 1.3,
    "매일경제": 1.2,
    "한국경제": 1.2,
    "서울경제": 1.1,
    "조선일보": 1.0,
    "중앙일보": 1.0,
    "동아일보": 1.0,
    "뉴시스": 0.9,
    "머니투데이": 0.9,
    "이데일리": 0.9,
}

IMPACT_KEYWORDS: Dict[str, float] = {
    "fomc": 1.6,
    "연준": 1.6,
    "금리": 1.3,
    "기준금리": 1.4,
    "국채": 1.2,
    "cpi": 1.3,
    "pce": 1.3,
    "인플레이션": 1.2,
    "gdp": 1.2,
    "실업률": 1.2,
    "중동": 1.1,
    "전쟁": 1.4,
    "제재": 1.2,
    "관세": 1.1,
    "환율": 1.2,
    "달러": 1.1,
    "vix": 1.1,
    "신용 스프레드": 1.2,
    "반도체": 1.0,
    "ai": 0.9,
    "엔비디아": 0.9,
}


TOPIC_TO_SECTOR: Dict[str, str] = {
    "국내지수": "지수/시장",
    "미국지수": "지수/시장",
    "환율/달러": "매크로",
    "금리/연준": "매크로",
    "인플레이션": "매크로",
    "경기/성장": "매크로",
    "변동성/리스크": "리스크",
    "반도체/AI": "IT/반도체",
    "2차전지/전기차": "2차전지/자동차",
    "바이오/헬스케어": "헬스케어",
    "에너지/원자재": "에너지/소재",
    "중국/신흥국": "글로벌",
    "정책/테마": "정책/테마",
}


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


def fetch_google_news_items(
    query: str = "KOSPI",
    limit: int = 20,
    timeout: int = 7,
) -> List[tuple[str, str, datetime | None]]:
    """Fetch news titles + links from Google News RSS.

    Returns a list of (title, link, published_at_utc) up to ``limit``.
    """
    q = quote(query)
    url = f"https://news.google.com/rss/search?q={q}"
    response = requests.get(url, timeout=timeout, headers=_default_headers())
    if response.status_code != 200:
        raise RuntimeError(f"http_status_{response.status_code}")

    root = ET.fromstring(response.text)
    items: List[tuple[str, str, datetime | None]] = []
    for item in root.findall(".//item"):
        title_el = item.find("title")
        link_el = item.find("link")
        pub_date_el = item.find("pubDate")
        title = (title_el.text or "").strip() if title_el is not None else ""
        link = (link_el.text or "").strip() if link_el is not None else ""
        pub_date_raw = (pub_date_el.text or "").strip() if pub_date_el is not None else ""
        published_at = _parse_rss_pub_date(pub_date_raw)
        if title:
            items.append((title, link, published_at))
        if len(items) >= limit:
            break
    return items


def _parse_rss_pub_date(pub_date: str) -> datetime | None:
    if not pub_date:
        return None
    try:
        dt = datetime.strptime(pub_date, "%a, %d %b %Y %H:%M:%S %Z")
    except ValueError:
        try:
            dt = datetime.strptime(pub_date, "%a, %d %b %Y %H:%M:%S %z")
        except ValueError:
            return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _is_same_day_in_kst(dt: datetime | None, now_utc: datetime) -> bool:
    if dt is None:
        return False
    kst = timezone(timedelta(hours=9))
    return dt.astimezone(kst).date() == now_utc.astimezone(kst).date()


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
        fetched = fetch_google_news_items(query=query, limit=max(limit * 2, 50))
        items = _deduplicate_news_items([(title, link) for title, link, _ in fetched], limit=limit)
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
    fallback_pool: List[tuple[str, str, str]] = []
    now_utc = datetime.now(timezone.utc)
    for topic, queries in topic_queries.items():
        for query in queries:
            try:
                items = fetch_google_news_items(query=query, limit=per_query_limit, timeout=timeout)
            except Exception:
                continue
            for title, link, published_at in items:
                fallback_pool.append((title, link, topic))
                if not _is_same_day_in_kst(published_at, now_utc):
                    continue
                pool.append((title, link, topic))

    if not pool:
        pool = fallback_pool
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

    topic_counter = Counter(topic for _, _, topic in deduped)
    scored_pool = _score_news_pool(deduped)
    topic_scores = _topic_quality_scores(scored_pool)
    ranked_topics = sorted(topic_scores.items(), key=lambda item: item[1], reverse=True)
    top_topics = [(topic, topic_counter.get(topic, 0)) for topic, _ in ranked_topics[:top_n]]

    top_articles: List[TopicDigestArticle] = []
    for topic, count in top_topics:
        topic_candidates = [item for item in scored_pool if item[2] == topic]
        if not topic_candidates:
            continue
        title, link, _, _ = sorted(topic_candidates, key=lambda item: item[3], reverse=True)[0]
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
        news_date=datetime.now(timezone.utc).astimezone(timezone(timedelta(hours=9))).date().isoformat(),
        total_collected=len(deduped),
        topic_counts=top_topics,
        top_articles=top_articles,
        sector_hot_topics=_build_sector_hot_topics(top_topics, top_articles),
    )
    return digest, None


def _build_sector_hot_topics(
    top_topics: List[tuple[str, int]],
    top_articles: List[TopicDigestArticle],
) -> List[dict[str, object]]:
    article_by_topic = {item.topic: item for item in top_articles}
    sector_map: Dict[str, List[dict[str, object]]] = {}
    for topic, count in top_topics:
        sector = TOPIC_TO_SECTOR.get(topic, "기타")
        article = article_by_topic.get(topic)
        sector_map.setdefault(sector, []).append(
            {
                "topic": topic,
                "count": count,
                "title": article.title if article else "",
                "link": article.link if article else "",
            }
        )

    ranked: List[dict[str, object]] = []
    for sector, topics in sorted(
        sector_map.items(),
        key=lambda item: sum(int(t.get("count", 0)) for t in item[1]),
        reverse=True,
    ):
        ranked.append(
            {
                "sector": sector,
                "total_count": sum(int(t.get("count", 0)) for t in topics),
                "topics": sorted(topics, key=lambda item: int(item.get("count", 0)), reverse=True),
            }
        )
    return ranked


def _score_news_pool(pool: List[tuple[str, str, str]]) -> List[tuple[str, str, str, float]]:
    """Score articles by source quality, impact keywords, and outlet diversity."""
    outlet_counter = Counter(_extract_outlet(title, link) for title, link, _ in pool)
    scored: List[tuple[str, str, str, float]] = []
    for title, link, topic in pool:
        outlet = _extract_outlet(title, link)
        source_score = _source_score(outlet)
        impact_score = _impact_score(title)
        duplicate_penalty = max(0, outlet_counter[outlet] - 1) * 0.08
        score = 1.0 + source_score + impact_score - duplicate_penalty
        scored.append((title, link, topic, round(score, 4)))
    return scored


def _topic_quality_scores(scored_pool: List[tuple[str, str, str, float]]) -> Dict[str, float]:
    """Aggregate topic quality score from article scores and breadth."""
    topic_to_scores: Dict[str, List[float]] = {}
    for _, _, topic, score in scored_pool:
        topic_to_scores.setdefault(topic, []).append(score)

    quality: Dict[str, float] = {}
    for topic, scores in topic_to_scores.items():
        scores_desc = sorted(scores, reverse=True)
        top_mean = sum(scores_desc[:3]) / max(1, min(3, len(scores_desc)))
        breadth_bonus = log1p(len(scores_desc)) * 0.25
        quality[topic] = round(top_mean + breadth_bonus, 4)
    return quality


def _extract_outlet(title: str, link: str) -> str:
    """Extract outlet name from title suffix or fallback to URL domain."""
    if " - " in title:
        tail = title.rsplit(" - ", 1)[-1].strip().lower()
        if tail:
            return tail
    m = re.search(r"https?://([^/]+)/?", link or "", flags=re.IGNORECASE)
    if m:
        return m.group(1).lower()
    return "unknown"


def _source_score(outlet: str) -> float:
    """Return outlet reliability weight."""
    if not outlet:
        return 0.0
    score = 0.0
    for keyword, weight in SOURCE_WEIGHT_BY_KEYWORD.items():
        if keyword in outlet:
            score = max(score, weight)
    return score


def _impact_score(title: str) -> float:
    """Return macro/market impact score from headline keywords."""
    text = (title or "").lower()
    score = 0.0
    for keyword, weight in IMPACT_KEYWORDS.items():
        if keyword in text:
            score += weight
    # Cap to avoid one headline with many overlapping keywords dominating.
    return min(score, 3.0)
