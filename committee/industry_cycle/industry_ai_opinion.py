from __future__ import annotations

"""Batched cross-industry LLM commentary grounded in scores and recent news.

The output is commentary only.  Nothing in this module writes to or mutates
``industry_cycle_signal``.
"""

import json
import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from committee.industry_cycle import insight_repository
from committee.tools.openai_chat import (
    ChatCompletionResult,
    OpenAIConfig,
    chat_completion_with_metadata,
)


ALLOWED_CONFIDENCE = {"낮음", "보통", "높음"}
ALLOWED_INVESTMENT_VIEWS = {"우호", "중립", "주의", "데이터 부족"}
PROMPT_VERSION = "industry_weekly_v2"
BATCHED_PROMPT_VERSION = "industry_weekly_v3_batched"


@dataclass(frozen=True)
class IndustryOpinionBatch:
    overall_summary: str
    opinions: list[dict[str, Any]]
    prompt_version: str = PROMPT_VERSION
    input_hash: str | None = None
    input_tokens: int | None = None
    output_tokens: int | None = None


@dataclass(frozen=True)
class BatchedIndustryOpinionResult:
    batch: IndustryOpinionBatch
    failed_industry_ids: tuple[str, ...]
    errors: dict[str, str]
    chunk_count: int
    retry_count: int


def _compact_previous_signal(signal: dict[str, Any]) -> dict[str, Any] | None:
    previous = signal.get("previous_signal")
    if not isinstance(previous, dict):
        return None
    return {
        key: previous.get(key)
        for key in (
            "as_of", "cycle_score", "raw_state", "confirmed_state",
            "confirmation_status", "confidence", "data_completeness",
        )
    }


def _delta(current: Any, previous: Any) -> float | None:
    if not isinstance(current, (int, float)) or not isinstance(previous, (int, float)):
        return None
    return round(float(current) - float(previous), 4)


