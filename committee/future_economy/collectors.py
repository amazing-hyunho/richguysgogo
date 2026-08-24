from __future__ import annotations

"""Source-backed evidence adapters for the 미래 경제 연구소 weekly run.

The adapters do not make investment decisions.  They turn existing industry
news, objective cycle signals, a small curated analogue registry, and optional
Google News RSS policy headlines into the common evidence contract.
"""

from datetime import date, datetime, timedelta, timezone
import hashlib
from pathlib import Path
import re
import sqlite3
from typing import Any, Callable, Mapping

from committee.tools.news_digest import _canonical_link, fetch_google_news_items


POLICY_TERMS = (
    "정부", "정책", "법안", "예산", "보조금", "세액공제", "관세", "수출 규제", "수출규제",
    "규제", "금지", "허가", "인허가", "행정명령", "국방비", "조달", "산업전략",
    "government", "policy", "bill", "budget", "subsidy", "tax credit", "tariff",
    "export control", "regulation", "procurement",
)
CORPORATE_TERMS = (
    "수주", "계약", "공급사", "공급계약", "증설", "설비투자", "투자", "협력", "파트너십",
    "출시", "상용화", "양산", "가동", "생산", "판매", "승인", "임상", "인상", "감산",
    "중단", "취소", "리콜", "실패", "지연", "하향", "둔화", "수주잔고",
    "order", "contract", "supplier", "capacity", "capex", "investment", "partnership",
    "launch", "commercial", "production", "approval", "trial", "backlog", "guidance",
    "cut", "cancel", "recall", "failure", "delay", "slowdown",
)
POSITIVE_TERMS = (
    "수주", "계약", "공급사", "증설", "설비투자", "투자", "협력", "파트너십", "출시", "상용화",
    "양산", "승인", "인상", "확대", "지원", "보조금", "세액공제", "예산 증액",
    "order", "contract", "supplier", "capacity expansion", "investment", "partnership",
    "launch", "commercial", "approval", "subsidy", "tax credit",
)
NEGATIVE_TERMS = (
    "감산", "중단", "취소", "리콜", "실패", "지연", "하향", "둔화", "금지", "규제 강화",
    "예산 삭감", "관세", "수출 규제", "수출규제",
    "production cut", "cancel", "recall", "failure", "delay", "slowdown", "ban",
    "budget cut", "tariff", "export control",
)
BLOCKED_SOURCE_TERMS = (
    "naver blog", "네이버 블로그", "blog", "블로그", "youtube", "유튜브",
    "daara", "다아라", "중고", "인플루언서",
)
OFFICIAL_SOURCE_TERMS = (
    "정책브리핑", "정부", "부처", "위원회", "청", "go.kr", "gov.",
)
REPUTABLE_SOURCE_TERMS = (
    "reuters", "bloomberg", "연합뉴스", "한국경제", "매일경제", "서울경제",
    "머니투데이", "이데일리", "전자신문", "kbs", "sbs", "조선비즈", "chosunbiz",
)

KRX_SOURCE_URL = "https://data.krx.co.kr/contents/MDC/MAIN/main/index.cmd"
US_MARKET_SOURCE_URL = "https://finance.yahoo.com/"


def _contains(text: str, terms: tuple[str, ...] | list[str]) -> bool:
    lowered = text.casefold()
    return any(str(term).casefold() in lowered for term in terms if str(term).strip())


def _iso_date(value: object) -> str | None:
    text = str(value or "").strip()
    if not text:
        return None
    try:
        return date.fromisoformat(text[:10]).isoformat()
    except ValueError:
        return None


def _plus_days(value: str, days: int) -> str:
    return (date.fromisoformat(value) + timedelta(days=days)).isoformat()


def _evidence_id(prefix: str, domain_id: str, identity: str) -> str:
    digest = hashlib.sha256(identity.encode("utf-8")).hexdigest()[:16]
    return f"{prefix}:{domain_id}:{digest}"


def _headline_without_outlet(title: str) -> str:
    return re.sub(r"\s+-\s+[^-]+$", "", title.strip()).strip()


def _direction(title: str) -> str:
    if _contains(title, NEGATIVE_TERMS):
        return "negative"
    if _contains(title, POSITIVE_TERMS):
        return "positive"
    return "neutral"


