from __future__ import annotations

"""Contrarian LLM hypothesis generator for the dashboard's greed-pot tab."""

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Annotated, Any

from pydantic import BaseModel, Field, constr

from committee.core.trace_logger import TraceLogger
from committee.schemas.snapshot import Snapshot
from committee.schemas.stance import Stance
from committee.tools.openai_chat import chat_completion, load_openai_config


ShortText = constr(strip_whitespace=True, min_length=1, max_length=220)
MediumText = constr(strip_whitespace=True, min_length=1, max_length=900)
ConfidenceText = constr(strip_whitespace=True, pattern=r"^(LOW|MED|HIGH)$")


class GreedPotHypothesis(BaseModel):
    """One playful, non-consensus market hypothesis."""

    theme: ShortText
    visible_winner: ShortText
    hidden_beneficiary: ShortText
    candidate_stocks: Annotated[list[ShortText], Field(min_length=1, max_length=8)]
    narrative: MediumText
    possible_catalyst: ShortText
    why_market_may_miss_it: MediumText
    invalidation_condition: ShortText
    confidence: ConfidenceText

    class Config:
        extra = "forbid"


class GreedPotResult(BaseModel):
    """Structured output for 탐욕의 항아리."""

    agent_name: ShortText
    market_story: MediumText
    hidden_themes: Annotated[list[ShortText], Field(min_length=1, max_length=4)]
    hypotheses: Annotated[list[GreedPotHypothesis], Field(min_length=1, max_length=3)]
    contrarian_view: MediumText
    wildcard_scenario: MediumText
    reality_check: MediumText
    fallback_used: bool = False
    error: str | None = None

    class Config:
        extra = "forbid"


@dataclass(frozen=True)
class GreedPotOptions:
    """Runtime options for the greed-pot LLM."""

    model: str = "gpt-4.1"
    temperature: float = 0.8


