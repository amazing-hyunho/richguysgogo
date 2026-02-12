
from __future__ import annotations

# Nightly runner for daily committee processing.

import sys
from datetime import date
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from committee.core.pipeline import DailyPipeline
from committee.core.snapshot_builder import get_last_snapshot_status


def main() -> None:
    """Run nightly pipeline and store run artifacts."""
    runs_dir = ROOT_DIR / "runs"
    pipeline = DailyPipeline(agent_ids=["macro", "flow", "sector", "risk"])
    pipeline.run(date.today(), runs_dir)
    status = get_last_snapshot_status()
    if status:
        print(
            f"snapshot sources status: usdkrw={status.get('usdkrw','FAIL')}, "
            f"kospi={status.get('kospi','FAIL')}, "
            f"flows={status.get('flows','FAIL')}, "
            f"headlines={status.get('headlines','FAIL')}"
        )


if __name__ == "__main__":
    main()