def _source_profile(source: str) -> tuple[str, float] | None:
    lowered = source.casefold()
    if any(term.casefold() in lowered for term in BLOCKED_SOURCE_TERMS):
        return None
    if any(term.casefold() in lowered for term in OFFICIAL_SOURCE_TERMS):
        return "official_policy", 0.95
    if any(term.casefold() in lowered for term in REPUTABLE_SOURCE_TERMS):
        return "reputable_media", 0.76
    return "secondary_analysis", 0.58


def _domain_keywords(domain: Mapping[str, Any]) -> list[str]:
    explicit = [str(value).strip() for value in domain.get("evidence_keywords", []) if str(value).strip()]
    if explicit:
        return explicit
    name = str(domain.get("name") or "")
    return [part.strip() for part in re.split(r"[·/,&]", name) if len(part.strip()) >= 2]


def _mapped_industry_ids(domain: Mapping[str, Any]) -> list[str]:
    return [str(value).strip() for value in domain.get("industry_ids", []) if str(value).strip()]


def _read_industry_news(
    *, domain: Mapping[str, Any], as_of: str, db_path: Path, lookback_days: int
) -> list[dict[str, Any]]:
    if not db_path.exists():
        return []
    industry_ids = _mapped_industry_ids(domain)
    if not industry_ids:
        return []
    cutoff = (date.fromisoformat(as_of) - timedelta(days=max(1, lookback_days))).isoformat()
    placeholders = ",".join("?" for _ in industry_ids)
    conn: sqlite3.Connection | None = None
    try:
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        exists = conn.execute(
            "SELECT 1 FROM sqlite_master WHERE type='table' AND name='industry_news'"
        ).fetchone()
        if not exists:
            return []
        rows = conn.execute(
            f"""
            SELECT industry_id, link, title, source, published_at, collected_at
            FROM industry_news
            WHERE industry_id IN ({placeholders})
              AND substr(COALESCE(published_at, collected_at), 1, 10) BETWEEN ? AND ?
              AND substr(collected_at, 1, 10) <= ?
            ORDER BY COALESCE(published_at, collected_at) DESC
            LIMIT 160
            """,
            [*industry_ids, cutoff, as_of, as_of],
        ).fetchall()
        return [dict(row) for row in rows]
    except sqlite3.Error:
        return []
    finally:
        if conn is not None:
            conn.close()


def collect_stored_news_evidence(
    *, domain: Mapping[str, Any], as_of: str, db_path: Path, lookback_days: int = 45,
    limit_per_type: int = 2,
) -> list[dict[str, Any]]:
    """Classify stored industry headlines as policy or corporate evidence.

    One headline can supply only one evidence type. Policy takes precedence so
    a single underlying source cannot create artificial evidence diversity.
    """

    domain_id = str(domain.get("domain_id") or "").strip()
    keywords = _domain_keywords(domain)
    selected: dict[str, list[dict[str, Any]]] = {"policy": [], "corporate": []}
    seen_links: set[str] = set()
    for row in _read_industry_news(domain=domain, as_of=as_of, db_path=db_path, lookback_days=lookback_days):
        title = str(row.get("title") or "").strip()
        link = _canonical_link(str(row.get("link") or ""))
        source_name = str(row.get("source") or "Google News RSS")
        source_profile = _source_profile(source_name)
        if (
            not title or not link or link in seen_links or not _contains(title, keywords)
            or source_profile is None
        ):
            continue
        evidence_type = "policy" if _contains(title, POLICY_TERMS) else (
            "corporate" if _contains(title, CORPORATE_TERMS) else ""
        )
        if not evidence_type or len(selected[evidence_type]) >= limit_per_type:
            continue
        event_date = _iso_date(row.get("published_at")) or _iso_date(row.get("collected_at"))
        known_at = _iso_date(row.get("collected_at"))
        if not event_date or not known_at or event_date > as_of or known_at > as_of:
            continue
        seen_links.add(link)
        clean_title = _headline_without_outlet(title)
        selected[evidence_type].append({
            "evidence_id": _evidence_id(evidence_type, domain_id, link),
            "evidence_type": evidence_type,
            "title": clean_title,
            "claim": f"수집된 헤드라인에서 확인된 {'정책' if evidence_type == 'policy' else '기업 행동'} 사건: {clean_title}",
            "event_date": event_date,
            "known_at": known_at,
            "valid_until": _plus_days(event_date, 90 if evidence_type == "policy" else 60),
            "source_url": link,
            "source_name": source_name,
            "source_kind": source_profile[0],
            "source_reliability": source_profile[1],
            "direction": _direction(title),
            "strength": 0.58 if evidence_type == "policy" else 0.55,
            "limitation": "기사 본문이 아닌 수집된 헤드라인 수준의 사건 확인이며 세부 수치와 맥락은 원문 재확인이 필요합니다.",
            "tags": [domain_id, str(row.get("industry_id") or ""), "stored_industry_news"],
        })
    return [*selected["policy"], *selected["corporate"]]