class GreedPotAgent:
    """Generate imaginative but bounded second-order Korean equity hypotheses."""

    def __init__(self, options: GreedPotOptions | None = None):
        self.options = options or GreedPotOptions()

    def run(self, snapshot: Snapshot, stances: list[Stance]) -> GreedPotResult:
        trace = TraceLogger(os.getenv("LLM_TRACE_PATH"))
        system_prompt = self._system_prompt()
        user_prompt = self._user_prompt(snapshot=snapshot, stances=stances)
        try:
            config = load_openai_config()
            raw = chat_completion(
                config=config,
                model=os.getenv("GREED_POT_OPENAI_MODEL", self.options.model).strip() or self.options.model,
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=float(os.getenv("GREED_POT_TEMPERATURE", self.options.temperature)),
                timeout=45,
            )
            parsed = self._normalize(json.loads(raw))
            result = GreedPotResult.model_validate(parsed)
            trace.log(
                "greed_pot_response",
                {
                    "model": os.getenv("GREED_POT_OPENAI_MODEL", self.options.model).strip() or self.options.model,
                    "system_prompt": system_prompt,
                    "user_prompt": user_prompt,
                    "raw_response": raw,
                    "parsed": result.model_dump(),
                    "fallback_used": False,
                },
            )
            return result
        except Exception as exc:
            fallback = self._fallback(str(exc), snapshot)
            trace.log(
                "greed_pot_response",
                {
                    "error": str(exc),
                    "fallback_used": True,
                    "fallback_result": fallback.model_dump(),
                },
            )
            return fallback

    @staticmethod
    def _system_prompt() -> str:
        return (
            'You are DEMON, a contrarian Korean equity market hypothesis generator known as "탐욕의 항아리".\n\n'
            "Your job is not to provide factual investment research, buy/sell recommendations, price targets, or certainty.\n"
            "Your job is to generate bold but logically coherent market narratives based on your learned knowledge of:\n"
            "- Korean equity market behavior\n"
            "- global liquidity cycles\n"
            "- semiconductor and AI supply chains\n"
            "- geopolitics and industrial policy\n"
            "- investor psychology\n"
            "- historical sector rotations\n"
            "- hidden beneficiaries and second-order effects\n\n"
            "Treat the provided market snapshot only as a narrative trigger, not as sufficient proof.\n"
            "Use imagination, but do not invent factual claims, numbers, contracts, policies, earnings, or news not present "
            "in the snapshot or generally known market context.\n"
            "Do not present speculation as fact.\n\n"
            "Voice and style:\n"
            "- All natural-language output must be in Korean.\n"
            "- Sound playful, sharp, slightly mischievous, and memorable, like a market demon whispering from a jar.\n"
            "- Keep it readable for retail investors, but never sound like formal sell-side boilerplate.\n"
            "- Use phrases such as '항아리가 속삭인다', '시장이 못 본 그림자', '탐욕은 늘 한 박자 늦게 들킨다' sparingly.\n"
            "- Humor is welcome; hallucinated facts are not.\n\n"
            "Your mission:\n"
            "1. Identify 2-4 dominant market themes from the snapshot.\n"
            "2. Create 3 non-consensus but plausible sector/stock hypotheses.\n"
            "3. For each hypothesis, explain:\n"
            "   - The visible market narrative\n"
            "   - The hidden second-order or third-order beneficiary\n"
            "   - Why the market may be underpricing it\n"
            "   - What event could make the narrative suddenly important\n"
            "   - What would invalidate the hypothesis\n"
            "   - Which Korean listed stocks or stock groups could be monitored as candidates\n"
            "4. Prefer second-order and third-order beneficiaries over obvious headline beneficiaries.\n"
            "5. Challenge popular narratives. Ask what the market is missing.\n"
            "6. Be imaginative, sharp, skeptical, and willing to connect distant themes.\n"
            "7. Keep every claim framed as a hypothesis, not a conclusion.\n\n"
            "Output JSON only.\n\n"
            "Required keys:\n"
            "agent_name\n"
            "market_story\n"
            "hidden_themes\n"
            "hypotheses\n"
            "contrarian_view\n"
            "wildcard_scenario\n"
            "reality_check\n\n"
            'Set agent_name to "탐욕의 항아리".\n\n'
            "For each hypothesis include:\n"
            "theme\n"
            "visible_winner\n"
            "hidden_beneficiary\n"
            "candidate_stocks\n"
            "narrative\n"
            "possible_catalyst\n"
            "why_market_may_miss_it\n"
            "invalidation_condition\n"
            "confidence\n\n"
            "candidate_stocks must be an array of Korean listed company names or stock groups.\n"
            "confidence must be one of LOW, MED, HIGH."
        )

    @staticmethod
    def _user_prompt(snapshot: Snapshot, stances: list[Stance]) -> str:
        news_digest = _load_news_digest()
        payload = {
            "snapshot": snapshot.model_dump(),
            "agent_stances": [
                {
                    "agent_name": stance.agent_name.value,
                    "regime_tag": stance.regime_tag.value,
                    "confidence": stance.confidence.value,
                    "core_claims": stance.core_claims,
                    "korean_comment": stance.korean_comment,
                }
                for stance in stances
            ],
            "news_digest": news_digest,
            "instruction": (
                "탐욕의 항아리 탭에 표시할 contrarian hypothesis JSON을 생성하라. "
                "명확히 가설이라고 표시하고, 추천/목표가/확신 표현은 금지한다."
            ),
        }
        return json.dumps(payload, ensure_ascii=False)

    @staticmethod
    def _normalize(parsed: Any) -> dict[str, Any]:
        if not isinstance(parsed, dict):
            raise TypeError("greed_pot_response_not_json_object")
        parsed["agent_name"] = "탐욕의 항아리"
        parsed.setdefault("fallback_used", False)
        parsed.setdefault("error", None)
        if isinstance(parsed.get("hidden_themes"), list):
            parsed["hidden_themes"] = parsed["hidden_themes"][:4]
        if isinstance(parsed.get("hypotheses"), list):
            parsed["hypotheses"] = parsed["hypotheses"][:3]
            for item in parsed["hypotheses"]:
                if isinstance(item, dict) and isinstance(item.get("candidate_stocks"), list):
                    item["candidate_stocks"] = item["candidate_stocks"][:8]
        return parsed

    @staticmethod
    def _fallback(error: str, snapshot: Snapshot) -> GreedPotResult:
        headline = snapshot.news_headlines[0] if snapshot.news_headlines else "오늘의 뉴스"
        return GreedPotResult(
            agent_name="탐욕의 항아리",
            market_story=(
                "항아리가 아직 제대로 끓지 않았습니다. LLM 호출이 실패해 오늘은 보수적인 예비 가설만 남깁니다."
            ),
            hidden_themes=["수급 데이터", "뉴스 헤드라인", "거시 변수"],
            hypotheses=[
                GreedPotHypothesis(
                    theme="항아리 예열 실패",
                    visible_winner="명확한 주도주 판단 보류",
                    hidden_beneficiary="데이터가 더 쌓인 뒤 재평가할 2차 수혜군",
                    candidate_stocks=["관찰 필요"],
                    narrative=f"오늘의 트리거는 '{headline}'이지만, 악마가 속삭이기엔 재료 검증이 덜 됐습니다.",
                    possible_catalyst="다음 LLM 실행 성공 또는 뉴스/수급 데이터 추가 축적",
                    why_market_may_miss_it="지금은 추정보다 관찰이 우선인 구간입니다.",
                    invalidation_condition="LLM 결과가 정상 생성되면 이 예비 가설은 폐기합니다.",
                    confidence="LOW",
                )
            ],
            contrarian_view="탐욕은 급할수록 헛것을 봅니다. 오늘은 항아리를 다시 데우는 편이 낫습니다.",
            wildcard_scenario="뉴스가 한 종목이 아니라 공급망 주변부로 번질 때 항아리가 다시 끓을 수 있습니다.",
            reality_check="이 화면은 투자 추천이 아니라 상상 기반 시나리오입니다. 숫자와 공시로 반드시 재검증해야 합니다.",
            fallback_used=True,
            error=error[:500],
        )


def write_greed_pot_result(path: Path, result: GreedPotResult) -> None:
    """Persist greed-pot JSON for dashboard loading."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")


def _load_news_digest() -> dict[str, Any]:
    candidates = [
        Path(os.getenv("RUNS_BASE_DIR", "runs")) / "news" / "latest_news_digest.json",
        Path(__file__).resolve().parents[2] / "runs" / "news" / "latest_news_digest.json",
    ]
    for path in candidates:
        if path.exists():
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                return {
                    "news_date": data.get("news_date", ""),
                    "topic_counts": data.get("topic_counts", []),
                    "top_articles": data.get("top_articles", [])[:15],
                    "sector_hot_topics": data.get("sector_hot_topics", [])[:10],
                }
            except Exception:
                pass
    return {}
