from __future__ import annotations

# Local runner for the end-to-end MVP pipeline.

import json
import os
import sys
from datetime import date
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from committee.agents.breadth_stub import BreadthStub
from committee.agents.chair_stub import ChairStub
from committee.agents.earnings_stub import EarningsStub
from committee.agents.flow_stub import FlowStub
from committee.agents.liquidity_stub import LiquidityStub
from committee.agents.llm_pre_analysis import LLMPreAnalysisAgent, LLMRunOptions
from committee.agents.macro_stub import MacroStub
from committee.agents.model_profiles import ModelBackend, get_agent_model_map, parse_backend
from committee.agents.risk_stub import RiskStub
from committee.agents.sector_stub import SectorStub
from committee.core.report_renderer import build_report, render_report
from committee.core.snapshot_builder import build_snapshot, get_last_snapshot_status
from committee.core.validators import validate_pipeline
from committee.schemas.stance import AgentName


def main() -> None:
    """Run the local pipeline and output a report."""
    market_date = date.today()
    trace_path = ROOT_DIR / "runs" / market_date.isoformat() / "llm_traces.jsonl"
    os.environ.setdefault("LLM_TRACE_PATH", str(trace_path))

    print("[run_local] step 1/6: building snapshot...")
    snapshot = build_snapshot(market_date)
    status = get_last_snapshot_status()
    if status:
        keys = ["usdkrw", "usdkrw_pct", "us10y", "vix", "kospi", "kosdaq", "sp500", "nasdaq", "dow", "flows", "headlines"]
        print("snapshot sources status: " + ", ".join([f"{k}={status.get(k,'FAIL')}" for k in keys]))

    backend = parse_backend(os.getenv("AGENT_MODEL_BACKEND", "openai"))
    model_map = get_agent_model_map(backend)
    print("[run_local] trace log path: " + os.environ["LLM_TRACE_PATH"])
    print(
        "agent model profile: "
        + ", ".join([f"{agent.value}={model}" for agent, model in model_map.items()])
    )

    use_llm_agents = os.getenv("USE_LLM_AGENTS", "0").strip() == "1"
    agent_specs = [
        (AgentName.MACRO, MacroStub()),
        (AgentName.FLOW, FlowStub()),
        (AgentName.SECTOR, SectorStub()),
        (AgentName.RISK, RiskStub()),
        (AgentName.EARNINGS, EarningsStub()),
        (AgentName.BREADTH, BreadthStub()),
        (AgentName.LIQUIDITY, LiquidityStub()),
    ]
    if use_llm_agents and backend == ModelBackend.OPENAI:
        options = LLMRunOptions(backend=backend, temperature=float(os.getenv("LLM_TEMPERATURE", "0.1")))
        agents = [
            LLMPreAnalysisAgent(agent_name=agent_name, fallback_agent=fallback, options=options)
            for agent_name, fallback in agent_specs
        ]
    else:
        agents = [fallback for _, fallback in agent_specs]

    print("[run_local] step 2/6: running pre-analysis agents...")
    stances = [agent.run(snapshot) for agent in agents]

    print("[run_local] step 3/6: running chair consensus...")
    chair = ChairStub()
    committee_result = chair.run(stances)

    print("[run_local] step 4/6: building report object...")
    report = build_report(
        market_date=market_date.isoformat(),
        snapshot=snapshot,
        stances=stances,
        committee_result=committee_result,
    )

    print("[run_local] step 5/6: validating pipeline artifacts...")
    validate_pipeline(snapshot, stances, committee_result, report)

    print("[run_local] step 6/6: rendering report file...")
    output_dir = ROOT_DIR / "reports"
    output_path = output_dir / f"{market_date.isoformat()}.json"
    render_report(report, output_path)

    print(json.dumps(report.model_dump(), ensure_ascii=False, indent=2))
    print(f"Report saved to: {output_path}")


if __name__ == "__main__":
    main()