def collect_live_policy_evidence(
    *, domain: Mapping[str, Any], as_of: str, limit: int = 2,
    fetcher: Callable[..., list[tuple[str, str, datetime | None]]] = fetch_google_news_items,
) -> list[dict[str, Any]]:
    """Fill policy-news gaps with same-day Google News RSS results.

    Historical reruns never call this collector because information collected
    today was not known at an earlier ``as_of`` date.
    """

    if as_of != date.today().isoformat():
        return []
    domain_id = str(domain.get("domain_id") or "").strip()
    keywords = _domain_keywords(domain)
    if not domain_id or not keywords:
        return []
    query_terms = " OR ".join(f'"{term}"' for term in keywords[:8])
    policy_terms = " OR ".join(f'"{term}"' for term in POLICY_TERMS[:12])
    query = f"({query_terms}) ({policy_terms})"
    results: list[dict[str, Any]] = []
    seen_links: set[str] = set()
    for title, raw_link, published_at in fetcher(query=query, limit=max(20, limit * 8)):
        link = _canonical_link(raw_link)
        event_date = published_at.astimezone(timezone.utc).date().isoformat() if published_at else None
        if (
            not title or not link or link in seen_links or not event_date or event_date > as_of
            or not _contains(title, keywords) or not _contains(title, POLICY_TERMS)
        ):
            continue
        seen_links.add(link)
        clean_title = _headline_without_outlet(title)
        results.append({
            "evidence_id": _evidence_id("policy", domain_id, link),
            "evidence_type": "policy",
            "title": clean_title,
            "claim": f"정책 RSS 헤드라인에서 확인된 산업 관련 사건: {clean_title}",
            "event_date": event_date,
            "known_at": as_of,
            "valid_until": _plus_days(event_date, 90),
            "source_url": link,
            "source_name": "Google News RSS",
            "source_kind": "reputable_media",
            "source_reliability": 0.68,
            "direction": _direction(title),
            "strength": 0.52,
            "limitation": "정책 보강용 RSS 헤드라인이며 시행 여부와 세부 조문은 연결된 원문·공식 발표로 재확인해야 합니다.",
            "tags": [domain_id, "live_policy_rss"],
        })
        if len(results) >= limit:
            break
    return results


