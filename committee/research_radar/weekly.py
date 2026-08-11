from __future__ import annotations

"""Weekly paper discovery and grounded LLM interpretation for research radar."""

import hashlib
import json
import re
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable, Mapping
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from xml.etree import ElementTree

from committee.research_radar.models import RadarReport, ThemeInput
from committee.research_radar.scoring import analyze_theme

if TYPE_CHECKING:
    from committee.tools.openai_chat import OpenAIConfig


CONFIG_SCHEMA_VERSION = "research-radar-weekly-config-v1"
AUDIT_SCHEMA_VERSION = "research-radar-weekly-audit-v1"
PROMPT_VERSION = "research_radar_paper_interpreter_v1"
ARXIV_API_URL = "https://export.arxiv.org/api/query"
_ATOM_NS = {"atom": "http://www.w3.org/2005/Atom"}
_SAFE_ID = re.compile(r"[^a-z0-9]+")
_ALLOWED_DIRECTIONS = {"positive", "neutral", "negative"}


@dataclass(frozen=True)
class PaperCandidate:
    paper_id: str
    title: str
    abstract: str
    authors: tuple[str, ...]
    published_at: datetime
    updated_at: datetime
    url: str
    categories: tuple[str, ...]

    @property
    def published_date(self) -> date:
        return self.published_at.date()

    def to_prompt_dict(self) -> dict[str, object]:
        return {
            "paper_id": self.paper_id,
            "title": self.title,
            "abstract": self.abstract,
            "authors": list(self.authors),
            "published_at": self.published_at.isoformat(),
            "url": self.url,
            "categories": list(self.categories),
        }


@dataclass(frozen=True)
class PaperInterpretation:
    paper_id: str
    relevant: bool
    direction: str
    claim: str
    limitation: str
    strength: float
    tags: tuple[str, ...]


@dataclass(frozen=True)
class InterpretationBatch:
    rows: tuple[PaperInterpretation, ...]
    model: str | None
    input_tokens: int | None
    output_tokens: int | None
    input_hash: str


def _normalize_space(value: str) -> str:
    return " ".join(value.split())


