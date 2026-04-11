from __future__ import annotations

# Nightly runner for daily committee processing.

import os
import sqlite3
import subprocess
import sys
from datetime import date
from pathlib import Path
import argparse

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from committee.agents.model_profiles import get_agent_model_map, parse_backend
from committee.core.env_loader import load_project_env
from committee.core.pipeline import DailyPipeline
from committee.core.snapshot_builder import get_last_snapshot_status


def _build_dashboard() -> None:
    command = [sys.executable, str(ROOT_DIR / "scripts" / "build_dashboard.py")]
    result = subprocess.run(command, cwd=str(ROOT_DIR), capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "dashboard_build_failed")
    if result.stdout.strip():
        print(result.stdout.strip())


def _auto_commit(market_date: date, include_dashboard: bool) -> bool:
    date_s = market_date.isoformat()
    _checkpoint_db()
    targets = [
        f"runs/{date_s}.json",
        f"runs/{date_s}",
        "data/investment.db",
    ]
    if include_dashboard:
        targets.append("docs/dashboard.html")

    add_command = ["git", "add", *targets]
    add_result = subprocess.run(add_command, cwd=str(ROOT_DIR), capture_output=True, text=True)
    if add_result.returncode != 0:
        raise RuntimeError(add_result.stderr.strip() or "git_add_failed")

    diff_command = ["git", "diff", "--cached", "--quiet"]
    diff_result = subprocess.run(diff_command, cwd=str(ROOT_DIR), capture_output=True, text=True)
    if diff_result.returncode == 0:
        print("[run_nightly] no staged changes, skip commit")
        return False
    if diff_result.returncode not in (0, 1):
        raise RuntimeError(diff_result.stderr.strip() or "git_diff_cached_failed")

    msg = f"chore(nightly): update pipeline artifacts for {date_s}"
    commit_command = ["git", "commit", "-m", msg]
    commit_result = subprocess.run(commit_command, cwd=str(ROOT_DIR), capture_output=True, text=True)
    if commit_result.returncode != 0:
        raise RuntimeError(commit_result.stderr.strip() or "git_commit_failed")
    if commit_result.stdout.strip():
        print(commit_result.stdout.strip())
    return True


def _checkpoint_db() -> None:
    """Flush SQLite WAL into main DB file before git add."""
    db_path = ROOT_DIR / "data" / "investment.db"
    if not db_path.exists():
        return
    conn = sqlite3.connect(str(db_path))
    try:
        conn.execute("PRAGMA wal_checkpoint(FULL);")
    finally:
        conn.close()


def _auto_push() -> None:
    push_command = ["git", "push", "origin", "HEAD"]
    push_result = subprocess.run(push_command, cwd=str(ROOT_DIR), capture_output=True, text=True)
    if push_result.returncode != 0:
        raise RuntimeError(push_result.stderr.strip() or "git_push_failed")
    if push_result.stdout.strip():
        print(push_result.stdout.strip())
    if push_result.stderr.strip():
        print(push_result.stderr.strip())


def main() -> None:
    """Run nightly pipeline and store run artifacts."""
    load_project_env(ROOT_DIR)
    parser = argparse.ArgumentParser(description="야간 파이프라인 실행")
    parser.add_argument("--build-dashboard", action="store_true", help="실행 후 대시보드 재생성")
    parser.add_argument(
        "--auto-commit",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="산출물 변경 시 자동 git commit (기본: 켬)",
    )
    parser.add_argument(
        "--auto-push",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="자동 커밋 후 git push origin HEAD (기본: 켬)",
    )
    args = parser.parse_args()

    runs_dir = ROOT_DIR / "runs"
    market_date = date.today()
    trace_path = runs_dir / market_date.isoformat() / "llm_traces.jsonl"
    os.environ.setdefault("LLM_TRACE_PATH", str(trace_path))
    if os.getenv("ECOS_API_KEY", "").strip():
        print("[run_nightly] ecos key check: OK")
    else:
        print("[run_nightly] ecos key check: MISSING (set ECOS_API_KEY for domestic base rate)")

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

    if args.build_dashboard:
        print("[run_nightly] dashboard build: start")
        _build_dashboard()
        print("[run_nightly] dashboard build: done")

    if args.auto_commit:
        print("[run_nightly] auto-commit: start")
        committed = _auto_commit(market_date=market_date, include_dashboard=args.build_dashboard)
        print("[run_nightly] auto-commit: done")
        if committed and args.auto_push:
            print("[run_nightly] auto-push: start")
            _auto_push()
            print("[run_nightly] auto-push: done")

    print("[run_nightly] step 4/4: done")


if __name__ == "__main__":
    main()
