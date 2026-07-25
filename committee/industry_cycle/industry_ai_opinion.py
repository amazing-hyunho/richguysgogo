from __future__ import annotations

"""One-call, cross-industry LLM commentary grounded in scores and recent news.

The output is commentary only.  Nothing in this module writes to or mutates
``industry_cycle_signal``.
"""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from committee.industry_cycle import insight_repository
from committee.tools.openai_chat import OpenAIConfig, chat_completion


ALLOWED_CONFIDENCE = {"낮음", "보통", "높음"}


@dataclass(frozen=True)
class IndustryOpinionBatch:
    overall_summary: str
    opinions: list[dict[str, Any]]


def _compact_signal(item: dict[str, Any]) -> dict[str, Any]:
    signal = item.get("latest_signal") or {}
    keys = (
        "cycle_score", "confirmed_state", "confirmation_status", "consecutive_weeks",
        "confidence", "data_completeness", "fundamentals_score",
        "earnings_revision_score", "breadth_score", "relative_strength_score",
        "trend_score", "overheat_score", "risk_score", "flow_score",
        "macro_fit_score", "urgent_flags",
    )
    return {
        "industry_id": item.get("industry_id"),
        "name_kr": item.get("name_kr"),
        "signal": {key: signal.get(key) for key in keys},
        "news": [
            {
                "title": news.get("title"),
                "source": news.get("source"),
                "published_at": news.get("published_at"),
                "link": news.get("link"),
            }
            for news in (item.get("news") or [])[:8]
        ],
    }


def build_prompts(industries: list[dict[str, Any]]) -> tuple[str, str]:
    system = (
        "당신은 산업 사이클 리서치 심사위원이다. 입력된 정량 데이터와 뉴스만 사용한다. "
        "정량 점수·국면·추천을 수정하거나 새로운 숫자를 만들지 않는다. 뉴스는 추천 등급을 "
        "변경하지 않고 근거 강화, 정책 리스크, 공급 충격, 수요 변화의 보조 해석에만 사용한다. "
        "급등 그 자체를 업황 개선의 근거로 취급하지 않는다. 동일 사건을 여러 기사가 보도해도 "
        "하나의 사건으로 본다. 데이터가 부족하면 반드시 데이터 부족이라고 쓴다. "
        "반드시 JSON 객체만 출력한다."
    )
    payload = [_compact_signal(item) for item in industries]
    user = (
        "아래 전체 산업을 서로 비교해 주간 AI 종합의견을 작성하라. 산업별 의견은 2~4문장으로 "
        "작성하고, 정량 판정과 뉴스가 충돌하면 충돌을 명시하라. 인용 링크는 해당 산업 입력에 "
        "포함된 링크만 사용하라.\n\n"
        "출력 스키마:\n"
        '{"overall_summary":"전체 산업 3~5문장 요약",'
        '"industries":[{"industry_id":"입력 ID","opinion":"정량·뉴스 종합의견",'
        '"news_assessment":"뉴스가 정량 근거를 강화/약화/중립 중 어떻게 보조하는지",'
        '"catalysts":["최대 3개"],"risks":["최대 3개"],'
        '"cited_links":["입력에 있는 URL만 최대 4개"],'
        '"confidence":"낮음|보통|높음"}]}\n\n'
        f"산업 데이터:\n{json.dumps(payload, ensure_ascii=False, separators=(',', ':'))}"
    )
    return system, user


def validate_opinion_payload(raw: str | dict[str, Any], industries: list[dict[str, Any]]) -> IndustryOpinionBatch:
    parsed = json.loads(raw) if isinstance(raw, str) else raw
    if not isinstance(parsed, dict):
        raise ValueError("industry_ai_response_not_object")
    overall = str(parsed.get("overall_summary") or "").strip()
    rows = parsed.get("industries")
    if not overall or not isinstance(rows, list):
        raise ValueError("industry_ai_response_missing_fields")

    expected_ids = {str(item["industry_id"]) for item in industries}
    links_by_id = {
        str(item["industry_id"]): {
            str(news.get("link")) for news in (item.get("news") or []) if news.get("link")
        }
        for item in industries
    }
    validated: list[dict[str, Any]] = []
    seen: set[str] = set()
    for row in rows:
        if not isinstance(row, dict):
            continue
        industry_id = str(row.get("industry_id") or "")
        if industry_id not in expected_ids or industry_id in seen:
            continue
        opinion = str(row.get("opinion") or "").strip()
        if not opinion:
            continue
        cited = [str(link) for link in row.get("cited_links", []) if str(link) in links_by_id[industry_id]][:4]
        confidence = str(row.get("confidence") or "낮음")
        if confidence not in ALLOWED_CONFIDENCE:
            confidence = "낮음"
        validated.append(
            {
                "industry_id": industry_id,
                "opinion": opinion[:1200],
                "news_assessment": str(row.get("news_assessment") or "")[:600],
                "catalysts": [str(v)[:200] for v in (row.get("catalysts") or [])[:3]],
                "risks": [str(v)[:200] for v in (row.get("risks") or [])[:3]],
                "cited_links": cited,
                "confidence": confidence,
            }
        )
        seen.add(industry_id)
    if seen != expected_ids:
        missing = sorted(expected_ids - seen)
        raise ValueError(f"industry_ai_response_missing_industries:{','.join(missing)}")
    return IndustryOpinionBatch(overall_summary=overall[:2000], opinions=validated)


def generate_industry_opinions(
    industries: list[dict[str, Any]],
    *,
    config: OpenAIConfig,
    model: str,
    llm_call: Callable[..., str] = chat_completion,
) -> IndustryOpinionBatch:
    system, user = build_prompts(industries)
    raw = llm_call(
        config=config,
        model=model,
        system_prompt=system,
        user_prompt=user,
        temperature=0.1,
        timeout=90,
    )
    return validate_opinion_payload(raw, industries)


def store_industry_opinions(
    batch: IndustryOpinionBatch,
    *,
    as_of: str,
    cycle_model_version: str,
    llm_model: str,
    db_path: Path | None = None,
) -> int:
    for opinion in batch.opinions:
        insight_repository.upsert_industry_ai_opinion(
            {
                **opinion,
                "as_of": as_of,
                "cycle_model_version": cycle_model_version,
                "llm_model": llm_model,
                "overall_summary": batch.overall_summary,
            },
            db_path=db_path,
        )
    return len(batch.opinions)

