from __future__ import annotations

# Local runner for the end-to-end MVP pipeline.

import json
import sys
from datetime import date
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from committee.agents.chair_stub import ChairStub
from committee.agents.flow_stub import FlowStub
from committee.agents.macro_stub import MacroStub
from committee.agents.risk_stub import RiskStub
from committee.agents.sector_stub import SectorStub
from committee.core.report_renderer import build_report, render_report
from committee.core.snapshot_builder import build_snapshot, get_last_snapshot_status
from committee.core.validators import validate_pipeline


def main() -> None:
    """Run the local pipeline and output a report."""
    market_date = date.today()
    snapshot = build_snapshot(market_date)
    status = get_last_snapshot_status()
    if status:
        print(
            f"snapshot sources status: usdkrw={status.get('usdkrw','FAIL')}, "
            f"kospi={status.get('kospi','FAIL')}, "
            f"flows={status.get('flows','FAIL')}, "
            f"headlines={status.get('headlines','FAIL')}"
        )

    agents = [MacroStub(), FlowStub(), SectorStub(), RiskStub()]
    stances = [agent.run(snapshot) for agent in agents]

    chair = ChairStub()
    committee_result = chair.run(stances)

    report = build_report(
        market_date=market_date.isoformat(),
        snapshot=snapshot,
        stances=stances,
        committee_result=committee_result,
    )

    validate_pipeline(snapshot, stances, committee_result, report)

    output_dir = ROOT_DIR / "reports"
    output_path = output_dir / f"{market_date.isoformat()}.json"
    render_report(report, output_path)

    print(json.dumps(report.model_dump(), ensure_ascii=True, indent=2))
    print(f"Report saved to: {output_path}")


if __name__ == "__main__":
    main()