def _parse_datetime(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _paper_id_from_url(url: str) -> str:
    raw = url.rstrip("/").rsplit("/", 1)[-1].lower()
    normalized = _SAFE_ID.sub("-", raw).strip("-")
    return normalized[:70] or hashlib.sha256(url.encode("utf-8")).hexdigest()[:16]


def parse_arxiv_feed(xml_text: str) -> list[PaperCandidate]:
    """Parse an arXiv Atom response without third-party feed dependencies."""
    root = ElementTree.fromstring(xml_text)
    result: list[PaperCandidate] = []
    for entry in root.findall("atom:entry", _ATOM_NS):
        entry_url = _normalize_space(entry.findtext("atom:id", default="", namespaces=_ATOM_NS))
        title = _normalize_space(entry.findtext("atom:title", default="", namespaces=_ATOM_NS))
        abstract = _normalize_space(entry.findtext("atom:summary", default="", namespaces=_ATOM_NS))
        published = entry.findtext("atom:published", default="", namespaces=_ATOM_NS)
        updated = entry.findtext("atom:updated", default=published, namespaces=_ATOM_NS)
        if not entry_url or not title or not abstract or not published:
            continue
        authors = tuple(
            _normalize_space(author.findtext("atom:name", default="", namespaces=_ATOM_NS))
            for author in entry.findall("atom:author", _ATOM_NS)
            if _normalize_space(author.findtext("atom:name", default="", namespaces=_ATOM_NS))
        )
        categories = tuple(
            str(category.attrib.get("term") or "").strip()
            for category in entry.findall("atom:category", _ATOM_NS)
            if str(category.attrib.get("term") or "").strip()
        )
        result.append(
            PaperCandidate(
                paper_id=_paper_id_from_url(entry_url),
                title=title,
                abstract=abstract,
                authors=authors,
                published_at=_parse_datetime(published),
                updated_at=_parse_datetime(updated),
                url=entry_url.replace("http://", "https://", 1),
                categories=categories,
            )
        )
    return result


def fetch_arxiv_papers(
    query: str,
    *,
    max_results: int,
    timeout: int = 30,
    http_get: Callable[..., Any] | None = None,
) -> list[PaperCandidate]:
    params = urlencode(
        {
            "search_query": query,
            "start": 0,
            "max_results": max(1, max_results),
            "sortBy": "submittedDate",
            "sortOrder": "descending",
        }
    )
    url = f"{ARXIV_API_URL}?{params}"
    headers = {"User-Agent": "richguysgogo-research-radar/1.0"}
    if http_get is None:
        request = Request(url, headers=headers)
        with urlopen(request, timeout=timeout) as response:
            xml_text = response.read().decode("utf-8")
    else:
        response = http_get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        xml_text = str(response.text)
    return parse_arxiv_feed(xml_text)


def filter_papers_for_window(
    papers: list[PaperCandidate], *, as_of: date, lookback_days: int
) -> list[PaperCandidate]:
    start = as_of - timedelta(days=max(1, lookback_days) - 1)
    return sorted(
        (paper for paper in papers if start <= paper.published_date <= as_of),
        key=lambda paper: (paper.published_at, paper.paper_id),
        reverse=True,
    )


def load_weekly_config(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("schema_version") != CONFIG_SCHEMA_VERSION:
        raise ValueError(f"weekly_config_schema_must_be:{CONFIG_SCHEMA_VERSION}")
    topics = payload.get("topics")
    if not isinstance(topics, list) or not topics:
        raise ValueError("weekly_config_topics_required")
    for index, topic in enumerate(topics):
        if not isinstance(topic, dict):
            raise ValueError(f"weekly_config_topic_not_object:{index}")
        for key in ("theme_id", "name", "thesis", "arxiv_query"):
            if not str(topic.get(key) or "").strip():
                raise ValueError(f"weekly_config_topic_missing:{index}:{key}")
    return payload


def build_interpretation_prompts(
    topic: Mapping[str, Any], papers: list[PaperCandidate], *, as_of: date
) -> tuple[str, str]:
    system_prompt = (
        "당신은 미래산업 논문 증거를 심사하는 보수적인 리서치 분석가다. 제공된 제목·초록·메타데이터만 "
        "사용하고 사전학습 지식으로 최근 사실을 보충하지 않는다. 논문이 특정 기업의 매출·투자·상용화를 "
        "증명한다고 추론하지 않는다. 사실, 저자의 주장, 한계와 대안 설명을 구분한다. survey·position paper·"
        "시뮬레이션 전용 연구는 실제 로봇 검증보다 낮은 strength를 부여한다. JSON 객체만 출력한다."
    )
    schema = {
        "papers": [
            {
                "paper_id": "입력 paper_id",
                "relevant": True,
                "direction": "positive|neutral|negative",
                "claim": "초록으로 직접 뒷받침되는 한국어 핵심 주장",
                "limitation": "초록에서 확인되는 한계 또는 검증되지 않은 부분",
                "strength": 0.0,
                "tags": ["최대 6개 영문 소문자 태그"],
            }
        ]
    }
    payload = {
        "as_of": as_of.isoformat(),
        "theme": {
            "theme_id": topic["theme_id"],
            "name": topic["name"],
            "thesis": topic["thesis"],
            "scope": topic.get("scope", []),
        },
        "strength_guide": {
            "0.85": "여러 실제 로봇·과제에서 비교 검증하고 재현 자산도 제공",
            "0.70": "실제 로봇 실험 또는 강한 정량 벤치마크",
            "0.55": "시뮬레이션·제한된 벤치마크 중심",
            "0.35": "survey·position·개념 제안 중심",
        },
        "papers": [paper.to_prompt_dict() for paper in papers],
    }
    user_prompt = (
        "각 입력 논문을 빠짐없이 한 번씩 판정하라. strength는 0~0.85로 제한하고, relevant=false인 "
        "경우에도 paper_id와 판정 필드는 반환하라. direction은 기술 가설을 강화하면 positive, 핵심 한계를 "
        "실증하면 negative, 정보가 혼합되거나 단순 survey면 neutral이다. 입력에 없는 URL이나 수치를 만들지 "
        "마라.\n\n출력 스키마:\n"
        f"{json.dumps(schema, ensure_ascii=False)}\n\n입력:\n"
        f"{json.dumps(payload, ensure_ascii=False, separators=(',', ':'))}"
    )
    return system_prompt, user_prompt


def validate_interpretation_payload(
    raw: str | Mapping[str, Any], papers: list[PaperCandidate]
) -> tuple[PaperInterpretation, ...]:
    parsed = json.loads(raw) if isinstance(raw, str) else dict(raw)
    rows = parsed.get("papers")
    if not isinstance(rows, list):
        raise ValueError("paper_interpretation_missing_papers")
    expected = {paper.paper_id for paper in papers}
    validated: list[PaperInterpretation] = []
    seen: set[str] = set()
    for row in rows:
        if not isinstance(row, dict):
            continue
        paper_id = str(row.get("paper_id") or "").strip()
        if paper_id not in expected or paper_id in seen:
            continue
        relevant = row.get("relevant") is True
        direction = str(row.get("direction") or "neutral").strip()
        if direction not in _ALLOWED_DIRECTIONS:
            direction = "neutral"
        claim = _normalize_space(str(row.get("claim") or ""))[:1000]
        limitation = _normalize_space(str(row.get("limitation") or ""))[:1000]
        try:
            strength = float(row.get("strength", 0.0))
        except (TypeError, ValueError):
            strength = 0.0
        strength = round(max(0.0, min(0.85, strength)), 4)
        tags: list[str] = []
        for value in row.get("tags", []) if isinstance(row.get("tags"), list) else []:
            tag = _SAFE_ID.sub("-", str(value).lower()).strip("-")[:40]
            if tag and tag not in tags:
                tags.append(tag)
        if relevant and not claim:
            relevant = False
            limitation = limitation or "LLM이 초록에서 근거가 있는 주장을 추출하지 못했습니다."
        validated.append(
            PaperInterpretation(
                paper_id=paper_id,
                relevant=relevant,
                direction=direction,
                claim=claim,
                limitation=limitation or "초록만 검토했으며 본문·독립 재현 여부는 확인하지 않았습니다.",
                strength=strength,
                tags=tuple(tags[:6]),
            )
        )
        seen.add(paper_id)
    missing = sorted(expected - seen)
    if missing:
        raise ValueError(f"paper_interpretation_missing_ids:{','.join(missing)}")
    return tuple(validated)


def interpret_papers(
    topic: Mapping[str, Any],
    papers: list[PaperCandidate],
    *,
    as_of: date,
    config: "OpenAIConfig",
    model: str,
    llm_call: Callable[..., Any] | None = None,
) -> InterpretationBatch:
    if llm_call is None:
        from committee.tools.openai_chat import chat_completion_with_metadata

        llm_call = chat_completion_with_metadata
    system_prompt, user_prompt = build_interpretation_prompts(topic, papers, as_of=as_of)
    result = llm_call(
        config=config,
        model=model,
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        temperature=0.0,
        timeout=120,
    )
    if isinstance(result, str):
        raw = result
        resolved_model = model
        input_tokens = None
        output_tokens = None
    else:
        raw = str(result.content)
        resolved_model = result.model
        input_tokens = result.input_tokens
        output_tokens = result.output_tokens
    rows = validate_interpretation_payload(raw, papers)
    return InterpretationBatch(
        rows=rows,
        model=resolved_model,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        input_hash=hashlib.sha256(user_prompt.encode("utf-8")).hexdigest(),
    )


def build_report(
    topic: Mapping[str, Any],
    papers: list[PaperCandidate],
    interpretations: tuple[PaperInterpretation, ...],
    *,
    as_of: date,
) -> RadarReport:
    papers_by_id = {paper.paper_id: paper for paper in papers}
    evidence: list[dict[str, object]] = []
    for interpretation in interpretations:
        if not interpretation.relevant:
            continue
        paper = papers_by_id[interpretation.paper_id]
        evidence.append(
            {
                "evidence_id": f"arxiv-{paper.paper_id}"[:80].rstrip("-"),
                "stage": "research_validation",
                "event_type": "weekly-paper-signal",
                "title": paper.title,
                "claim": interpretation.claim,
                "event_date": paper.published_date.isoformat(),
                "known_at": paper.published_date.isoformat(),
                "date_precision": "day",
                "source_url": paper.url,
                "source_name": "arXiv",
                "source_kind": "academic_preprint",
                "direction": interpretation.direction,
                "strength": interpretation.strength,
                "limitation": interpretation.limitation,
                "tags": list(dict.fromkeys(["weekly-paper", *interpretation.tags])),
            }
        )
    payload = {
        "schema_version": "research-radar-input-v1",
        "as_of": as_of.isoformat(),
        "theme": {
            "theme_id": topic["theme_id"],
            "name": topic["name"],
            "thesis": topic["thesis"],
        },
        "evidence": evidence,
        "public_companies": [],
        "limitations": [
            "주간 논문 레이더는 제목·초록만 해석하며 동료평가, 본문 재현성, 상용화를 자동으로 확정하지 않습니다.",
            "논문 수와 기술 진전은 투자수익이나 기업 실적을 직접 의미하지 않습니다.",
            *[str(item) for item in topic.get("limitations", []) if str(item).strip()],
        ],
    }
    return analyze_theme(ThemeInput.from_dict(payload))


def build_audit_payload(
    topic: Mapping[str, Any],
    papers: list[PaperCandidate],
    batch: InterpretationBatch,
    report: RadarReport,
    *,
    as_of: date,
    lookback_days: int,
) -> dict[str, object]:
    selected = {row.paper_id for row in batch.rows if row.relevant}
    return {
        "schema_version": AUDIT_SCHEMA_VERSION,
        "prompt_version": PROMPT_VERSION,
        "theme_id": topic["theme_id"],
        "as_of": as_of.isoformat(),
        "lookback_days": lookback_days,
        "candidate_count": len(papers),
        "accepted_count": len(selected),
        "rejected_count": len(papers) - len(selected),
        "accepted_paper_ids": sorted(selected),
        "llm_model": batch.model,
        "input_hash": batch.input_hash,
        "input_tokens": batch.input_tokens,
        "output_tokens": batch.output_tokens,
        "report_status": report.status,
        "report_score": report.chain_score,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
