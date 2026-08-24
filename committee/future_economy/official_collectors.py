from __future__ import annotations

"""First-party government and regulatory evidence for 미래 경제 연구소."""

from datetime import date, timedelta
import hashlib
from pathlib import Path
import re
import sqlite3
from typing import Any, Callable, Mapping

import requests


FEDERAL_REGISTER_API_URL = "https://www.federalregister.gov/api/v1/documents.json"
DART_VIEWER_URL = "https://dart.fss.or.kr/dsaf001/main.do?rcpNo="

_POSITIVE_TERMS = (
    "investment", "funding", "grant", "approval", "award", "support", "expansion",
    "투자", "지원", "승인", "수주", "계약", "공급", "증설", "합병",
)
_NEGATIVE_TERMS = (
    "ban", "prohibit", "restriction", "suspension", "termination", "recall", "penalty",
    "sanction", "tariff", "export control",
    "중단", "해지", "취소", "회수", "부도", "영업정지", "소송",
)
_DART_MATERIAL_TERMS = (
    "단일판매", "공급계약", "신규시설투자", "시설투자", "영업양수", "영업양도",
    "기술이전", "임상시험", "품목허가", "영업정지", "회생절차", "부도발생",
)
_FEDERAL_REGISTER_BLOCK_TERMS = (
    "proposed collection", "information collection", "comment request", "privacy act",
    "notice of meeting", "meeting notice",
)


def _contains(text: str, terms: list[str] | tuple[str, ...]) -> bool:
    lowered = text.casefold()
    for raw_term in terms:
        term = str(raw_term).strip().casefold()
        if not term:
            continue
        if len(term) <= 3 and term.isascii() and term.replace("-", "").isalnum():
            if re.search(rf"(?<![a-z0-9]){re.escape(term)}(?![a-z0-9])", lowered):
                return True
        elif term in lowered:
            return True
    return False


def _direction(text: str) -> str:
    if _contains(text, _NEGATIVE_TERMS):
        return "negative"
    if _contains(text, _POSITIVE_TERMS):
        return "positive"
    return "neutral"


def _plus_days(value: str, days: int) -> str:
    return (date.fromisoformat(value) + timedelta(days=days)).isoformat()


def _domain_keywords(domain: Mapping[str, Any]) -> list[str]:
    return [
        str(value).strip()
        for value in domain.get("evidence_keywords", [])
        if len(str(value).strip()) >= 2
    ]


def fetch_federal_register_documents(
    *,
    as_of: str,
    lookback_days: int = 21,
    limit: int = 100,
    requester: Callable[..., Any] = requests.get,
) -> list[dict[str, Any]]:
    """Fetch a bounded recent window from the official Federal Register API."""

    end = date.fromisoformat(as_of)
    start = end - timedelta(days=max(1, lookback_days) - 1)
    response = requester(
        FEDERAL_REGISTER_API_URL,
        params={
            "conditions[publication_date][gte]": start.isoformat(),
            "conditions[publication_date][lte]": end.isoformat(),
            "order": "newest",
            "per_page": min(100, max(1, limit)),
        },
        headers={"User-Agent": "richguysgogo-future-economy/1.0"},
        timeout=25,
    )
    response.raise_for_status()
    payload = response.json() or {}
    rows = payload.get("results") if isinstance(payload, Mapping) else None
    return [dict(row) for row in rows if isinstance(row, Mapping)] if isinstance(rows, list) else []


def collect_official_policy_api_evidence(
    *,
    domain: Mapping[str, Any],
    as_of: str,
    documents: list[Mapping[str, Any]],
    limit: int = 2,
) -> list[dict[str, Any]]:
    """Map first-party regulatory documents to a configured research domain."""

    keywords = _domain_keywords(domain)
    if not keywords:
        return []
    evidence: list[dict[str, Any]] = []
    seen: set[str] = set()
    for row in documents:
        title = str(row.get("title") or "").strip()
        abstract = str(row.get("abstract") or "").strip()
        publication_date = str(row.get("publication_date") or "")[:10]
        document_number = str(row.get("document_number") or "").strip()
        source_url = str(row.get("html_url") or row.get("pdf_url") or "").strip()
        agencies = row.get("agencies") if isinstance(row.get("agencies"), list) else []
        agency_names = [
            str(agency.get("name") or "").strip()
            for agency in agencies
            if isinstance(agency, Mapping) and str(agency.get("name") or "").strip()
        ]
        searchable = " ".join([title, abstract, *agency_names])
        if (
            not title or not document_number or not source_url or document_number in seen
            or not _contains(searchable, keywords)
            or _contains(searchable, _FEDERAL_REGISTER_BLOCK_TERMS)
        ):
            continue
        try:
            event_date = date.fromisoformat(publication_date).isoformat()
        except ValueError:
            continue
        if event_date > as_of:
            continue
        seen.add(document_number)
        evidence.append({
            "evidence_id": f"federal-register:{document_number}",
            "evidence_type": "policy",
            "title": title,
            "claim": f"미국 연방정부가 {title} 문서를 공식 게재했습니다.",
            "event_date": event_date,
            "known_at": event_date,
            "valid_until": _plus_days(event_date, 120),
            "source_url": source_url,
            "source_name": "Federal Register" + (f" · {', '.join(agency_names[:2])}" if agency_names else ""),
            "source_kind": "official_policy",
            "source_reliability": 1.0,
            "direction": _direction(searchable),
            "strength": 0.72,
            "limitation": "공식 규정·고시의 존재를 확인한 근거이며 시행 효과와 한국 산업 전달 강도는 별도 검증이 필요합니다.",
            "tags": [str(domain.get("domain_id") or ""), "federal_register", "first_party_policy"],
        })
        if len(evidence) >= limit:
            break
    return evidence


