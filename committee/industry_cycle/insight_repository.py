from __future__ import annotations

"""Persistence for industry news metadata and non-authoritative AI commentary."""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from committee.core.database import connect, init_db


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def upsert_industry_news(record: dict[str, Any], db_path: Path | None = None) -> None:
    for key in ("industry_id", "link", "title"):
        if not str(record.get(key) or "").strip():
            raise ValueError(f"industry_news missing required field '{key}'")
    init_db(db_path)
    with connect(db_path) as conn:
        conn.execute(
            """
            INSERT INTO industry_news (
                industry_id, link, title, source, published_at, query, collected_at
            ) VALUES (
                :industry_id, :link, :title, :source, :published_at, :query, :collected_at
            )
            ON CONFLICT(industry_id, link) DO UPDATE SET
                title=excluded.title,
                source=excluded.source,
                published_at=excluded.published_at,
                query=excluded.query,
                collected_at=excluded.collected_at;
            """,
            {
                "industry_id": str(record["industry_id"]).strip(),
                "link": str(record["link"]).strip(),
                "title": str(record["title"]).strip(),
                "source": record.get("source"),
                "published_at": record.get("published_at"),
                "query": record.get("query"),
                "collected_at": record.get("collected_at") or _now_iso(),
            },
        )


def list_industry_news(
    industry_id: str,
    *,
    published_since: str | None = None,
    limit: int = 20,
    db_path: Path | None = None,
) -> list[dict[str, Any]]:
    init_db(db_path)
    params: dict[str, Any] = {"industry_id": industry_id, "limit": max(1, int(limit))}
    since_clause = ""
    if published_since:
        since_clause = "AND COALESCE(published_at, collected_at) >= :published_since"
        params["published_since"] = published_since
    with connect(db_path) as conn:
        rows = conn.execute(
            f"""
            SELECT industry_id, link, title, source, published_at, query, collected_at
            FROM industry_news
            WHERE industry_id = :industry_id
              {since_clause}
            ORDER BY COALESCE(published_at, collected_at) DESC
            LIMIT :limit;
            """,
            params,
        ).fetchall()
        return [dict(row) for row in rows]


def upsert_industry_ai_opinion(record: dict[str, Any], db_path: Path | None = None) -> None:
    for key in ("industry_id", "as_of", "cycle_model_version"):
        if not str(record.get(key) or "").strip():
            raise ValueError(f"industry_ai_opinion missing required field '{key}'")
    init_db(db_path)
    with connect(db_path) as conn:
        conn.execute(
            """
            INSERT INTO industry_ai_opinion (
                industry_id, as_of, cycle_model_version, llm_model,
                opinion, news_assessment, catalysts_json, risks_json,
                cited_links_json, confidence, overall_summary,
                input_tokens, output_tokens, created_at
            ) VALUES (
                :industry_id, :as_of, :cycle_model_version, :llm_model,
                :opinion, :news_assessment, :catalysts_json, :risks_json,
                :cited_links_json, :confidence, :overall_summary,
                :input_tokens, :output_tokens, :created_at
            )
            ON CONFLICT(industry_id, as_of, cycle_model_version) DO UPDATE SET
                llm_model=excluded.llm_model,
                opinion=excluded.opinion,
                news_assessment=excluded.news_assessment,
                catalysts_json=excluded.catalysts_json,
                risks_json=excluded.risks_json,
                cited_links_json=excluded.cited_links_json,
                confidence=excluded.confidence,
                overall_summary=excluded.overall_summary,
                input_tokens=excluded.input_tokens,
                output_tokens=excluded.output_tokens,
                created_at=excluded.created_at;
            """,
            {
                "industry_id": record["industry_id"],
                "as_of": record["as_of"],
                "cycle_model_version": record["cycle_model_version"],
                "llm_model": record.get("llm_model"),
                "opinion": record.get("opinion"),
                "news_assessment": record.get("news_assessment"),
                "catalysts_json": json.dumps(record.get("catalysts") or [], ensure_ascii=False),
                "risks_json": json.dumps(record.get("risks") or [], ensure_ascii=False),
                "cited_links_json": json.dumps(record.get("cited_links") or [], ensure_ascii=False),
                "confidence": record.get("confidence"),
                "overall_summary": record.get("overall_summary"),
                "input_tokens": record.get("input_tokens"),
                "output_tokens": record.get("output_tokens"),
                "created_at": record.get("created_at") or _now_iso(),
            },
        )


def get_industry_ai_opinion(
    industry_id: str,
    as_of: str,
    cycle_model_version: str,
    db_path: Path | None = None,
) -> dict[str, Any] | None:
    init_db(db_path)
    with connect(db_path) as conn:
        row = conn.execute(
            """
            SELECT * FROM industry_ai_opinion
            WHERE industry_id = :industry_id
              AND as_of = :as_of
              AND cycle_model_version = :cycle_model_version;
            """,
            {
                "industry_id": industry_id,
                "as_of": as_of,
                "cycle_model_version": cycle_model_version,
            },
        ).fetchone()
    if row is None:
        return None
    result = dict(row)
    for json_key, output_key in (
        ("catalysts_json", "catalysts"),
        ("risks_json", "risks"),
        ("cited_links_json", "cited_links"),
    ):
        try:
            result[output_key] = json.loads(result.get(json_key) or "[]")
        except (TypeError, ValueError):
            result[output_key] = []
    return result


def get_latest_industry_ai_opinion(
    industry_id: str,
    cycle_model_version: str,
    db_path: Path | None = None,
) -> dict[str, Any] | None:
    init_db(db_path)
    with connect(db_path) as conn:
        row = conn.execute(
            """
            SELECT * FROM industry_ai_opinion
            WHERE industry_id = :industry_id
              AND cycle_model_version = :cycle_model_version
            ORDER BY as_of DESC
            LIMIT 1;
            """,
            {"industry_id": industry_id, "cycle_model_version": cycle_model_version},
        ).fetchone()
    if row is None:
        return None
    result = dict(row)
    for json_key, output_key in (
        ("catalysts_json", "catalysts"),
        ("risks_json", "risks"),
        ("cited_links_json", "cited_links"),
    ):
        try:
            result[output_key] = json.loads(result.get(json_key) or "[]")
        except (TypeError, ValueError):
            result[output_key] = []
    return result
