from __future__ import annotations

# Validation safeguards for MVP pipeline outputs.

import re
from typing import Iterable, List, Sequence

from pydantic import ValidationError

from committee.core.report_renderer import Report
from committee.schemas.committee_result import CommitteeResult
from committee.schemas.snapshot import Snapshot
from committee.schemas.stance import Stance


FORBIDDEN_PHRASES = [
    "무조건 매수",
    "반드시 매도",
    "절대 손실 없음",
    "확정 수익",
]

ALLOWED_EVIDENCE_IDS = {
    "snapshot.market_summary.note",
    "snapshot.market_summary.usdkrw",
    "snapshot.market_summary.kospi_change_pct",
    "snapshot.flow_summary.note",
    "snapshot.sector_moves",
    "snapshot.news_headlines",
    "snapshot.watchlist",
}

ALLOWED_NON_TICKER_TOKENS = {
    # Region/market labels frequently present in headlines (not tickers).
    "US",
    "KR",
    "USD",
    "CPI",
    "GDP",
    "PMI",
    "FOMC",
    "ETF",
    "AI",
    "OIL",
    "FED",
    "CNBC",
    "KOSPI",
    "KOSDAQ",
    "SP500",
    "NASDAQ",
    "DOW",
    "VIX",
    "FX",
    "KRW",
    "RISK_ON",
    "RISK_OFF",
    "NEUTRAL",
    "OK",
    "CAUTION",
    "AVOID",
    # KRX internal market codes (not tickers). May appear in flow error notes.
    "STK",  # KOSPI market id in KRX payloads
    "KSQ",  # KOSDAQ market id in KRX payloads
}

TICKER_PATTERN = re.compile(r"\b[A-Z][A-Z0-9]{1,11}\b")


def _assert_no_forbidden_phrases(texts: Iterable[str]) -> None:
    """Reject forbidden phrases in any text field."""
    for text in texts:
        lowered = text.lower()
        for phrase in FORBIDDEN_PHRASES:
            if phrase.lower() in lowered:
                raise ValueError(f"Forbidden phrase detected: {phrase}")


def _extract_text_fields(snapshot: Snapshot, stances: Sequence[Stance], result: CommitteeResult) -> List[str]:
    """Collect text fields for safety checks."""
    texts: List[str] = []
    texts.extend([snapshot.market_summary.note, snapshot.flow_summary.note])
    texts.extend(snapshot.sector_moves)
    texts.extend(snapshot.news_headlines)
    for stance in stances:
        texts.extend(stance.core_claims)
        texts.append(stance.korean_comment)
    texts.append(result.consensus)
    for key_point in result.key_points:
        texts.append(key_point.point)
        texts.extend(key_point.sources)
    for disagreement in result.disagreements:
        texts.extend(
            [
                disagreement.topic,
                disagreement.majority,
                disagreement.minority,
                disagreement.why_it_matters,
            ]
        )
    for guidance in result.ops_guidance:
        texts.append(guidance.text)
    return texts


def _assert_consensus_single_sentence(consensus: str) -> None:
    """Ensure consensus is a single sentence."""
    if "\n" in consensus:
        raise ValueError("Consensus must be a single sentence without newlines.")
    terminators = sum(consensus.count(ch) for ch in ".!?")
    if terminators > 1:
        raise ValueError("Consensus must be a single sentence.")


def _assert_ops_guidance(result: CommitteeResult) -> None:
    """Ensure ops guidance is complete and valid."""
    if len(result.ops_guidance) != 3:
        raise ValueError("ops_guidance must contain exactly 3 items.")
    levels = {guidance.level for guidance in result.ops_guidance}
    level_values = {level.value for level in levels}
    if "OK" not in level_values:
        raise ValueError("ops_guidance must include an OK level.")
    if "CAUTION" not in level_values:
        raise ValueError("ops_guidance must include a CAUTION level.")
    if "AVOID" not in level_values:
        raise ValueError("ops_guidance must include an AVOID level.")
    if not level_values.issubset({"OK", "CAUTION", "AVOID"}):
        raise ValueError("ops_guidance must only use OK/CAUTION/AVOID levels.")


def _assert_stances_present(stances: Sequence[Stance]) -> None:
    """Require at least one stance."""
    if len(stances) < 1:
        raise ValueError("At least one stance is required.")


