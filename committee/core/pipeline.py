from __future__ import annotations

# Core daily pipeline orchestration.

from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import List

from committee.core.report_renderer import Report, build_report, render_report
from committee.core.storage import save_run
from committee.core.snapshot_builder import build_snapshot
from committee.schemas.committee_result import (
    CommitteeResult,
    Disagreement,
    OpsGuidance,
    OpsGuidanceLevel,
)
from committee.schemas.stance import AgentName, ConfidenceLevel, RegimeTag, Stance


def run_pre_analysis(snapshot: object, agent_ids: List[str]) -> List[Stance]:
    """Generate stub stances for configured agent IDs."""
    stances: List[Stance] = []
    for agent_id in agent_ids:
        stances.append(
            Stance(
                agent_name=AgentName(agent_id),
                core_claims=[
                    f"{agent_id} sees balanced risk.",
                    "Liquidity is stable.",
                ],
                regime_tag=RegimeTag.NEUTRAL,
                evidence_ids=["snapshot.market_summary.note", "snapshot.flow_summary.note"],
                confidence=ConfidenceLevel.MED,
            )
        )
    return stances


def run_committee(snapshot: object, stances: List[Stance]) -> CommitteeResult:
    """Generate a stub committee result from stances."""
    key_points = _build_key_points(stances, None)
    return CommitteeResult(
        consensus="Committee agrees on a neutral stance with selective monitoring.",
        key_points=key_points,
        disagreements=[
            Disagreement(
                topic="Regime tags",
                majority=RegimeTag.NEUTRAL.value,
                minority="None",
                minority_agents=["none"],
                why_it_matters="No dissenting regime tags are present.",
            )
        ],
        ops_guidance=[
            OpsGuidance(level=OpsGuidanceLevel.OK, text="Keep watchlist tight and avoid overexposure."),
            OpsGuidance(level=OpsGuidanceLevel.CAUTION, text="Keep position sizes moderate."),
            OpsGuidance(level=OpsGuidanceLevel.AVOID, text="Avoid aggressive leverage."),
        ],
    )


def _build_key_points(stances: List[Stance], majority_tag: RegimeTag | None) -> list[dict]:
    if not stances:
        return [{"point": "No stances provided.", "sources": ["none"]}]

    tag_to_agents: dict[RegimeTag, list[str]] = {
        RegimeTag.RISK_ON: [],
        RegimeTag.NEUTRAL: [],
        RegimeTag.RISK_OFF: [],
    }
    for stance in stances:
        tag_to_agents[stance.regime_tag].append(stance.agent_name.value)

    if majority_tag is None:
        majority_tag = max(tag_to_agents, key=lambda tag: len(tag_to_agents[tag]))
    return [
        {
            "point": f"Majority regime tag: {majority_tag.value}.",
            "sources": tag_to_agents[majority_tag][:5] or ["unknown"],
        }
    ]


@dataclass(frozen=True)
class DailyPipeline:
    """Pipeline runner for daily snapshot-to-report flow."""
    agent_ids: List[str]

    def run(self, market_date: date, output_dir: Path) -> Report:
        """Run the full pipeline and write the report."""
        snapshot = build_snapshot(market_date)
        stances = run_pre_analysis(snapshot, self.agent_ids)
        committee_result = run_committee(snapshot, stances)

        report = build_report(
            market_date=market_date.isoformat(),
            snapshot=snapshot,
            stances=stances,
            committee_result=committee_result,
        )

        output_path = output_dir / f"{market_date.isoformat()}.json"
        render_report(report, output_path)
        save_run(output_dir, market_date, snapshot, stances, committee_result, report)
        return report