def collect_market_evidence(
    *, domain: Mapping[str, Any], as_of: str, db_path: Path, model_version: str = "cycle_v2",
    limit: int = 2,
) -> list[dict[str, Any]]:
    """Convert existing objective industry-cycle rows into market evidence."""

    if not db_path.exists():
        return []
    domain_id = str(domain.get("domain_id") or "").strip()
    industry_ids = _mapped_industry_ids(domain)
    rows: list[dict[str, Any]] = []
    conn: sqlite3.Connection | None = None
    try:
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        exists = conn.execute(
            "SELECT 1 FROM sqlite_master WHERE type='table' AND name='industry_cycle_v2_signal'"
        ).fetchone()
        if not exists:
            return []
        for industry_id in industry_ids:
            row = conn.execute(
                """
                SELECT v.*, COALESCE(m.name_kr, v.industry_id) AS industry_name,
                       s.representative_market
                FROM industry_cycle_v2_signal v
                LEFT JOIN industry_master m ON m.industry_id = v.industry_id
                LEFT JOIN industry_cycle_signal s
                  ON s.industry_id = v.industry_id AND s.as_of = v.as_of
                 AND s.model_version = 'cycle_v1'
                WHERE v.industry_id = ? AND v.model_version = ? AND v.as_of <= ?
                ORDER BY v.as_of DESC LIMIT 1
                """,
                (industry_id, model_version, as_of),
            ).fetchone()
            if row is not None:
                rows.append(dict(row))
    except sqlite3.Error:
        return []
    finally:
        if conn is not None:
            conn.close()

    usable = [
        row for row in rows
        if row.get("market_confirmation_score") is not None
        and float(row.get("data_completeness") or 0.0) >= 0.75
    ]
    usable.sort(
        key=lambda row: (
            -abs(float(row.get("market_confirmation_score") or 50.0) - 50.0),
            str(row.get("industry_id") or ""),
        )
    )
    evidence: list[dict[str, Any]] = []
    for row in usable[:limit]:
        score = float(row["market_confirmation_score"])
        signal = str(row.get("entry_signal") or "")
        direction = "negative" if signal == "AVOID" or score <= 35.0 else (
            "positive" if signal in {"EARLY_ENTRY", "CONFIRM_ADD"} or score >= 65.0 else "neutral"
        )
        market = str(row.get("representative_market") or "KR")
        source_url = KRX_SOURCE_URL if market == "KR" else US_MARKET_SOURCE_URL
        industry_name = str(row.get("industry_name") or row.get("industry_id") or "산업")
        event_date = str(row.get("as_of") or as_of)
        evidence.append({
            "evidence_id": _evidence_id("market", domain_id, f"{row.get('industry_id')}:{event_date}:{model_version}"),
            "evidence_type": "market",
            "title": f"{industry_name} 시장 확인 점수 {score:.1f}",
            "claim": f"프로젝트의 객관식 산업 사이클 계산에서 {industry_name}의 시장 확인 점수는 {score:.1f}, 상태는 {signal or '-'}입니다.",
            "event_date": event_date,
            "known_at": event_date,
            "valid_until": _plus_days(event_date, 14),
            "source_url": source_url,
            "source_name": "프로젝트 산업 사이클 DB",
            "source_kind": "secondary_analysis",
            "source_reliability": 0.65,
            "direction": direction,
            "strength": round(min(0.8, max(0.35, abs(score - 50.0) / 50.0)), 4),
            "limitation": "가격·상대강도·폭·실적 수정치를 합성한 내부 확인 점수이며 기대수익률이나 매수 추천이 아닙니다.",
            "tags": [domain_id, str(row.get("industry_id") or ""), model_version],
        })
    return evidence


def load_historical_analogue_evidence(
    *, domain_id: str, as_of: str, payload: Mapping[str, Any]
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    evidence: list[dict[str, Any]] = []
    analogues: list[dict[str, Any]] = []
    for row in payload.get("analogues", []):
        if not isinstance(row, Mapping) or domain_id not in row.get("domain_ids", []):
            continue
        known_at = _iso_date(row.get("known_at"))
        event_date = _iso_date(row.get("event_date"))
        if not known_at or not event_date or known_at > as_of or event_date > as_of:
            continue
        analogue_id = str(row.get("analogue_id") or "").strip()
        source_url = str(row.get("source_url") or "").strip()
        if not analogue_id or not source_url:
            continue
        evidence.append({
            "evidence_id": f"historical:{analogue_id}",
            "evidence_type": "historical_analogy",
            "title": str(row.get("title") or analogue_id),
            "claim": str(row.get("claim") or "검증된 과거 사례"),
            "event_date": event_date,
            "known_at": known_at,
            "source_url": source_url,
            "source_name": str(row.get("source_name") or "원문"),
            "source_kind": str(row.get("source_kind") or "academic_primary"),
            "direction": "neutral",
            "strength": float(row.get("strength") or 0.45),
            "limitation": str(row.get("limitation") or "과거 사례는 현재 결과를 보장하지 않습니다."),
            "tags": [domain_id, "historical_analogue"],
        })
        analogues.append({
            "analogue_id": analogue_id,
            "title": str(row.get("title") or analogue_id),
            "source_url": source_url,
            "similarities": list(row.get("similarities") or []),
            "differences": list(row.get("differences") or []),
            "reapplication_conditions": list(row.get("reapplication_conditions") or []),
        })
    return evidence, analogues