def _assert_core_claims_limit(stances: Sequence[Stance]) -> None:
    """Enforce maximum core claims per stance."""
    for stance in stances:
        if len(stance.core_claims) > 3:
            raise ValueError("core_claims must not exceed 3 items.")


def _assert_evidence_ids(stance: Stance) -> None:
    """Validate evidence IDs against allowed snapshot paths."""
    invalid = [item for item in stance.evidence_ids if item not in ALLOWED_EVIDENCE_IDS]
    if invalid:
        raise ValueError(f"Invalid evidence_ids: {invalid}")


def _assert_no_unknown_tickers(texts: Iterable[str], watchlist: Sequence[str]) -> None:
    """Block unknown ticker mentions not in watchlist."""
    watchlist_set = {ticker.upper() for ticker in watchlist}
    for text in texts:
        for token in TICKER_PATTERN.findall(text):
            if token in ALLOWED_NON_TICKER_TOKENS:
                continue
            if token not in watchlist_set:
                raise ValueError(f"Ticker '{token}' not found in snapshot watchlist.")


def validate_snapshot(snapshot: Snapshot | dict) -> Snapshot:
    """Validate snapshot schema."""
    try:
        return Snapshot.model_validate(snapshot)
    except ValidationError as exc:
        raise ValueError(str(exc)) from exc


def validate_stances(stances: Iterable[Stance | dict]) -> List[Stance]:
    """Validate stance list schema and constraints."""
    normalized: List[Stance] = []
    for stance in stances:
        try:
            model = Stance.model_validate(stance)
        except ValidationError as exc:
            raise ValueError(str(exc)) from exc
        _assert_evidence_ids(model)
        normalized.append(model)
    _assert_stances_present(normalized)
    _assert_core_claims_limit(normalized)
    return normalized


def validate_committee_result(result: CommitteeResult | dict) -> CommitteeResult:
    """Validate committee result schema and constraints."""
    try:
        model = CommitteeResult.model_validate(result)
    except ValidationError as exc:
        raise ValueError(str(exc)) from exc
    _assert_consensus_single_sentence(model.consensus)
    _assert_ops_guidance(model)
    return model


def validate_report(report: Report | dict) -> Report:
    """Validate final report schema."""
    try:
        model = Report.model_validate(report)
    except ValidationError as exc:
        raise ValueError(str(exc)) from exc
    return model


def validate_pipeline(
    snapshot: Snapshot | dict,
    stances: Iterable[Stance | dict],
    committee_result: CommitteeResult | dict,
    report: Report | dict | None = None,
) -> None:
    """Validate full pipeline outputs."""
    normalized_snapshot = validate_snapshot(snapshot)
    normalized_stances = validate_stances(stances)
    normalized_result = validate_committee_result(committee_result)

    texts = _extract_text_fields(normalized_snapshot, normalized_stances, normalized_result)
    _assert_no_forbidden_phrases(texts)
    # NOTE: Ticker validation is intended to prevent *generated* outputs from mentioning
    # unknown tickers not present in the snapshot watchlist.
    #
    # Snapshot inputs like `news_headlines` and `sector_moves` are external text and may
    # contain arbitrary 2–4 letter acronyms (e.g., "SK", "AI", "US") that match our ticker
    # regex but are not tradable symbols in our watchlist. To avoid false positives that
    # break the nightly pipeline, we only enforce the ticker whitelist on:
    # - agent/committee generated text
    # - snapshot summary notes (authored by our code)
    ticker_guard_texts: List[str] = []
    ticker_guard_texts.extend([normalized_snapshot.market_summary.note, normalized_snapshot.flow_summary.note])
    for stance in normalized_stances:
        ticker_guard_texts.extend(stance.core_claims)
        ticker_guard_texts.append(stance.korean_comment)
    ticker_guard_texts.append(normalized_result.consensus)
    for key_point in normalized_result.key_points:
        ticker_guard_texts.append(key_point.point)
        ticker_guard_texts.extend(key_point.sources)
    for disagreement in normalized_result.disagreements:
        ticker_guard_texts.extend(
            [
                disagreement.topic,
                disagreement.majority,
                disagreement.minority,
                disagreement.why_it_matters,
            ]
        )
    for guidance in normalized_result.ops_guidance:
        ticker_guard_texts.append(guidance.text)
    _assert_no_unknown_tickers(ticker_guard_texts, normalized_snapshot.watchlist)

    if report is not None:
        validate_report(report)
