from __future__ import annotations

"""Validated input and output models for the research-to-market radar."""

from dataclasses import dataclass
from datetime import date
import re
from typing import Any, Mapping
from urllib.parse import urlparse


INPUT_SCHEMA_VERSION = "research-radar-input-v1"
REPORT_SCHEMA_VERSION = "research-radar-report-v1"

STAGE_ORDER = (
    "research_validation",
    "talent_mobility",
    "capital_formation",
    "infrastructure_bottleneck",
    "earnings_confirmation",
)

STAGE_LABELS = {
    "research_validation": "연구 검증",
    "talent_mobility": "인재 이동·창업",
    "capital_formation": "자본 형성",
    "infrastructure_bottleneck": "인프라 병목",
    "earnings_confirmation": "상장사 실적 확인",
}

STAGE_WEIGHTS = {
    "research_validation": 0.25,
    "talent_mobility": 0.15,
    "capital_formation": 0.20,
    "infrastructure_bottleneck": 0.20,
    "earnings_confirmation": 0.20,
}

SOURCE_RELIABILITY = {
    "academic_primary": 1.00,
    "academic_preprint": 0.75,
    "regulatory_filing": 1.00,
    "company_filing": 0.95,
    "company_release": 0.82,
    "reputable_media": 0.72,
    "secondary_analysis": 0.55,
    "other": 0.40,
}

DIRECTION_VALUES = {"positive": 1.0, "neutral": 0.0, "negative": -1.0}
DIRECTNESS_WEIGHTS = {"direct": 1.0, "enabler": 0.85, "adjacent": 0.60, "speculative": 0.35}
DATE_PRECISIONS = {"day", "month", "year"}

_ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]{1,79}$")


class RadarValidationError(ValueError):
    """Raised when a radar input violates the evidence contract."""


def parse_iso_date(value: Any, *, field_name: str) -> date:
    if not isinstance(value, str) or not value.strip():
        raise RadarValidationError(f"{field_name} must be an ISO date string")
    try:
        return date.fromisoformat(value.strip())
    except ValueError as exc:
        raise RadarValidationError(f"{field_name} must use YYYY-MM-DD: {value!r}") from exc


def required_text(payload: Mapping[str, Any], key: str, *, context: str) -> str:
    value = payload.get(key)
    if not isinstance(value, str) or not value.strip():
        raise RadarValidationError(f"{context}.{key} is required")
    return value.strip()


def validate_id(value: str, *, field_name: str) -> str:
    if not _ID_RE.fullmatch(value):
        raise RadarValidationError(
            f"{field_name} must use lowercase letters, digits, and hyphens (2-80 chars): {value!r}"
        )
    return value


def validate_url(value: str, *, field_name: str) -> str:
    parsed = urlparse(value)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise RadarValidationError(f"{field_name} must be an absolute http(s) URL")
    return value


def _string_tuple(value: Any, *, field_name: str) -> tuple[str, ...]:
    if value is None:
        return ()
    if not isinstance(value, list):
        raise RadarValidationError(f"{field_name} must be a JSON array")
    result: list[str] = []
    for item in value:
        if not isinstance(item, str) or not item.strip():
            raise RadarValidationError(f"{field_name} entries must be non-empty strings")
        normalized = item.strip()
        if normalized not in result:
            result.append(normalized)
    return tuple(result)


