from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import asdict
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from committee.tools.news_digest import build_topic_digest, recommended_topic_queries


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


def _auto_commit(include_dashboard: bool) -> None:
    targets = [
        "runs/news/latest_news_digest.json",
        "runs/news/history.jsonl",
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
        print("[news_hourly] no staged changes, skip commit")
        return
    if diff_result.returncode not in (0, 1):
        raise RuntimeError(diff_result.stderr.strip() or "git_diff_cached_failed")

    msg = "chore(news): update hourly topic digest and dashboard"
    commit_command = ["git", "commit", "-m", msg]
    commit_result = subprocess.run(commit_command, cwd=str(ROOT_DIR), capture_output=True, text=True)
    if commit_result.returncode != 0:
        raise RuntimeError(commit_result.stderr.strip() or "git_commit_failed")
    print(commit_result.stdout.strip() or "[news_hourly] auto-commit complete")


def main() -> None:
    parser = argparse.ArgumentParser(description="경제 뉴스 1시간 주기 수집/요약 실행")
    parser.add_argument("--target-total", type=int, default=300, help="중복 제거 후 목표 수집 기사 수")
    parser.add_argument("--top-n", type=int, default=5, help="저장할 상위 주제 개수")
    parser.add_argument("--build-dashboard", action="store_true", help="실행 후 대시보드 재생성")
    parser.add_argument("--auto-commit", action="store_true", help="산출물 변경 시 자동 git commit")
    args = parser.parse_args()

    digest, reason = build_topic_digest(target_total=args.target_total, top_n=args.top_n)
    if digest is None:
        raise RuntimeError(f"news_topic_digest_failed: {reason}")

    payload = asdict(digest)
    payload["recommended_topics"] = recommended_topic_queries()
    _save_digest(payload)

    if args.build_dashboard:
        _build_dashboard()

    if args.auto_commit:
        _auto_commit(include_dashboard=args.build_dashboard)

    print(
        "[news_hourly] done: "
        f"collected={payload.get('total_collected')} top_topics={len(payload.get('top_articles', []))}"
    )


if __name__ == "__main__":
    main()
