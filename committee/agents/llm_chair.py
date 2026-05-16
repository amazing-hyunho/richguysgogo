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
        return (
            "You are the CHAIR of an investment committee. Your job is two-fold:\n"
            "(A) Produce a structured consensus JSON, AND\n"
            "(B) Write a professional Korean market report in sugeup_narrative — "
            "similar to a sell-side equity strategist's daily note.\n\n"
            "Output JSON only. No markdown outside sugeup_narrative. "
            "All natural-language text must be in Korean.\n\n"
            "=== JSON SCHEMA ===\n"
            "Required keys: consensus, key_points, disagreements, ops_guidance, sugeup_narrative.\n"
            "consensus: one concise Korean sentence summarizing today's market regime.\n"
            "key_points: 1~3 items, each with keys 'point' (Korean, max 200 chars) and 'sources' (agent name list).\n"
            "disagreements: 1~3 items with keys topic, majority, minority, minority_agents, why_it_matters.\n"
            "ops_guidance: exactly 3 items with levels OK, CAUTION, AVOID and concise Korean text.\n\n"
            "=== sugeup_narrative FORMAT ===\n"
            "Plain text Korean. No bullet symbols, no markdown. "
            "Separate sections with a single blank line. "
            "MUST contain exactly these 5 sections in order, each as one paragraph:\n\n"
            "Section 1 — [핵심 판단]\n"
            "Open with a strong one-paragraph assessment of TODAY's market character. "
            "State whether it is a late-stage rally, an overheating clash, a healthy correction, etc. "
            "Cite the key numbers: KOSPI level/change, USD/KRW, VIX, foreign and retail net flows (억원). "
            "Do not overfit to one day — weigh the 5-day and 20-day cumulative context. "
            "IMPORTANT: Reference the most market-relevant news headlines from today's news_digest "
            "to explain WHY the market moved as it did. Name specific topics (e.g. 연준 발언, 엔비디아 실적, "
            "반도체 수급, 환율 정책) that are driving sentiment.\n\n"
            "Section 2 — [외국인 매도 이유]\n"
            "Explain foreign selling with 3 numbered reasons embedded naturally in prose (not bullet points). "
            "첫째: profit-taking after cumulative gain (cite KOSPI 5d/20d cumulative %). "
            "둘째: passive fund rebalancing when Korea/semiconductor weight exceeded index limits. "
            "셋째: FX pressure — when USD/KRW rises simultaneously with selling, it signals capital outflow not just rebalancing. "
            "Use actual numbers from the data for each reason.\n\n"
            "Section 3 — [개인 매수 이유와 리스크]\n"
            "Explain WHY retail investors are absorbing foreign supply "
            "(AI/semiconductor re-rating thesis, FOMO, domestic growth narrative). "
            "Then state the KEY RISK: if retail is buying on leverage, cite the implication "
            "(forced selling cascade if market drops X%). "
            "Assess whether the absorption pace is sustainable given current flow numbers.\n\n"
            "Section 4 — [시나리오 판단]\n"
            "Present 3 distinct scenarios as prose paragraphs (not a table): "
            "Scenario A (base case, most likely): describe trigger conditions, expected market move, probability characterization. "
            "Scenario B (bull continuation): what would have to be true, what confirms it. "
            "Scenario C (sharp correction): what catalyst breaks the current support, what to watch. "
            "Where relevant, tie scenarios to specific upcoming news events from today's headlines "
            "(e.g. FOMC minutes release, earnings results, policy announcements). "
            "End with which indicator to monitor first.\n\n"
            "Section 5 — [투자 관점 결론]\n"
            "Two-part conclusion: "
            "(1) For existing holders — whether to trim, hold, or add, with a specific rationale. "
            "(2) For new entrants — what signals must appear before entry (e.g. foreign net selling narrowing, "
            "USD/KRW stabilizing, VIX declining). "
            "Close with one memorable sentence that captures the essence of the current regime.\n\n"
            "Total sugeup_narrative length: 800~2000 Korean characters. "
            "Write with the depth and precision of a senior Korean equity strategist. "
            "Always reference the actual numeric data provided."
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

        # ── 핵심 수치 요약 블록 (의장이 보고서에 바로 인용하도록) ──
        key_figures: dict = {
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
            key_figures.update({
                "KOSPI_5d_cum_pct": cc.kospi_5d_cum_pct,
                "KOSPI_20d_cum_pct": cc.kospi_20d_cum_pct,
                "USDKRW_5d_change_pct": cc.usdkrw_5d_change_pct,
                "VIX_5d_avg": cc.vix_5d_avg,
                "KOSPI_abs_move_5d_avg": cc.kospi_abs_move_5d_avg,
                "reversal_signal": cc.reversal_signal,
                "cumulative_note": cc.note,
            })
        if macro:
            d = macro.daily
            key_figures.update({
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
            "KEY_FIGURES_FOR_REPORT": key_figures,
            "korean_market_flow_breakdown": (
                snapshot.korean_market_flow.model_dump() if snapshot.korean_market_flow else None
            ),
            "SP500_pct": m.us.sp500_pct,
            "NASDAQ_pct": m.us.nasdaq_pct,
            "DOW_pct": m.us.dow_pct,
            "news_digest": news_context,
            "sector_moves": snapshot.sector_moves,
        }
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
        payload = {
            "indicator_context": indicator_context,
            "agent_opinions": agent_opinions,
            "debate_round": debate_round.model_dump() if debate_round is not None else None,
        }
        return json.dumps(payload, ensure_ascii=False)
