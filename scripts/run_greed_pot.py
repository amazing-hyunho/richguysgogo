from __future__ import annotations

"""Run 탐욕의 항아리 against the latest saved snapshot."""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from committee.agents.greed_pot import GreedPotAgent, write_greed_pot_result
from committee.core.env_loader import load_project_env
from committee.schemas.snapshot import Snapshot
from committee.schemas.stance import Stance


def _latest_run_dir() -> Path:
    candidates = sorted(
        path
        for path in (ROOT_DIR / "runs").iterdir()
        if path.is_dir() and (path / "snapshot.json").exists() and path.name[:4].isdigit()
    )
    if not candidates:
        raise RuntimeError("latest_run_snapshot_not_found")
    return candidates[-1]


def _build_dashboard() -> None:
    result = subprocess.run(
        [sys.executable, str(ROOT_DIR / "scripts" / "build_dashboard.py")],
        cwd=str(ROOT_DIR),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "dashboard_build_failed")
    if result.stdout.strip():
        print(result.stdout.strip())


def main() -> None:
    parser = argparse.ArgumentParser(description="탐욕의 항아리 LLM 가설 생성")
    parser.add_argument("--run-dir", type=Path, default=None, help="runs/YYYY-MM-DD 디렉터리")
    parser.add_argument("--build-dashboard", action=argparse.BooleanOptionalAction, default=True)
    args = parser.parse_args()

    load_project_env(ROOT_DIR)
    run_dir = args.run_dir or _latest_run_dir()
    os.environ.setdefault("LLM_TRACE_PATH", str(run_dir / "llm_traces.jsonl"))

    snapshot = Snapshot.model_validate(json.loads((run_dir / "snapshot.json").read_text(encoding="utf-8")))
    stances_path = run_dir / "stances.json"
    stances = [
        Stance.model_validate(item)
        for item in json.loads(stances_path.read_text(encoding="utf-8"))
    ] if stances_path.exists() else []

    print(f"[greed_pot] run_dir={run_dir}")
    result = GreedPotAgent().run(snapshot=snapshot, stances=stances)
    out_path = run_dir / "greed_pot.json"
    write_greed_pot_result(out_path, result)
    print(f"[greed_pot] saved={out_path} fallback_used={result.fallback_used}")

    if args.build_dashboard:
        print("[greed_pot] dashboard build: start")
        _build_dashboard()
        print("[greed_pot] dashboard build: done")


if __name__ == "__main__":
    main()
