from __future__ import annotations

# Core daily pipeline orchestration.

from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import List
import os

from committee.agents.flow_stub import FlowStub
from committee.agents.debate_stub import DebateStub
from committee.agents.earnings_stub import EarningsStub
from committee.agents.breadth_stub import BreadthStub
from committee.agents.liquidity_stub import LiquidityStub
from committee.agents.chair_stub import ChairStub
from committee.agents.llm_chair import ChairLLMOptions, LLMChairAgent
from committee.agents.llm_pre_analysis import LLMPreAnalysisAgent, LLMRunOptions
from committee.agents.macro_stub import MacroStub
from committee.agents.model_profiles import ModelBackend, parse_backend
from committee.agents.risk_stub import RiskStub
from committee.agents.sector_stub import SectorStub
from committee.core.report_renderer import Report, build_report, render_report
from committee.core.regime_tuner import tune_committee_result
from committee.core.market_collector import persist_snapshot_metrics
from committee.core.storage import save_run
from committee.core.trace_logger import TraceLogger
from committee.core.snapshot_builder import build_snapshot, get_last_snapshot_status
from committee.schemas.committee_result import CommitteeResult
from committee.schemas.debate import DebateRound
from committee.schemas.snapshot import Snapshot
from committee.schemas.stance import AgentName, Stance


def run_pre_analysis(snapshot: Snapshot, agent_ids: List[str]) -> List[Stance]:
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
        AgentName.EARNINGS: EarningsStub(),
        AgentName.BREADTH: BreadthStub(),
        AgentName.LIQUIDITY: LiquidityStub(),
    }
    fallback_agent = fallback_map[agent_name]
    if use_llm_agents and options.backend == ModelBackend.OPENAI:
        return LLMPreAnalysisAgent(agent_name=agent_name, fallback_agent=fallback_agent, options=options)
    return fallback_agent


def run_committee(snapshot: Snapshot, stances: List[Stance], debate_round: DebateRound | None = None) -> CommitteeResult:
    """Generate committee result from stances, with optional LLM chair."""
    chair_stub = ChairStub()
    use_llm_chair = os.getenv("USE_LLM_CHAIR", "0").strip() == "1"
    if use_llm_chair:
        chair = LLMChairAgent(
            fallback_agent=chair_stub,
            options=ChairLLMOptions(
                model=os.getenv("CHAIR_OPENAI_MODEL", "gpt-4.1-mini").strip() or "gpt-4.1-mini",
                temperature=float(os.getenv("CHAIR_LLM_TEMPERATURE", "0.1")),
            ),
        )
        raw_result = chair.run(snapshot, stances, debate_round=debate_round)
        return tune_committee_result(snapshot, stances, raw_result)
    raw_result = chair_stub.run(stances)
    return tune_committee_result(snapshot, stances, raw_result)


def run_debate(snapshot: Snapshot, stances: List[Stance]) -> DebateRound | None:
    """Run optional one-round agent debate before chair synthesis."""
    use_debate = os.getenv("USE_AGENT_DEBATE", "0").strip() == "1"
    if not use_debate:
        return None
    return DebateStub().run(snapshot, stances)


@dataclass(frozen=True)
class DailyPipeline:
    """Pipeline runner for daily snapshot-to-report flow."""
    agent_ids: List[str]

    def run(self, market_date: date, output_dir: Path) -> Report:
        """Run the full pipeline and write the report."""
        trace = TraceLogger(os.getenv("LLM_TRACE_PATH"))
        print("[pipeline] stage 1/6: build snapshot")
        snapshot = build_snapshot(market_date)
        status = get_last_snapshot_status()
        trace.log("pipeline_stage", {"stage": "snapshot_built", "market_date": market_date.isoformat(), "status": status})
        persist_snapshot_metrics(snapshot=snapshot, market_date=market_date, status=status)
        print("[pipeline] stage 2/6: run pre-analysis")
        stances = run_pre_analysis(snapshot, self.agent_ids)
        trace.log("pipeline_stage", {"stage": "stances_built", "count": len(stances)})

        print("[pipeline] stage 3/6: run debate")
        debate_round = run_debate(snapshot, stances)
        trace.log(
            "pipeline_stage",
            {
                "stage": "debate_built",
                "enabled": debate_round is not None,
                "minute_count": len(debate_round.minutes) if debate_round else 0,
            },
        )

        print("[pipeline] stage 4/6: run committee")
        committee_result = run_committee(snapshot, stances, debate_round=debate_round)
        trace.log("pipeline_stage", {"stage": "committee_result_built", "consensus": committee_result.consensus})

        print("[pipeline] stage 5/6: build report")
        report = build_report(
            market_date=market_date.isoformat(),
            snapshot=snapshot,
            stances=stances,
            committee_result=committee_result,
            debate_round=debate_round,
        )

        output_path = output_dir / f"{market_date.isoformat()}.json"
        print("[pipeline] stage 6/6: persist artifacts")
        render_report(report, output_path)
        run_dir = save_run(output_dir, market_date, snapshot, stances, committee_result, report, debate_round=debate_round)
        trace.log("pipeline_stage", {"stage": "artifacts_saved", "run_dir": str(run_dir), "report_json": str(output_path)})
        return report
