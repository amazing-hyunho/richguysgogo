from __future__ import annotations

"""LLM-powered chair agent with rule-based fallback."""

import json
import os
import time
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from committee.agents.chair_stub import ChairStub
from committee.schemas.committee_result import AnalysisStatus, CommitteeResult
from committee.schemas.debate import DebateRound
from committee.schemas.snapshot import Snapshot
from committee.schemas.stance import RegimeTag, Stance
from committee.core.trace_logger import TraceLogger
from committee.future_economy.context import load_latest_committee_agenda
from committee.tools.openai_chat import load_openai_config, responses_completion_with_metadata


_REASONING_EFFORTS = {"none", "low", "medium", "high", "xhigh", "max"}


def _env_flag(name: str, default: bool = False) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def _env_float(name: str, default: float) -> float:
    try:
        return float(os.getenv(name, str(default)))
    except (TypeError, ValueError):
        return default


def _env_int(name: str, default: int, *, minimum: int, maximum: int) -> int:
    try:
        value = int(os.getenv(name, str(default)))
    except (TypeError, ValueError):
        return default
    return max(minimum, min(maximum, value))


def _env_reasoning_effort(name: str, default: str) -> str:
    value = os.getenv(name, default).strip().lower() or default
    return value if value in _REASONING_EFFORTS else default


@dataclass(frozen=True)
class ChairLLMOptions:
    """Runtime options for chair LLM consensus."""

    model: str = "gpt-5.6-terra"
    escalation_model: str = "gpt-5.6-sol"
    reasoning_effort: str = "medium"
    escalation_reasoning_effort: str = "medium"
    force_escalation: bool = False
    urgent_flag: bool = False
    report_mode: str = "daily"
    vix_escalation_threshold: float = 30.0
    kospi_move_escalation_pct: float = 3.0
    usdkrw_move_escalation_pct: float = 1.5
    source_conflict_threshold_pct: float = 0.5
    timeout_sec: int = 180
    same_model_retries: int = 1
    retry_model: str = "gpt-5.6-luna"
    retry_reasoning_effort: str = "low"

    @classmethod
    def from_env(cls) -> "ChairLLMOptions":
        """Build the chair's tiered model policy from environment variables."""

        return cls(
            model=os.getenv("CHAIR_OPENAI_MODEL", "gpt-5.6-terra").strip()
            or "gpt-5.6-terra",
            escalation_model=os.getenv(
                "CHAIR_ESCALATION_MODEL", "gpt-5.6-sol"
            ).strip()
            or "gpt-5.6-sol",
            reasoning_effort=_env_reasoning_effort(
                "CHAIR_REASONING_EFFORT", "medium"
            ),
            escalation_reasoning_effort=_env_reasoning_effort(
                "CHAIR_ESCALATION_REASONING_EFFORT", "medium"
            ),
            force_escalation=_env_flag("CHAIR_FORCE_SOL"),
            urgent_flag=_env_flag("CHAIR_URGENT_FLAG"),
            report_mode=os.getenv("CHAIR_REPORT_MODE", "daily").strip().lower()
            or "daily",
            vix_escalation_threshold=_env_float(
                "CHAIR_ESCALATION_VIX", 30.0
            ),
            kospi_move_escalation_pct=_env_float(
                "CHAIR_ESCALATION_KOSPI_PCT", 3.0
            ),
            usdkrw_move_escalation_pct=_env_float(
                "CHAIR_ESCALATION_USDKRW_PCT", 1.5
            ),
            source_conflict_threshold_pct=_env_float(
                "CHAIR_SOURCE_CONFLICT_PCT", 0.5
            ),
            timeout_sec=_env_int(
                "CHAIR_TIMEOUT_SEC", 180, minimum=30, maximum=600
            ),
            same_model_retries=_env_int(
                "CHAIR_SAME_MODEL_RETRIES", 1, minimum=0, maximum=2
            ),
            retry_model=os.getenv("CHAIR_RETRY_MODEL", "gpt-5.6-luna").strip()
            or "gpt-5.6-luna",
            retry_reasoning_effort=_env_reasoning_effort(
                "CHAIR_RETRY_REASONING_EFFORT", "low"
            ),
        )


