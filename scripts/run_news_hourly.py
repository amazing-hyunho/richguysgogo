from __future__ import annotations

import argparse
import json
import sqlite3
import subprocess
import sys
from dataclasses import asdict
from datetime import date
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from committee.tools.news_digest import build_topic_digest, recommended_topic_queries
from committee.core.market_collector import persist_snapshot_metrics
from committee.core.snapshot_builder import build_snapshot, get_last_snapshot_status


def _save_digest(payload: dict[str, object]) -> None:
    news_dir = ROOT_DIR / "runs" / "news"
    news_dir.mkdir(parents=True, exist_ok=True)

    latest_path = news_dir / "latest_news_digest.json"
    history_path = news_dir / "history.jsonl"

    latest_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    with history_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False) + "\n")

    print(f"[news_hourly] saved latest: {latest_path}")
    print(f"[news_hourly] appended history: {history_path}")


def _build_dashboard() -> None:
    command = [sys.executable, str(ROOT_DIR / "scripts" / "build_dashboard.py")]
    result = subprocess.run(command, cwd=str(ROOT_DIR), capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "dashboard_build_failed")
    print(result.stdout.strip())


def _collect_indicators(market_date: date) -> None:
    print("[news_hourly] indicator collection: start")
    snapshot = build_snapshot(market_date)
    status = get_last_snapshot_status()
    persist_snapshot_metrics(snapshot=snapshot, market_date=market_date, status=status)
    keys = [
        "usdkrw",
        "usdkrw_pct",
        "us10y",
        "vix",
        "vix3m",
        "vix_term_spread",
        "hy_oas",
        "ig_oas",
        "fed_balance_sheet",
        "kospi",
        "kosdaq",
        "sp500",
        "nasdaq",
        "dow",
        "flows",
        "headlines",
    ]
    print("snapshot sources status: " + ", ".join([f"{k}={status.get(k, 'FAIL')}" for k in keys]))
    print("[news_hourly] indicator collection: done")


def _auto_commit(include_dashboard: bool, include_indicator_db: bool) -> bool:
    targets = [
        "runs/news/latest_news_digest.json",
        "runs/news/history.jsonl",
    ]
    if include_indicator_db:
        _checkpoint_db()
        targets.append("data/investment.db")
    if include_dashboard:
        targets.append("docs/dashboard.html")

    add_command = ["git", "add", *targets]
    add_result = subprocess.run(add_command, cwd=str(ROOT_DIR), capture_output=True, text=True)
    if add_result.returncode != 0:
        raise RuntimeError(add_result.stderr.strip() or "git_add_failed")

    diff_command = ["git", "diff", "--cached", "--quiet"]
    diff_result = subprocess.run(diff_command, cwd=str(ROOT_DIR), capture_output=True, text=True)
    if diff_result.returncode == 0:
        print("[news_hourly] no staged changes, skip commit")
        return False
    if diff_result.returncode not in (0, 1):
        raise RuntimeError(diff_result.stderr.strip() or "git_diff_cached_failed")

    msg = "chore(news): update hourly topic digest and dashboard"
    commit_command = ["git", "commit", "-m", msg]
    commit_result = subprocess.run(commit_command, cwd=str(ROOT_DIR), capture_output=True, text=True)
    if commit_result.returncode != 0:
        raise RuntimeError(commit_result.stderr.strip() or "git_commit_failed")
    print(commit_result.stdout.strip() or "[news_hourly] auto-commit complete")
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
    parser = argparse.ArgumentParser(description="경제 뉴스 1시간 주기 수집/요약 실행")
    parser.add_argument("--target-total", type=int, default=300, help="중복 제거 후 목표 수집 기사 수")
    parser.add_argument("--top-n", type=int, default=5, help="저장할 상위 주제 개수")
    parser.add_argument(
        "--market-date",
        default=date.today().isoformat(),
        help="지표 수집 기준일 (YYYY-MM-DD). 기본값은 오늘 날짜",
    )
    parser.add_argument(
        "--collect-indicators",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="뉴스 실행 시 지표 수집/DB upsert도 함께 수행 (기본: 켬)",
    )
    parser.add_argument(
        "--build-dashboard",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="실행 후 대시보드 재생성 (기본: 켬)",
    )
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

    if args.collect_indicators:
        _collect_indicators(market_date=date.fromisoformat(args.market_date))

    digest, reason = build_topic_digest(target_total=args.target_total, top_n=args.top_n)
    if digest is None:
        raise RuntimeError(f"news_topic_digest_failed: {reason}")

    payload = asdict(digest)
    payload["recommended_topics"] = recommended_topic_queries()
    _save_digest(payload)

    if args.build_dashboard:
        _build_dashboard()

    if args.auto_commit:
        committed = _auto_commit(
            include_dashboard=args.build_dashboard,
            include_indicator_db=args.collect_indicators,
        )
        if committed and args.auto_push:
            _auto_push()

    print(
        "[news_hourly] done: "
        f"collected={payload.get('total_collected')} top_topics={len(payload.get('top_articles', []))}"
    )


if __name__ == "__main__":
    main()
