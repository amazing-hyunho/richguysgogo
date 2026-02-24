from __future__ import annotations

# Storage utilities for run artifacts.

import json
from datetime import date
from pathlib import Path
from typing import List

from committee.core.report_renderer import Report, build_report_markdown
from committee.schemas.committee_result import CommitteeResult
from committee.schemas.snapshot import Snapshot
from committee.schemas.stance import Stance


def save_run(
    base_dir: Path,
    market_date: date,
    snapshot: Snapshot,
    stances: List[Stance],
    committee_result: CommitteeResult,
    report: Report,
) -> Path:
    """Persist run artifacts to a date-based folder."""
    run_dir = base_dir / market_date.isoformat()
    run_dir.mkdir(parents=True, exist_ok=True)

    _write_json(run_dir / "snapshot.json", snapshot.model_dump())
    _write_json(run_dir / "stances.json", [stance.model_dump() for stance in stances])
    _write_json(run_dir / "committee_result.json", committee_result.model_dump())

    report_md = build_report_markdown(report)
    (run_dir / "report.md").write_text(report_md, encoding="utf-8")

    return run_dir


def _write_json(path: Path, payload: dict | list) -> None:
    """Write JSON payload to disk."""
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)
