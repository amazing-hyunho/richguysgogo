from __future__ import annotations

"""Backfill daily pipeline artifacts and DB rows for a date range.

Use cases
- Fill missing dates only (default).
- Re-run all dates in a range (e.g., full 1-year refresh).
"""

import argparse
import os
import sqlite3
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from datetime import date, timedelta
from pathlib import Path
import json

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from committee.core.env_loader import load_project_env
from committee.core.market_collector import persist_snapshot_metrics
from committee.core.pipeline import DailyPipeline
from committee.core.snapshot_builder import build_snapshot, get_last_snapshot_status
from committee.core.trace_logger import TraceLogger


DEFAULT_AGENT_IDS = ["macro", "flow", "sector", "risk", "earnings", "breadth", "liquidity"]


@dataclass(frozen=True)
class BackfillTarget:
    market_date: date
    reason: str


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="날짜 범위 파이프라인 백필 (runs + DB 동시 적재)")
    parser.add_argument(
        "--mode",
        choices=["missing", "all"],
        default="missing",
        help="missing: 누락일만 실행, all: 범위 전체 재실행",
    )
    parser.add_argument("--start-date", default="", help="시작일 (YYYY-MM-DD)")
    parser.add_argument("--end-date", default="", help="종료일 (YYYY-MM-DD, 기본: 오늘)")
    parser.add_argument(
        "--lookback-days",
        type=int,
        default=365,
        help="--start-date 미지정 시, 종료일 기준 역산 일수 (기본 365)",
    )
    parser.add_argument(
        "--agent-ids",
        default=",".join(DEFAULT_AGENT_IDS),
        help="쉼표 구분 agent ids (기본: macro,flow,sector,risk,earnings,breadth,liquidity)",
    )
    parser.add_argument(
        "--skip-weekends",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="주말(토/일) 건너뛰기 (기본: false)",
    )
    parser.add_argument(
        "--check-db",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="missing 모드에서 DB 누락 여부도 함께 검사 (기본: true)",
    )
    parser.add_argument("--dry-run", action="store_true", help="실제 실행 없이 대상 날짜만 출력")
    parser.add_argument(
        "--rebuild-dashboard",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="처리 후 dashboard 재생성 (기본: true)",
    )
    parser.add_argument(
        "--continue-on-error",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="일부 날짜 실패 시 계속 진행 (기본: true)",
    )
    parser.add_argument(
        "--exclude-ai",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="AI 판단(stance/committee) 없이 스냅샷+DB 적재만 수행 (기본: false)",
    )
    return parser.parse_args()


def _resolve_date_range(args: argparse.Namespace) -> tuple[date, date]:
    end_d = date.today() if not args.end_date else date.fromisoformat(str(args.end_date))
    if args.start_date:
        start_d = date.fromisoformat(str(args.start_date))
    else:
        lookback = max(int(args.lookback_days), 1)
        start_d = end_d - timedelta(days=lookback - 1)
    if end_d < start_d:
        raise ValueError("end-date must be >= start-date")
    return start_d, end_d


def _iter_dates(start_d: date, end_d: date) -> list[date]:
    days: list[date] = []
    cur = start_d
    while cur <= end_d:
        days.append(cur)
        cur += timedelta(days=1)
    return days


def _has_run_artifacts(day: date, *, exclude_ai: bool) -> bool:
    date_s = day.isoformat()
    run_dir = ROOT_DIR / "runs" / date_s
    summary_json = ROOT_DIR / "runs" / f"{date_s}.json"
    required_dir_files = [run_dir / "snapshot.json"]
    if not exclude_ai:
        required_dir_files.extend(
            [
                run_dir / "stances.json",
                run_dir / "committee_result.json",
                run_dir / "report.md",
            ]
        )
    return summary_json.exists() and all(path.exists() for path in required_dir_files)


def _db_has_core_rows(day: date, conn: sqlite3.Connection) -> bool:
    date_s = day.isoformat()
    checks = {
        "market_daily": "SELECT 1 FROM market_daily WHERE date = ? LIMIT 1",
        "market_flow_daily": "SELECT 1 FROM market_flow_daily WHERE date = ? LIMIT 1",
        "daily_macro": "SELECT 1 FROM daily_macro WHERE date = ? LIMIT 1",
    }
    for _, query in checks.items():
        row = conn.execute(query, (date_s,)).fetchone()
        if row is None:
            return False
    return True