@dataclass(frozen=True)
class ChairModelSelection:
    """Auditable result of deterministic chair model routing."""

    model: str
    reasoning_effort: str
    escalated: bool
    reasons: tuple[str, ...]


def select_chair_model(
    *,
    snapshot: Snapshot,
    stances: list[Stance],
    debate_round: DebateRound | None,
    options: ChairLLMOptions,
) -> ChairModelSelection:
    """Select Terra normally and Sol only for bounded, observable conditions."""

    reasons: list[str] = []
    if options.force_escalation:
        reasons.append("forced")
    if options.urgent_flag:
        reasons.append("urgent_flag")
    if options.report_mode in {"monthly", "month", "monthly_report"}:
        reasons.append("monthly_report")

    cumulative = snapshot.cumulative_context
    if cumulative is not None and cumulative.reversal_signal:
        reasons.append("regime_reversal")

    stance_tags = {stance.regime_tag for stance in stances}
    if RegimeTag.RISK_ON in stance_tags and RegimeTag.RISK_OFF in stance_tags:
        reasons.append("agent_regime_conflict")

    if debate_round is not None:
        debate_tags = {minute.internal_regime_tag for minute in debate_round.minutes}
        if RegimeTag.RISK_ON in debate_tags and RegimeTag.RISK_OFF in debate_tags:
            reasons.append("debate_regime_conflict")

    markets = snapshot.markets
    if markets.volatility.vix >= options.vix_escalation_threshold:
        reasons.append("vix_stress")
    if abs(markets.kr.kospi_pct) >= options.kospi_move_escalation_pct:
        reasons.append("kospi_shock")
    if abs(markets.fx.usdkrw_pct) >= options.usdkrw_move_escalation_pct:
        reasons.append("fx_shock")

    if (
        abs(snapshot.market_summary.kospi_change_pct - markets.kr.kospi_pct)
        >= options.source_conflict_threshold_pct
    ):
        reasons.append("kospi_source_conflict")
    if snapshot.market_summary.usdkrw:
        usdkrw_gap_pct = abs(
            (markets.fx.usdkrw - snapshot.market_summary.usdkrw)
            / snapshot.market_summary.usdkrw
            * 100.0
        )
        if usdkrw_gap_pct >= options.source_conflict_threshold_pct:
            reasons.append("usdkrw_source_conflict")

    # Opposing core signals must be broad enough to avoid escalating on ordinary noise.
    risk_on_signals = sum(
        (
            markets.kr.kospi_pct >= 0.7,
            markets.fx.usdkrw_pct <= -0.5,
            0.0 < markets.volatility.vix <= 18.0,
            snapshot.flow_summary.foreign_net >= 2000.0,
        )
    )
    risk_off_signals = sum(
        (
            markets.kr.kospi_pct <= -0.7,
            markets.fx.usdkrw_pct >= 0.5,
            markets.volatility.vix >= 25.0,
            snapshot.flow_summary.foreign_net <= -2000.0,
        )
    )
    if risk_on_signals >= 2 and risk_off_signals >= 2:
        reasons.append("core_signal_conflict")

    unique_reasons = tuple(dict.fromkeys(reasons))
    escalated = bool(unique_reasons)
    return ChairModelSelection(
        model=options.escalation_model if escalated else options.model,
        reasoning_effort=(
            options.escalation_reasoning_effort
            if escalated
            else options.reasoning_effort
        ),
        escalated=escalated,
        reasons=unique_reasons,
    )