@dataclass(frozen=True)
class Evidence:
    evidence_id: str
    stage: str
    event_type: str
    title: str
    claim: str
    event_date: date
    known_at: date
    date_precision: str
    source_url: str
    source_name: str
    source_kind: str
    direction: str
    strength: float
    limitation: str | None = None
    tags: tuple[str, ...] = ()

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any], *, index: int) -> "Evidence":
        context = f"evidence[{index}]"
        evidence_id = validate_id(required_text(payload, "evidence_id", context=context), field_name=f"{context}.evidence_id")
        stage = required_text(payload, "stage", context=context)
        if stage not in STAGE_ORDER:
            raise RadarValidationError(f"{context}.stage must be one of {', '.join(STAGE_ORDER)}")
        source_kind = required_text(payload, "source_kind", context=context)
        if source_kind not in SOURCE_RELIABILITY:
            raise RadarValidationError(
                f"{context}.source_kind must be one of {', '.join(SOURCE_RELIABILITY)}"
            )
        direction = str(payload.get("direction") or "positive").strip()
        if direction not in DIRECTION_VALUES:
            raise RadarValidationError(f"{context}.direction must be positive, neutral, or negative")
        strength_raw = payload.get("strength")
        if isinstance(strength_raw, bool) or not isinstance(strength_raw, (int, float)):
            raise RadarValidationError(f"{context}.strength must be a number from 0 to 1")
        strength = float(strength_raw)
        if not 0.0 <= strength <= 1.0:
            raise RadarValidationError(f"{context}.strength must be between 0 and 1")
        date_precision = str(payload.get("date_precision") or "day").strip()
        if date_precision not in DATE_PRECISIONS:
            raise RadarValidationError(f"{context}.date_precision must be day, month, or year")
        limitation_raw = payload.get("limitation")
        limitation = None
        if limitation_raw is not None:
            if not isinstance(limitation_raw, str):
                raise RadarValidationError(f"{context}.limitation must be a string")
            limitation = limitation_raw.strip() or None
        source_url = validate_url(
            required_text(payload, "source_url", context=context), field_name=f"{context}.source_url"
        )
        return cls(
            evidence_id=evidence_id,
            stage=stage,
            event_type=required_text(payload, "event_type", context=context),
            title=required_text(payload, "title", context=context),
            claim=required_text(payload, "claim", context=context),
            event_date=parse_iso_date(payload.get("event_date"), field_name=f"{context}.event_date"),
            known_at=parse_iso_date(payload.get("known_at"), field_name=f"{context}.known_at"),
            date_precision=date_precision,
            source_url=source_url,
            source_name=required_text(payload, "source_name", context=context),
            source_kind=source_kind,
            direction=direction,
            strength=strength,
            limitation=limitation,
            tags=_string_tuple(payload.get("tags"), field_name=f"{context}.tags"),
        )

    @property
    def reliability(self) -> float:
        return SOURCE_RELIABILITY[self.source_kind]

    @property
    def source_domain(self) -> str:
        return (urlparse(self.source_url).hostname or "").lower().removeprefix("www.")

    @property
    def signed_signal(self) -> float:
        return DIRECTION_VALUES[self.direction] * self.strength * self.reliability

    def to_dict(self) -> dict[str, Any]:
        return {
            "evidence_id": self.evidence_id,
            "stage": self.stage,
            "stage_label": STAGE_LABELS[self.stage],
            "event_type": self.event_type,
            "title": self.title,
            "claim": self.claim,
            "event_date": self.event_date.isoformat(),
            "known_at": self.known_at.isoformat(),
            "date_precision": self.date_precision,
            "source_url": self.source_url,
            "source_name": self.source_name,
            "source_kind": self.source_kind,
            "source_reliability": self.reliability,
            "direction": self.direction,
            "strength": self.strength,
            "signed_signal": round(self.signed_signal, 4),
            "limitation": self.limitation,
            "tags": list(self.tags),
        }


@dataclass(frozen=True)
class PublicCompanyLink:
    ticker: str
    market: str
    company_name: str
    role: str
    directness: str
    thesis: str
    evidence_ids: tuple[str, ...]

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any], *, index: int) -> "PublicCompanyLink":
        context = f"public_companies[{index}]"
        directness = required_text(payload, "directness", context=context)
        if directness not in DIRECTNESS_WEIGHTS:
            raise RadarValidationError(
                f"{context}.directness must be one of {', '.join(DIRECTNESS_WEIGHTS)}"
            )
        evidence_ids = _string_tuple(payload.get("evidence_ids"), field_name=f"{context}.evidence_ids")
        if not evidence_ids:
            raise RadarValidationError(f"{context}.evidence_ids must contain at least one evidence ID")
        return cls(
            ticker=required_text(payload, "ticker", context=context).upper(),
            market=required_text(payload, "market", context=context).upper(),
            company_name=required_text(payload, "company_name", context=context),
            role=required_text(payload, "role", context=context),
            directness=directness,
            thesis=required_text(payload, "thesis", context=context),
            evidence_ids=evidence_ids,
        )