def _plan_targets(
    *,
    start_d: date,
    end_d: date,
    mode: str,
    skip_weekends: bool,
    check_db: bool,
    exclude_ai: bool,
) -> list[BackfillTarget]:
    days = _iter_dates(start_d, end_d)
    targets: list[BackfillTarget] = []

    conn: sqlite3.Connection | None = None
    if check_db:
        db_path = ROOT_DIR / "data" / "investment.db"
        if db_path.exists():
            conn = sqlite3.connect(str(db_path))

    try:
        for day in days:
            if skip_weekends and day.weekday() >= 5:
                continue

            if mode == "all":
                targets.append(BackfillTarget(market_date=day, reason="mode=all"))
                continue

            has_runs = _has_run_artifacts(day, exclude_ai=exclude_ai)
            has_db = True
            if conn is not None:
                has_db = _db_has_core_rows(day, conn)

            if not has_runs and not has_db:
                reason = "runs_missing+db_missing"
            elif not has_runs:
                reason = "runs_missing"
            elif not has_db:
                reason = "db_missing"
            else:
                reason = ""

            if reason:
                targets.append(BackfillTarget(market_date=day, reason=reason))
    finally:
        if conn is not None:
            conn.close()

    return targets


def _parse_agent_ids(raw: str) -> list[str]:
    items = [token.strip() for token in str(raw).split(",")]
    return [item for item in items if item]


def _build_dashboard() -> None:
    cmd = [sys.executable, str(ROOT_DIR / "scripts" / "build_dashboard.py")]
    result = subprocess.run(cmd, cwd=str(ROOT_DIR), capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "dashboard_build_failed")
    if result.stdout.strip():
        print(result.stdout.strip())


def _persist_snapshot_only_artifacts(
    *,
    market_date: date,
    snapshot_obj: object,
    status: dict[str, str],
) -> None:
    date_s = market_date.isoformat()
    run_dir = ROOT_DIR / "runs" / date_s
    run_dir.mkdir(parents=True, exist_ok=True)

    snapshot_payload = snapshot_obj.model_dump()
    (run_dir / "snapshot.json").write_text(
        json.dumps(snapshot_payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    summary_payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "market_date": date_s,
        "snapshot": snapshot_payload,
    }
    (ROOT_DIR / "runs" / f"{date_s}.json").write_text(
        json.dumps(summary_payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    trace_path = run_dir / "llm_traces.jsonl"
    tracer = TraceLogger(trace_path)
    tracer.log(
        "pipeline_stage",
        {
            "stage": "snapshot_built",
            "market_date": date_s,
            "status": status,
            "exclude_ai": True,
        },
    )


def main() -> None:
    args = _parse_args()
    load_project_env(ROOT_DIR)

    start_d, end_d = _resolve_date_range(args)
    agent_ids = _parse_agent_ids(args.agent_ids)
    if not agent_ids:
        raise ValueError("agent-ids is empty")

    targets = _plan_targets(
        start_d=start_d,
        end_d=end_d,
        mode=str(args.mode),
        skip_weekends=bool(args.skip_weekends),
        check_db=bool(args.check_db),
        exclude_ai=bool(args.exclude_ai),
    )

    print(
        f"[backfill] range={start_d.isoformat()}..{end_d.isoformat()} "
        f"mode={args.mode} targets={len(targets)} dry_run={args.dry_run}"
    )
    for item in targets:
        print(f"[backfill] target {item.market_date.isoformat()} ({item.reason})")

    if args.dry_run or not targets:
        return

    pipeline = DailyPipeline(agent_ids=agent_ids)
    success = 0
    failed = 0

    for idx, item in enumerate(targets, start=1):
        d = item.market_date
        trace_path = ROOT_DIR / "runs" / d.isoformat() / "llm_traces.jsonl"
        os.environ["LLM_TRACE_PATH"] = str(trace_path)
        print(f"[backfill] run {idx}/{len(targets)} -> {d.isoformat()}")
        try:
            if args.exclude_ai:
                snapshot = build_snapshot(d)
                status = get_last_snapshot_status() or {}
                persist_snapshot_metrics(snapshot=snapshot, market_date=d, status=status)
                _persist_snapshot_only_artifacts(
                    market_date=d,
                    snapshot_obj=snapshot,
                    status=status,
                )
            else:
                pipeline.run(d, ROOT_DIR / "runs")
            success += 1
        except Exception as exc:  # noqa: BLE001
            failed += 1
            print(f"[backfill] failed {d.isoformat()}: {exc}")
            if not args.continue_on_error:
                raise

    if args.rebuild_dashboard and success > 0:
        print("[backfill] dashboard rebuild: start")
        _build_dashboard()
        print("[backfill] dashboard rebuild: done")

    print(f"[backfill] done success={success} failed={failed} targets={len(targets)}")


if __name__ == "__main__":
    main()
