from __future__ import annotations

# Report assembly and rendering utilities.

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import List

from pydantic import BaseModel, Field

from committee.schemas.committee_result import CommitteeResult
from committee.schemas.snapshot import Snapshot
from committee.schemas.stance import Stance


class Report(BaseModel):
    """Structured report for daily output."""
    generated_at: str = Field(..., description="ISO-8601 timestamp (UTC).")
    market_date: str = Field(..., description="Market date (YYYY-MM-DD).")
    snapshot: Snapshot
    stances: List[Stance]
    committee_result: CommitteeResult

    class Config:
        extra = "forbid"


def build_report(
    market_date: str,
    snapshot: Snapshot,
    stances: List[Stance],
    committee_result: CommitteeResult,
) -> Report:
    """Build a report from pipeline artifacts."""
    return Report(
        generated_at=datetime.now(timezone.utc).isoformat(),
        market_date=market_date,
        snapshot=snapshot,
        stances=stances,
        committee_result=committee_result,
    )


def render_report(report: Report, output_path: Path) -> None:
    """Write report JSON to disk."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(report.model_dump(), handle, ensure_ascii=True, indent=2)


def build_report_markdown(report: Report) -> str:
    """Render a minimal markdown report for human review."""
    lines = [
        "# Daily AI Investment Committee",
        "",
        f"Date: {report.market_date}",
        f"Generated: {report.generated_at}",
        "",
        "## Consensus",
        report.committee_result.consensus,
        "",
        "## Key Points",
    ]
    for key_point in report.committee_result.key_points:
        sources = ", ".join(key_point.sources)
        lines.append(f"- {key_point.point} (sources: {sources})")

    tag_counts = {"RISK_ON": 0, "NEUTRAL": 0, "RISK_OFF": 0}
    for stance in report.stances:
        tag_counts[stance.regime_tag.value] = tag_counts.get(stance.regime_tag.value, 0) + 1
    lines.append("")
    lines.append(
        "Regime votes: "
        f"NEUTRAL={tag_counts['NEUTRAL']}, "
        f"RISK_ON={tag_counts['RISK_ON']}, "
        f"RISK_OFF={tag_counts['RISK_OFF']}"
    )

    lines.extend(["", "## Disagreements"])
    for disagreement in report.committee_result.disagreements:
        agents = ", ".join(disagreement.minority_agents)
        lines.append(
            f"- {disagreement.topic}: majority={disagreement.majority}, "
            f"minority={disagreement.minority}, agents=[{agents}]. "
            f"{disagreement.why_it_matters}"
        )

    lines.extend(["", "## Ops Guidance"])
    for guidance in report.committee_result.ops_guidance:
        lines.append(f"- [{guidance.level}] {guidance.text}")

    lines.extend(["", "## Snapshot Notes"])
    lines.append(f"- Market: {report.snapshot.market_summary.note}")
    lines.append(f"- Flow: {report.snapshot.flow_summary.note}")

    return "\n".join(lines)