@dataclass(frozen=True)
class ThemeInput:
    theme_id: str
    name: str
    thesis: str
    as_of: date
    evidence: tuple[Evidence, ...]
    public_companies: tuple[PublicCompanyLink, ...]
    limitations: tuple[str, ...] = ()

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any], *, as_of_override: str | None = None) -> "ThemeInput":
        if not isinstance(payload, Mapping):
            raise RadarValidationError("input root must be a JSON object")
        if payload.get("schema_version") != INPUT_SCHEMA_VERSION:
            raise RadarValidationError(f"schema_version must be {INPUT_SCHEMA_VERSION!r}")
        theme_payload = payload.get("theme")
        if not isinstance(theme_payload, Mapping):
            raise RadarValidationError("theme must be a JSON object")
        theme_id = validate_id(
            required_text(theme_payload, "theme_id", context="theme"), field_name="theme.theme_id"
        )
        evidence_payload = payload.get("evidence")
        if not isinstance(evidence_payload, list):
            raise RadarValidationError("evidence must be a JSON array")
        evidence = tuple(Evidence.from_dict(row, index=index) for index, row in enumerate(evidence_payload) if isinstance(row, Mapping))
        if len(evidence) != len(evidence_payload):
            raise RadarValidationError("every evidence entry must be a JSON object")
        evidence_ids = [row.evidence_id for row in evidence]
        if len(set(evidence_ids)) != len(evidence_ids):
            duplicates = sorted({item for item in evidence_ids if evidence_ids.count(item) > 1})
            raise RadarValidationError(f"duplicate evidence_id: {', '.join(duplicates)}")

        company_payload = payload.get("public_companies", [])
        if not isinstance(company_payload, list):
            raise RadarValidationError("public_companies must be a JSON array")
        companies = tuple(
            PublicCompanyLink.from_dict(row, index=index)
            for index, row in enumerate(company_payload)
            if isinstance(row, Mapping)
        )
        if len(companies) != len(company_payload):
            raise RadarValidationError("every public_companies entry must be a JSON object")
        known_ids = set(evidence_ids)
        for index, company in enumerate(companies):
            unknown = sorted(set(company.evidence_ids) - known_ids)
            if unknown:
                raise RadarValidationError(
                    f"public_companies[{index}].evidence_ids references unknown IDs: {', '.join(unknown)}"
                )

        raw_as_of = as_of_override if as_of_override is not None else payload.get("as_of")
        return cls(
            theme_id=theme_id,
            name=required_text(theme_payload, "name", context="theme"),
            thesis=required_text(theme_payload, "thesis", context="theme"),
            as_of=parse_iso_date(raw_as_of, field_name="as_of"),
            evidence=evidence,
            public_companies=companies,
            limitations=_string_tuple(payload.get("limitations"), field_name="limitations"),
        )


@dataclass(frozen=True)
class StageAssessment:
    stage: str
    score: float
    net_signal: float
    confidence: float
    evidence_count: int
    distinct_source_count: int
    positive_count: int
    neutral_count: int
    negative_count: int
    evidence_ids: tuple[str, ...]
    passed: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "stage": self.stage,
            "label": STAGE_LABELS[self.stage],
            "score": self.score,
            "net_signal": self.net_signal,
            "confidence": self.confidence,
            "evidence_count": self.evidence_count,
            "distinct_source_count": self.distinct_source_count,
            "positive_count": self.positive_count,
            "neutral_count": self.neutral_count,
            "negative_count": self.negative_count,
            "evidence_ids": list(self.evidence_ids),
            "passed": self.passed,
        }


@dataclass(frozen=True)
class CompanyAssessment:
    ticker: str
    market: str
    company_name: str
    role: str
    directness: str
    thesis: str
    link_strength: float
    evidence_ids: tuple[str, ...]
    unavailable_evidence_ids: tuple[str, ...]
    positive_count: int
    negative_count: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "ticker": self.ticker,
            "market": self.market,
            "company_name": self.company_name,
            "role": self.role,
            "directness": self.directness,
            "thesis": self.thesis,
            "link_strength": self.link_strength,
            "evidence_ids": list(self.evidence_ids),
            "unavailable_evidence_ids": list(self.unavailable_evidence_ids),
            "positive_count": self.positive_count,
            "negative_count": self.negative_count,
        }


@dataclass(frozen=True)
class ExcludedEvidence:
    evidence_id: str
    reason: str
    known_at: str

    def to_dict(self) -> dict[str, str]:
        return {"evidence_id": self.evidence_id, "reason": self.reason, "known_at": self.known_at}


@dataclass(frozen=True)
class RadarReport:
    theme_id: str
    name: str
    thesis: str
    as_of: str
    status: str
    status_label: str
    chain_score: float
    confidence: float
    stages: tuple[StageAssessment, ...]
    public_companies: tuple[CompanyAssessment, ...]
    evidence: tuple[Evidence, ...]
    excluded_evidence: tuple[ExcludedEvidence, ...]
    data_gaps: tuple[str, ...]
    limitations: tuple[str, ...]
    methodology: Mapping[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": REPORT_SCHEMA_VERSION,
            "theme": {"theme_id": self.theme_id, "name": self.name, "thesis": self.thesis},
            "as_of": self.as_of,
            "status": self.status,
            "status_label": self.status_label,
            "chain_score": self.chain_score,
            "confidence": self.confidence,
            "stages": [row.to_dict() for row in self.stages],
            "public_companies": [row.to_dict() for row in self.public_companies],
            "evidence": [row.to_dict() for row in self.evidence],
            "excluded_evidence": [row.to_dict() for row in self.excluded_evidence],
            "data_gaps": list(self.data_gaps),
            "limitations": list(self.limitations),
            "methodology": dict(self.methodology),
        }
