from __future__ import annotations

"""LLM-powered chair agent with rule-based fallback."""

import json
import os
from dataclasses import dataclass
from pathlib import Path

from committee.agents.chair_stub import ChairStub
from committee.schemas.committee_result import CommitteeResult
from committee.schemas.debate import DebateRound
from committee.schemas.snapshot import Snapshot
from committee.schemas.stance import Stance
from committee.tools.openai_chat import chat_completion, load_openai_config


@dataclass(frozen=True)
class ChairLLMOptions:
    """Runtime options for chair LLM consensus."""

    model: str = "gpt-4.1-mini"
    temperature: float = 0.1


class LLMChairAgent:
    """Generate committee consensus via LLM, then validate schema."""

    def __init__(self, *, fallback_agent: ChairStub, options: ChairLLMOptions):
        self.fallback_agent = fallback_agent
        self.options = options

    def run(self, snapshot: Snapshot, stances: list[Stance], debate_round: DebateRound | None = None) -> CommitteeResult:
        """Return a strict CommitteeResult with safe fallback on any error."""

        try:
            config = load_openai_config()
            system_prompt = self._system_prompt()
            user_prompt = self._user_prompt(snapshot=snapshot, stances=stances, debate_round=debate_round)
            raw = chat_completion(
                config=config,
                model=self.options.model,
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=self.options.temperature,
            )
            parsed = json.loads(raw)
            return CommitteeResult.model_validate(parsed)
        except Exception:
            return self.fallback_agent.run(stances)

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
            "disagreements: 1~3 items with keys topic, majority, minority, minority_agents, why_it_matters.\n"
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
        if agent_opinions is not None:
            payload["agent_opinions"] = agent_opinions
        return json.dumps(payload, ensure_ascii=False)