class LLMChairAgent:
    """Generate committee consensus via LLM, then validate schema."""

    def __init__(self, *, fallback_agent: ChairStub, options: ChairLLMOptions):
        self.fallback_agent = fallback_agent
        self.options = options

    def run(self, snapshot: Snapshot, stances: list[Stance], debate_round: DebateRound | None = None) -> CommitteeResult:
        """Return a strict CommitteeResult with safe fallback on any error."""

        selection = select_chair_model(
            snapshot=snapshot,
            stances=stances,
            debate_round=debate_round,
            options=self.options,
        )
        trace = TraceLogger(os.getenv("LLM_TRACE_PATH"))
        trace.log(
            "chair_model_routing",
            {
                "model": selection.model,
                "reasoning_effort": selection.reasoning_effort,
                "escalated": selection.escalated,
                "reasons": list(selection.reasons),
                "timeout_sec": self.options.timeout_sec,
                "same_model_retries": self.options.same_model_retries,
                "retry_model": self.options.retry_model,
            },
        )
        try:
            config = load_openai_config()
        except Exception as exc:
            return self._fallback_result(
                snapshot=snapshot,
                stances=stances,
                trace=trace,
                requested_model=selection.model,
                errors=[exc],
            )

        system_prompt = self._system_prompt()
        user_prompt = self._user_prompt(
            snapshot=snapshot,
            stances=stances,
            debate_round=debate_round,
        )
        attempts: list[tuple[str, str, str]] = [
            ("primary", selection.model, selection.reasoning_effort)
        ]
        attempts.extend(
            (f"same_model_retry_{index + 1}", selection.model, selection.reasoning_effort)
            for index in range(self.options.same_model_retries)
        )
        attempts.append(
            (
                "recovery_model",
                self.options.retry_model,
                self.options.retry_reasoning_effort,
            )
        )

        errors: list[Exception] = []
        for attempt_index, (attempt_kind, model, effort) in enumerate(attempts, start=1):
            started_at = time.perf_counter()
            response = None
            trace.log(
                "chair_model_attempt",
                {
                    "attempt": attempt_index,
                    "attempts_total": len(attempts),
                    "attempt_kind": attempt_kind,
                    "model": model,
                    "reasoning_effort": effort,
                    "timeout_sec": self.options.timeout_sec,
                },
            )
            try:
                response = responses_completion_with_metadata(
                    config=config,
                    model=model,
                    system_prompt=system_prompt,
                    user_prompt=user_prompt,
                    reasoning_effort=effort,
                    timeout=self.options.timeout_sec,
                )
                elapsed_sec = round(time.perf_counter() - started_at, 3)
                trace.log(
                    "chair_model_response",
                    {
                        "attempt": attempt_index,
                        "attempt_kind": attempt_kind,
                        "requested_model": model,
                        "response_model": response.model,
                        "request_id": response.request_id,
                        "reasoning_effort": effort,
                        "elapsed_sec": elapsed_sec,
                        "input_tokens": response.input_tokens,
                        "output_tokens": response.output_tokens,
                    },
                )
                parsed = json.loads(response.content)
                repaired, repairs = self._repair_payload(parsed)
                result = CommitteeResult.model_validate(repaired)
                recovered = attempt_index > 1 or bool(repairs)
                note_parts: list[str] = []
                if attempt_index > 1:
                    note_parts.append(f"{attempt_index}번째 호출에서 복구")
                if repairs:
                    note_parts.append("응답 형식 자동 보정")
                    trace.log(
                        "chair_response_repaired",
                        {
                            "attempt": attempt_index,
                            "repairs": repairs,
                        },
                    )
                result = self._with_status(
                    result,
                    status=(
                        AnalysisStatus.RECOVERED
                        if recovered
                        else AnalysisStatus.COMPLETE
                    ),
                    note=" · ".join(note_parts) or None,
                )
                trace.log(
                    "chair_run_status",
                    {
                        "status": result.analysis_status.value,
                        "attempt": attempt_index,
                        "model": model,
                        "note": result.analysis_note,
                    },
                )
                return result
            except Exception as exc:
                errors.append(exc)
                trace.log(
                    "chair_model_attempt_failed",
                    {
                        "attempt": attempt_index,
                        "attempt_kind": attempt_kind,
                        "requested_model": model,
                        "reasoning_effort": effort,
                        "elapsed_sec": round(time.perf_counter() - started_at, 3),
                        "error_type": type(exc).__name__,
                        "error": str(exc)[:500],
                        "response_preview": (
                            response.content[:2000] if response is not None else None
                        ),
                    },
                )

        return self._fallback_result(
            snapshot=snapshot,
            stances=stances,
            trace=trace,
            requested_model=selection.model,
            errors=errors,
        )

    @staticmethod
    def _repair_payload(payload: object) -> tuple[object, list[str]]:
        """Repair only bounded, non-semantic chair response shape errors."""

        if not isinstance(payload, dict):
            return payload, []
        repaired = dict(payload)
        repairs: list[str] = []
        disagreements = repaired.get("disagreements")
        if isinstance(disagreements, list):
            repaired_disagreements: list[object] = []
            for index, item in enumerate(disagreements):
                if not isinstance(item, dict):
                    repaired_disagreements.append(item)
                    continue
                normalized = dict(item)
                if not normalized.get("minority_agents"):
                    normalized["minority_agents"] = ["출처 미지정"]
                    repairs.append(f"disagreements.{index}.minority_agents")
                repaired_disagreements.append(normalized)
            repaired["disagreements"] = repaired_disagreements
        return repaired, repairs

    @staticmethod
    def _with_status(
        result: CommitteeResult,
        *,
        status: AnalysisStatus,
        note: str | None,
    ) -> CommitteeResult:
        payload = result.model_dump()
        payload["analysis_status"] = status
        payload["analysis_note"] = note
        return CommitteeResult.model_validate(payload)

    def _fallback_result(
        self,
        *,
        snapshot: Snapshot,
        stances: list[Stance],
        trace: TraceLogger,
        requested_model: str,
        errors: list[Exception],
    ) -> CommitteeResult:
        fallback = self.fallback_agent.run(stances)
        payload = fallback.model_dump()
        payload["sugeup_narrative"] = self._fallback_narrative(snapshot)
        payload["analysis_status"] = AnalysisStatus.FALLBACK
        payload["analysis_note"] = "의장 AI 호출 실패 · 규칙 기반 대체"
        result = CommitteeResult.model_validate(payload)
        last_error = errors[-1] if errors else RuntimeError("unknown_chair_failure")
        trace.log(
            "chair_model_fallback",
            {
                "requested_model": requested_model,
                "attempt_count": len(errors),
                "error_type": type(last_error).__name__,
                "error": str(last_error)[:500],
            },
        )
        trace.log(
            "chair_run_status",
            {
                "status": AnalysisStatus.FALLBACK.value,
                "attempt_count": len(errors),
                "note": result.analysis_note,
            },
        )
        return result

    @staticmethod
    def _fallback_narrative(snapshot: Snapshot) -> str:
        markets = snapshot.markets
        flow = snapshot.flow_summary
        cumulative = snapshot.cumulative_context
        cumulative_line = "누적 흐름은 제공 데이터만으로 확인이 제한됩니다."
        if cumulative is not None:
            cumulative_line = (
                f"KOSPI 5일 누적 {cumulative.kospi_5d_cum_pct:+.2f}%, "
                f"20일 누적 {cumulative.kospi_20d_cum_pct:+.2f}%, "
                f"VIX 5일 평균 {cumulative.vix_5d_avg:.2f}입니다."
            )
        return (
            "## 분석 상태 안내\n\n"
            "의장 AI 응답을 최종 검증하지 못해 아래 내용은 수집된 수치만으로 만든 규칙 기반 대체 분석입니다. "
            "장문 AI 해석으로 간주하지 말고 데이터 확인용으로 사용해야 합니다.\n\n"
            "## 시장과 수급\n\n"
            f"KOSPI는 {markets.kr.kospi_pct:+.2f}%, KOSDAQ은 {markets.kr.kosdaq_pct:+.2f}% 움직였습니다. "
            f"원/달러 환율은 {markets.fx.usdkrw:.2f}, VIX는 {markets.volatility.vix:.2f}입니다. "
            f"전체 수급은 외국인 {flow.foreign_net:+.0f}억원, 기관 {flow.institution_net:+.0f}억원, "
            f"개인 {flow.retail_net:+.0f}억원입니다.\n\n"
            "## 누적 흐름과 대응\n\n"
            f"{cumulative_line} AI 의장 판단이 복구되기 전에는 새로운 강한 방향성 결론을 추가하지 않고, "
            "환율·외국인 수급·변동성의 동시 악화 여부를 우선 확인합니다."
        )

    @staticmethod
    def _system_prompt() -> str:
        use_llm_agents = os.getenv("USE_LLM_AGENTS", "0").strip() == "1"
        agent_instruction = (
            "Base your analysis on three sources of evidence: "
            "(1) numeric market data and macro indicators, "
            "(2) today's news headlines and digest, "
            "(3) agent opinions provided — reference agent names and their claims where relevant."
        ) if use_llm_agents else (
            "Base your entire analysis on the numeric market data, flow figures, macro indicators, "
            "and today's news headlines and digest provided. "
            "Do NOT invent agent opinions — none are provided."
        )
        return (
            "You are the CHAIR of an investment committee. Your job is two-fold:\n"
            "(A) Produce a structured consensus JSON, AND\n"
            "(B) Write a professional Korean market report in sugeup_narrative — "
            "similar to a sell-side equity strategist's daily note.\n\n"
            f"{agent_instruction}\n\n"
            "=== HARD DATA GROUNDING RULES (MUST FOLLOW) ===\n"
            "Use ONLY values explicitly provided in indicator_context.KEY_FIGURES_FOR_REPORT and other payload fields.\n"
            "Do NOT infer, estimate, back-calculate, or invent any index level/price/flow number.\n"
            "If a required value is missing or null, write '확인 불가(제공 데이터 기준)' instead of guessing.\n"
            "When mentioning KOSPI/KOSDAQ point levels, use ONLY KOSPI_level_today / KOSDAQ_level_today from payload.\n"
            "Do NOT mix historical memory or external knowledge. Treat payload as the single source of truth for today's report.\n\n"
            "=== FUTURE ECONOMY CONTEXT RULE ===\n"
            "future_economy_context contains verified weekly research agendas, not current market signals or trading orders. "
            "Use an item only when today's macro/flow evidence makes it relevant, state conflicts explicitly, and never invent "
            "a company, source, fact, order, position size, or automatic-trading action. If the context is empty, ignore it.\n\n"
            "=== PRIORITY / CONFLICT RULES ===\n"
            "You are given two evidence buckets: CORE_SIGNALS and SUPPORTING_SIGNALS.\n"
            "CORE_SIGNALS drive the main thesis. SUPPORTING_SIGNALS are for confirmation or rebuttal only.\n"
            "If core and supporting conflict, do NOT change core thesis immediately.\n"
            "Instead: (1) keep the core thesis, (2) mention the conflict explicitly, (3) lower confidence and state watchpoints.\n"
            "In the final conclusion, always state one invalidation condition that would break today's thesis.\n\n"
            "Output JSON only. "
            "All natural-language text must be in Korean.\n\n"
            "=== JSON SCHEMA ===\n"
            "Required keys: consensus, key_points, disagreements, ops_guidance, sugeup_narrative.\n"
            "consensus: one concise Korean sentence summarizing today's market regime.\n"
            "key_points: 1~3 items, each with keys 'point' (Korean, max 200 chars) and 'sources' "
            "(list of data sources used, e.g. ['flow_data', 'news', 'macro_daily'] — not agent names unless USE_LLM_AGENTS is on).\n"
            "disagreements: 1~3 items with keys topic, majority, minority, minority_agents, why_it_matters. "
            "minority_agents MUST contain 1~5 non-empty strings; when no named agent exists, use ['해당 없음'] and never [].\n"
            "ops_guidance: exactly 3 items with levels OK, CAUTION, AVOID and concise Korean text.\n\n"
            "=== sugeup_narrative FORMAT ===\n"
            "Korean Markdown text (headings, bullet points, links allowed). "
            "Use '##' headings for each section and separate sections with a blank line. "
            "Write a DAILY macro/flow issue report, not a fixed-template foreign-selling report. "
            "The section titles MUST vary by the day's dominant issues. Do NOT reuse a fixed 5-section template. "
            "Use 3~5 sections only, and choose section titles from today's actual 핵심 키워드. "
            "Every report MUST include these ingredients, but the headings/order may change naturally:\n"
            "(1) one opening section with today's market character and key numbers "
            "(KOSPI/KOSDAQ level or change, USD/KRW, VIX, foreign/institution/retail net flows in 억원); "
            "(2) one 수급 해석 section that explains who dominated flows and WHY, linking the flow to macro/news keywords; "
            "(3) one 날짜별 핵심 이슈 section that ranks or groups 2~4 issues from today's news_digest/headlines "
            "(e.g. 연준/금리, 환율/달러, 반도체/AI, GDP/성장, 정책/관세, 지정학); "
            "(4) one implication section explaining what to watch next and what condition invalidates the thesis. "
            "If foreign selling is not the dominant issue, do NOT force an '외국인 매도 이유' section. "
            "If retail buying is not central, mention it briefly instead of creating a separate retail section. "
            "Use cumulative_context (5d/20d KOSPI, USD/KRW 5d, VIX 5d) to avoid overreacting to one day. "
            "Tie each major conclusion to actual numbers and at least one news keyword. "
            "The report should feel like it was written for TODAY specifically, so repeated generic section titles are discouraged.\n\n"
            "=== NEWS EVIDENCE RULE ===\n"
            "When citing news as evidence, include markdown links inline using this format: "
            "[기사 제목](https://...). "
            "Include at least 2 linked news references in sugeup_narrative when news links are available.\n\n"
            "Total sugeup_narrative length: 800~2000 Korean characters. "
            "Write with the depth and precision of a senior Korean equity strategist. "
            "Always reference the actual numeric data provided. "
            "Write concise and highly readable Korean for retail investors (short paragraphs, clear transitions, minimal jargon)."
        )

    @staticmethod
    def _load_news_digest() -> dict:
        """Load latest news digest for richer headline context. Best-effort."""
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
                        "total_collected": data.get("total_collected", 0),
                        "topic_counts": data.get("topic_counts", []),
                        "top_headlines_by_topic": [
                            {
                                "topic": a.get("topic", ""),
                                "title": a.get("title", ""),
                                "summary": a.get("summary_lines", []),
                                "link": a.get("link", ""),
                            }
                            for a in data.get("top_articles", [])[:15]
                        ],
                    }
                except Exception:
                    pass
        return {}

    @staticmethod
    def _user_prompt(snapshot: Snapshot, stances: list[Stance], debate_round: DebateRound | None = None) -> str:
        m = snapshot.markets
        macro = snapshot.macro
        cc = snapshot.cumulative_context

        # ── 핵심 신호(Core): 본문 논지를 직접 결정하는 지표 ──
        core_signals: dict = {
            "KOSPI_level_today": m.kr.kospi,
            "KOSDAQ_level_today": m.kr.kosdaq,
            "KOSPI_pct_today": m.kr.kospi_pct,
            "KOSDAQ_pct_today": m.kr.kosdaq_pct,
            "USDKRW": m.fx.usdkrw,
            "USDKRW_pct": m.fx.usdkrw_pct,
            "VIX": m.volatility.vix,
            "foreign_net_eok": snapshot.flow_summary.foreign_net,
            "institution_net_eok": snapshot.flow_summary.institution_net,
            "retail_net_eok": snapshot.flow_summary.retail_net,
            "flow_note": snapshot.flow_summary.note,
            "market_note": snapshot.market_summary.note,
        }
        if cc is not None:
            core_signals.update({
                "KOSPI_5d_cum_pct": cc.kospi_5d_cum_pct,
                "KOSPI_20d_cum_pct": cc.kospi_20d_cum_pct,
                "USDKRW_5d_change_pct": cc.usdkrw_5d_change_pct,
                "VIX_5d_avg": cc.vix_5d_avg,
                "KOSPI_abs_move_5d_avg": cc.kospi_abs_move_5d_avg,
                "reversal_signal": cc.reversal_signal,
                "cumulative_note": cc.note,
            })

        # ── 보조 신호(Supporting): 논지 확인/반증용 지표 ──
        supporting_signals: dict = {
            "SP500_level_today": m.us.sp500,
            "NASDAQ_level_today": m.us.nasdaq,
            "DOW_level_today": m.us.dow,
            "SP500_pct_today": m.us.sp500_pct,
            "NASDAQ_pct_today": m.us.nasdaq_pct,
            "DOW_pct_today": m.us.dow_pct,
            "sector_moves": snapshot.sector_moves,
        }
        if macro:
            d = macro.daily
            supporting_signals.update({
                "US10Y": d.us10y,
                "US2Y": d.us2y,
                "spread_2_10": d.spread_2_10,
                "DXY": d.dxy,
                "oil_WTI": d.oil_wti,
                "HY_OAS": macro.structural.hy_oas,
                "fed_funds_rate": macro.structural.fed_funds_rate,
                "real_rate": macro.structural.real_rate,
                "CPI_yoy": macro.monthly.cpi_yoy,
                "PMI": macro.monthly.pmi,
                "unemployment": macro.monthly.unemployment_rate,
                "GDP_qoq_annualized": macro.quarterly.gdp_qoq_annualized,
            })

        # 뉴스: 스냅샷 헤드라인(단순 목록) + 다이제스트(토픽별 분류) 병합
        news_digest = LLMChairAgent._load_news_digest()
        news_context: dict = {
            "snapshot_headlines": snapshot.news_headlines[:20],
        }
        if news_digest:
            news_context["digest"] = news_digest

        indicator_context = {
            "report_date_context": {
                "news_date": news_digest.get("news_date") if news_digest else None,
                "korean_flow_date": (
                    snapshot.korean_market_flow.date if snapshot.korean_market_flow is not None else None
                ),
            },
            "KEY_FIGURES_FOR_REPORT": {
                "CORE_SIGNALS": core_signals,
                "SUPPORTING_SIGNALS": supporting_signals,
            },
            "korean_market_flow_breakdown": (
                snapshot.korean_market_flow.model_dump() if snapshot.korean_market_flow else None
            ),
            "news_digest": news_context,
        }
        # USE_LLM_AGENTS=0이면 에이전트 의견은 규칙 기반 stub 출력이므로
        # 의장에게 전달하지 않는다. 의장은 수치 데이터와 뉴스만으로 판단한다.
        use_llm_agents = os.getenv("USE_LLM_AGENTS", "0").strip() == "1"
        if use_llm_agents:
            agent_opinions = [
                {
                    "agent_name": stance.agent_name.value,
                    "regime_tag": stance.regime_tag.value,
                    "confidence": stance.confidence.value,
                    "core_claims": stance.core_claims,
                    "korean_comment": stance.korean_comment,
                }
                for stance in stances
            ]
        else:
            agent_opinions = None  # stub 의견은 의장에게 전달하지 않음

        payload = {
            "indicator_context": indicator_context,
            "debate_round": debate_round.model_dump() if debate_round is not None else None,
        }
        context_date_raw = (
            snapshot.korean_market_flow.date
            if snapshot.korean_market_flow is not None
            else (news_digest.get("news_date") if news_digest else None)
        )
        try:
            context_date = date.fromisoformat(str(context_date_raw))
        except (TypeError, ValueError):
            context_date = date.today()
        runs_dir = Path(os.getenv("RUNS_BASE_DIR", "runs"))
        if not runs_dir.is_absolute():
            runs_dir = Path(__file__).resolve().parents[2] / runs_dir
        payload["future_economy_context"] = load_latest_committee_agenda(
            runs_dir=runs_dir,
            as_of=context_date,
            max_age_days=14,
        )
        if agent_opinions is not None:
            payload["agent_opinions"] = agent_opinions
        return json.dumps(payload, ensure_ascii=False)
