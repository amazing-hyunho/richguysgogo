from __future__ import annotations

# Core daily pipeline orchestration.

from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import List
import os

from committee.agents.flow_stub import FlowStub
from committee.agents.chair_stub import ChairStub
from committee.agents.llm_pre_analysis import LLMPreAnalysisAgent, LLMRunOptions
from committee.agents.macro_stub import MacroStub
from committee.agents.model_profiles import ModelBackend, parse_backend
from committee.agents.risk_stub import RiskStub
from committee.agents.sector_stub import SectorStub
from committee.core.report_renderer import Report, build_report, render_report
from committee.core.database import (
    safe_upsert_daily_macro,
    safe_upsert_market_daily,
    safe_upsert_market_flow_daily,
    safe_upsert_monthly_macro,
    safe_upsert_quarterly_macro,
)
from committee.core.storage import save_run
from committee.core.trace_logger import TraceLogger
from committee.core.snapshot_builder import build_snapshot, get_last_snapshot_status
from committee.schemas.committee_result import CommitteeResult
from committee.schemas.stance import AgentName, Stance


def run_pre_analysis(snapshot: object, agent_ids: List[str]) -> List[Stance]:
    """Generate stances from configured agent IDs (stub or LLM)."""
    backend = parse_backend(os.getenv("AGENT_MODEL_BACKEND", "openai"))
    use_llm_agents = os.getenv("USE_LLM_AGENTS", "0").strip() == "1"
    options = LLMRunOptions(backend=backend, temperature=float(os.getenv("LLM_TEMPERATURE", "0.1")))

    stances: List[Stance] = []
    for agent_id in agent_ids:
        agent_name = AgentName(agent_id)
        agent = _build_pre_analysis_agent(agent_name, use_llm_agents=use_llm_agents, options=options)
        stances.append(agent.run(snapshot))
    return stances


def _build_pre_analysis_agent(agent_name: AgentName, use_llm_agents: bool, options: LLMRunOptions):
    """Build one pre-analysis agent instance for the requested ID."""
    fallback_map = {
        AgentName.MACRO: MacroStub(),
        AgentName.FLOW: FlowStub(),
        AgentName.SECTOR: SectorStub(),
        AgentName.RISK: RiskStub(),
    }
    fallback_agent = fallback_map[agent_name]
    if use_llm_agents and options.backend == ModelBackend.OPENAI:
        return LLMPreAnalysisAgent(agent_name=agent_name, fallback_agent=fallback_agent, options=options)
    return fallback_agent


def run_committee(snapshot: object, stances: List[Stance]) -> CommitteeResult:
    """Generate committee result from stance distribution via ChairStub."""
    _ = snapshot  # reserved for future chair rules that inspect snapshot directly
    return ChairStub().run(stances)


@dataclass(frozen=True)
class DailyPipeline:
    """Pipeline runner for daily snapshot-to-report flow."""
    agent_ids: List[str]

    def run(self, market_date: date, output_dir: Path) -> Report:
        """Run the full pipeline and write the report."""
        trace = TraceLogger(os.getenv("LLM_TRACE_PATH"))
        print("[pipeline] stage 1/5: build snapshot")
        snapshot = build_snapshot(market_date)
        status = get_last_snapshot_status()
        trace.log("pipeline_stage", {"stage": "snapshot_built", "market_date": market_date.isoformat(), "status": status})
        # DB persistence layer (additive): best-effort upsert.
        # Must not break the existing pipeline even if DB is unavailable/locked.
        # Data integrity: use NULL (not 0.0) for missing/unavailable/not-implemented values.
        usdkrw_pct_db = snapshot.markets.fx.usdkrw_pct if status.get("usdkrw_pct") == "OK" else None
        # Not implemented yet: explicitly store NULL rather than 0.0 placeholders.
        us10y_db = None
        vix_db = snapshot.markets.volatility.vix if status.get("vix") == "OK" else None
        safe_upsert_market_daily(
            date=market_date.isoformat(),
            kospi_pct=snapshot.markets.kr.kospi_pct,
            kosdaq_pct=snapshot.markets.kr.kosdaq_pct,
            sp500_pct=snapshot.markets.us.sp500_pct,
            nasdaq_pct=snapshot.markets.us.nasdaq_pct,
            dow_pct=snapshot.markets.us.dow_pct,
            usdkrw=snapshot.markets.fx.usdkrw,
            usdkrw_pct=usdkrw_pct_db,
            us10y=us10y_db,
            vix=vix_db,
        )
        foreign_net_db = snapshot.flow_summary.foreign_net if status.get("flows") == "OK" else None
        safe_upsert_market_flow_daily(
            date=market_date.isoformat(),
            foreign_net=foreign_net_db,
        )

        # Macro engine persistence (additive). Values are Optional in snapshot.macro and map to NULL in DB.
        if snapshot.macro is not None:
            d = snapshot.macro.daily
            m = snapshot.macro.monthly
            q = snapshot.macro.quarterly
            s = snapshot.macro.structural

            safe_upsert_daily_macro(
                date=market_date.isoformat(),
                us10y=d.us10y,
                us2y=d.us2y,
                spread_2_10=d.spread_2_10,
                vix=d.vix,
                dxy=d.dxy,
                usdkrw=d.usdkrw,
                fed_funds_rate=s.fed_funds_rate,
                real_rate=s.real_rate,
            )
            safe_upsert_monthly_macro(
                date=market_date.isoformat(),
                unemployment_rate=m.unemployment_rate,
                cpi_yoy=m.cpi_yoy,
                core_cpi_yoy=m.core_cpi_yoy,
                pce_yoy=m.pce_yoy,
                pmi=m.pmi,
                wage_level=m.wage_level,
                wage_yoy=m.wage_yoy,
            )
            safe_upsert_quarterly_macro(
                date=market_date.isoformat(),
                real_gdp=q.real_gdp,
                gdp_qoq_annualized=q.gdp_qoq_annualized,
            )
        print("[pipeline] stage 2/5: run pre-analysis")
        stances = run_pre_analysis(snapshot, self.agent_ids)
        trace.log("pipeline_stage", {"stage": "stances_built", "count": len(stances)})

        print("[pipeline] stage 3/5: run committee")
        committee_result = run_committee(snapshot, stances)
        trace.log("pipeline_stage", {"stage": "committee_result_built", "consensus": committee_result.consensus})

        print("[pipeline] stage 4/5: build report")
        report = build_report(
            market_date=market_date.isoformat(),
            snapshot=snapshot,
            stances=stances,
            committee_result=committee_result,
        )

        output_path = output_dir / f"{market_date.isoformat()}.json"
        print("[pipeline] stage 5/5: persist artifacts")
        render_report(report, output_path)
        run_dir = save_run(output_dir, market_date, snapshot, stances, committee_result, report)
        trace.log("pipeline_stage", {"stage": "artifacts_saved", "run_dir": str(run_dir), "report_json": str(output_path)})
        return report