def _compact_signal(item: dict[str, Any]) -> dict[str, Any]:
    signal = item.get("latest_signal") or {}
    previous = _compact_previous_signal(item)
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
        "previous_signal": previous,
        "weekly_change": {
            "cycle_score_delta": _delta(
                signal.get("cycle_score"), previous.get("cycle_score") if previous else None
            ),
            "confidence_delta": _delta(
                signal.get("confidence"), previous.get("confidence") if previous else None
            ),
            "state_changed": (
                None
                if previous is None
                else signal.get("confirmed_state") != previous.get("confirmed_state")
            ),
        },
        "top_reasons": [
            {
                "component_key": reason.get("component_key"),
                "raw_value": reason.get("raw_value"),
                "contribution": reason.get("contribution"),
                "direction": reason.get("direction"),
                "note": reason.get("note"),
            }
            for reason in (item.get("signal_reasons") or [])[:6]
        ],
        "top_candidates": [
            {
                "asset_id": candidate.get("asset_id"),
                "asset_type": candidate.get("asset_type"),
                "market": candidate.get("market"),
                "score": candidate.get("score"),
                "rank": candidate.get("rank"),
            }
            for candidate in (item.get("candidates") or [])[:3]
        ],
        "portfolio": item.get("portfolio") or {"status": "NONE", "weekly_events": []},
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
        "모델의 사전학습 지식은 산업의 장기 구조, 일반적인 수익 동인, 거시 변수의 통상적 전달 "
        "경로처럼 시점에 의존하지 않는 배경 설명에만 사용할 수 있다. 사전학습 지식으로 최근 "
        "사건, 현재 정책, 기업 실적, 가격, 시장 점유율을 주장하지 말고 현재 판단의 증거로 "
        "사용하지 않는다. 이 일반론은 structural_context에만 분리해 쓴다. "
        "급등 그 자체를 업황 개선의 근거로 취급하지 않는다. 동일 사건을 여러 기사가 보도해도 "
        "하나의 사건으로 본다. 데이터가 부족하면 반드시 데이터 부족이라고 쓴다. 직접적인 "
        "매수·매도 지시, 목표가, 수익률 예측, 투자 비중은 제시하지 않는다. "
        "반드시 JSON 객체만 출력한다."
    )
    payload = [_compact_signal(item) for item in industries]
    user = (
        "아래 입력 산업을 서로 비교해 주간 AI 종합의견을 작성하라. 산업별 의견은 2~4문장으로 "
        "작성하고, 정량 판정과 뉴스가 충돌하면 충돌을 명시하라. 인용 링크는 해당 산업 입력에 "
        "포함된 링크만 사용하라.\n\n"
        "출력 스키마:\n"
        '{"overall_summary":"전체 산업 3~5문장 요약",'
        '"industries":[{"industry_id":"입력 ID","investment_view":"우호|중립|주의|데이터 부족",'
        '"opinion":"현재 입력 근거에 한정한 조건부 투자 관점",'
        '"weekly_change":"전주 대비 핵심 변화. 전주 데이터가 없으면 최초 관측",'
        '"structural_context":"사전학습 기반 시점 비의존 산업 일반론 1~2문장. 현재 사실 근거 아님",'
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
    signals_by_id = {
        str(item["industry_id"]): (item.get("latest_signal") or {})
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
        investment_view = str(row.get("investment_view") or "데이터 부족")
        if investment_view not in ALLOWED_INVESTMENT_VIEWS:
            investment_view = "데이터 부족"
        cited = [str(link) for link in row.get("cited_links", []) if str(link) in links_by_id[industry_id]][:4]
        confidence = str(row.get("confidence") or "낮음")
        if confidence not in ALLOWED_CONFIDENCE:
            confidence = "낮음"
        source_signal = signals_by_id[industry_id]
        signal_confidence = source_signal.get("confidence")
        data_completeness = source_signal.get("data_completeness")
        if (
            isinstance(signal_confidence, (int, float)) and signal_confidence < 0.35
        ) or (
            isinstance(data_completeness, (int, float)) and data_completeness < 0.5
        ):
            confidence = "낮음"
        elif (
            isinstance(signal_confidence, (int, float))
            and signal_confidence < 0.7
            and confidence == "높음"
        ):
            confidence = "보통"
        validated.append(
            {
                "industry_id": industry_id,
                "investment_view": investment_view,
                "opinion": opinion[:1200],
                "weekly_change": str(row.get("weekly_change") or "")[:600],
                "structural_context": str(row.get("structural_context") or "")[:800],
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
    llm_call: Callable[..., str | ChatCompletionResult] = chat_completion_with_metadata,
) -> IndustryOpinionBatch:
    system, user = build_prompts(industries)
    raw_result = llm_call(
        config=config,
        model=model,
        system_prompt=system,
        user_prompt=user,
        temperature=0.1,
        timeout=90,
    )
    if isinstance(raw_result, ChatCompletionResult):
        raw = raw_result.content
        input_tokens = raw_result.input_tokens
        output_tokens = raw_result.output_tokens
    else:
        raw = raw_result
        input_tokens = None
        output_tokens = None
    validated = validate_opinion_payload(raw, industries)
    return IndustryOpinionBatch(
        overall_summary=validated.overall_summary,
        opinions=validated.opinions,
        prompt_version=PROMPT_VERSION,
        input_hash=hashlib.sha256(user.encode("utf-8")).hexdigest(),
        input_tokens=input_tokens,
        output_tokens=output_tokens,
    )


def _sum_optional(values: list[int | None]) -> int | None:
    present = [value for value in values if value is not None]
    return sum(present) if present else None


def generate_industry_opinions_batched(
    industries: list[dict[str, Any]],
    *,
    config: OpenAIConfig,
    model: str,
    batch_size: int = 5,
    llm_call: Callable[..., str | ChatCompletionResult] = chat_completion_with_metadata,
) -> BatchedIndustryOpinionResult:
    """Generate small strict batches, retrying only a failed batch's industries."""
    if not industries:
        return BatchedIndustryOpinionResult(
            batch=IndustryOpinionBatch(
                overall_summary="분석할 산업 신호가 없습니다.",
                opinions=[],
                prompt_version=BATCHED_PROMPT_VERSION,
                input_hash=hashlib.sha256(b"no-industries").hexdigest(),
            ),
            failed_industry_ids=(),
            errors={},
            chunk_count=0,
            retry_count=0,
        )

    size = max(1, int(batch_size))
    chunks = [industries[index : index + size] for index in range(0, len(industries), size)]
    successful_batches: list[IndustryOpinionBatch] = []
    opinions_by_id: dict[str, dict[str, Any]] = {}
    errors: dict[str, str] = {}
    retry_count = 0

    def remember(batch: IndustryOpinionBatch) -> None:
        successful_batches.append(batch)
        for opinion in batch.opinions:
            opinions_by_id[str(opinion["industry_id"])] = opinion

    for chunk in chunks:
        try:
            remember(
                generate_industry_opinions(
                    chunk,
                    config=config,
                    model=model,
                    llm_call=llm_call,
                )
            )
            continue
        except Exception as chunk_exc:
            chunk_error = str(chunk_exc)

        for industry in chunk:
            industry_id = str(industry["industry_id"])
            retry_count += 1
            try:
                remember(
                    generate_industry_opinions(
                        [industry],
                        config=config,
                        model=model,
                        llm_call=llm_call,
                    )
                )
            except Exception as retry_exc:
                errors[industry_id] = f"batch={chunk_error}; retry={retry_exc}"

    ordered_ids = [str(industry["industry_id"]) for industry in industries]
    opinions = [
        opinions_by_id[industry_id]
        for industry_id in ordered_ids
        if industry_id in opinions_by_id
    ]
    summaries = [batch.overall_summary for batch in successful_batches if batch.overall_summary]
    overall_summary = (
        "배치별 요약: " + " / ".join(summaries)
        if summaries
        else "산업 AI 의견 생성에 실패했습니다."
    )
    hashes = [batch.input_hash for batch in successful_batches if batch.input_hash]
    aggregate_hash_source = "|".join(hashes) or "all-batches-failed"
    combined = IndustryOpinionBatch(
        overall_summary=overall_summary[:2000],
        opinions=opinions,
        prompt_version=BATCHED_PROMPT_VERSION,
        input_hash=hashlib.sha256(aggregate_hash_source.encode("utf-8")).hexdigest(),
        input_tokens=_sum_optional([batch.input_tokens for batch in successful_batches]),
        output_tokens=_sum_optional([batch.output_tokens for batch in successful_batches]),
    )
    return BatchedIndustryOpinionResult(
        batch=combined,
        failed_industry_ids=tuple(
            industry_id for industry_id in ordered_ids if industry_id in errors
        ),
        errors=errors,
        chunk_count=len(chunks),
        retry_count=retry_count,
    )


def store_industry_opinions(
    batch: IndustryOpinionBatch,
    *,
    as_of: str,
    cycle_model_version: str,
    llm_model: str,
    db_path: Path | None = None,
) -> int:
    insight_repository.upsert_industry_ai_run(
        {
            "as_of": as_of,
            "cycle_model_version": cycle_model_version,
            "llm_model": llm_model,
            "prompt_version": batch.prompt_version,
            "input_hash": batch.input_hash,
            "industry_count": len(batch.opinions),
            "overall_summary": batch.overall_summary,
            "input_tokens": batch.input_tokens,
            "output_tokens": batch.output_tokens,
        },
        db_path=db_path,
    )
    for opinion in batch.opinions:
        insight_repository.upsert_industry_ai_opinion(
            {
                **opinion,
                "as_of": as_of,
                "cycle_model_version": cycle_model_version,
                "llm_model": llm_model,
                "overall_summary": batch.overall_summary,
                "prompt_version": batch.prompt_version,
                "input_hash": batch.input_hash,
            },
            db_path=db_path,
        )
    return len(batch.opinions)