def _mapped_korean_tickers(
    *, domain: Mapping[str, Any], as_of: str, db_path: Path
) -> dict[str, dict[str, str]]:
    raw_industry_ids = (
        domain.get("dart_industry_ids", [])
        if "dart_industry_ids" in domain
        else domain.get("industry_ids", [])
    )
    industry_ids = [str(value).strip() for value in raw_industry_ids if str(value).strip()]
    if not db_path.exists() or not industry_ids:
        return {}
    placeholders = ",".join("?" for _ in industry_ids)
    conn: sqlite3.Connection | None = None
    try:
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            f"""
            SELECT DISTINCT iam.asset_id AS stock_code, iam.industry_id,
                            COALESCE(tm.company_name, iam.asset_id) AS company_name
            FROM industry_asset_map iam
            LEFT JOIN ticker_master tm ON tm.ticker = iam.asset_id AND tm.market = 'KR'
            WHERE iam.asset_type = 'STOCK' AND iam.market = 'KR'
              AND iam.industry_id IN ({placeholders})
              AND iam.valid_from <= ?
              AND (iam.valid_to IS NULL OR iam.valid_to >= ?)
              AND iam.weight >= 0.30
            """,
            [*industry_ids, as_of, as_of],
        ).fetchall()
        return {
            str(row["stock_code"]): {
                "company_name": str(row["company_name"]),
                "industry_id": str(row["industry_id"]),
            }
            for row in rows
            if str(row["stock_code"] or "").strip()
        }
    except sqlite3.Error:
        return {}
    finally:
        if conn is not None:
            conn.close()


def collect_dart_disclosure_evidence(
    *,
    domain: Mapping[str, Any],
    as_of: str,
    db_path: Path,
    disclosures: list[Mapping[str, Any]],
    limit: int = 2,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Attach material DART filings only to mapped Korean industry assets."""

    mapped = _mapped_korean_tickers(domain=domain, as_of=as_of, db_path=db_path)
    if not mapped:
        return [], []
    evidence: list[dict[str, Any]] = []
    companies: list[dict[str, Any]] = []
    seen: set[str] = set()
    for row in disclosures:
        stock_code = str(row.get("stock_code") or "").strip()
        report_name = str(row.get("report_name") or "").strip()
        receipt_no = str(row.get("receipt_no") or "").strip()
        receipt_date = str(row.get("receipt_date") or "")[:10]
        if (
            stock_code not in mapped or not report_name or not receipt_no or receipt_no in seen
            or not _contains(report_name, _DART_MATERIAL_TERMS)
        ):
            continue
        try:
            event_date = date.fromisoformat(receipt_date).isoformat()
        except ValueError:
            continue
        if event_date > as_of:
            continue
        seen.add(receipt_no)
        company_name = str(row.get("company_name") or mapped[stock_code]["company_name"])
        source_url = f"{DART_VIEWER_URL}{receipt_no}"
        evidence.append({
            "evidence_id": f"dart:{receipt_no}",
            "evidence_type": "corporate",
            "title": f"{company_name} · {report_name}",
            "claim": f"{company_name}가 DART에 {report_name} 공시를 제출했습니다.",
            "event_date": event_date,
            "known_at": event_date,
            "valid_until": _plus_days(event_date, 90),
            "source_url": source_url,
            "source_name": "금융감독원 DART",
            "source_kind": "regulatory_filing",
            "source_reliability": 1.0,
            "direction": _direction(report_name),
            "strength": 0.76,
            "limitation": "공시 제출 사실을 확인한 근거이며 계약 규모·실적 기여·사업 지속성은 공시 본문과 후속 실적으로 재검증해야 합니다.",
            "tags": [str(domain.get("domain_id") or ""), mapped[stock_code]["industry_id"], stock_code, "dart"],
        })
        companies.append({
            "company_name": company_name,
            "stock_code": stock_code,
            "connection_reason": report_name,
            "source_url": source_url,
        })
        if len(evidence) >= limit:
            break
    return evidence, companies
