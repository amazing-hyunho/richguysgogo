from __future__ import annotations

# Nightly runner for daily committee processing.

import os
import sys
from datetime import date
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from committee.agents.model_profiles import get_agent_model_map, parse_backend
from committee.core.pipeline import DailyPipeline
from committee.core.snapshot_builder import get_last_snapshot_status


def main() -> None:
    """Run nightly pipeline and store run artifacts."""
    runs_dir = ROOT_DIR / "runs"
    market_date = date.today()
    trace_path = runs_dir / market_date.isoformat() / "llm_traces.jsonl"
    os.environ.setdefault("LLM_TRACE_PATH", str(trace_path))

    print("[run_nightly] step 1/4: resolving model profile...")
    backend = parse_backend(os.getenv("AGENT_MODEL_BACKEND", "openai"))
    model_map = get_agent_model_map(backend)
    print("[run_nightly] trace log path: " + os.environ["LLM_TRACE_PATH"])
    print("agent model profile: " + ", ".join([f"{agent.value}={model}" for agent, model in model_map.items()]))

    print("[run_nightly] step 2/4: running daily pipeline...")
    pipeline = DailyPipeline(agent_ids=["macro", "flow", "sector", "risk", "earnings", "breadth", "liquidity"])
    pipeline.run(market_date, runs_dir)

    print("[run_nightly] step 3/4: collecting snapshot source status...")
    status = get_last_snapshot_status()
    if status:
        keys = ["usdkrw", "usdkrw_pct", "us10y", "vix", "vix3m", "vix_term_spread", "hy_oas", "ig_oas", "fed_balance_sheet", "kospi", "kosdaq", "sp500", "nasdaq", "dow", "flows", "headlines"]
        print("snapshot sources status: " + ", ".join([f"{k}={status.get(k,'FAIL')}" for k in keys]))

    print("[run_nightly] step 4/4: done")


if __name__ == "__main__":
    main()
