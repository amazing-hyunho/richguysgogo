from __future__ import annotations

"""주간·정기 무거운 데이터 동기화 스크립트.

매일 돌리는 sync_all.py 와 달리, 주 1~2회 또는 월 1회처럼
시간이 오래 걸리는 작업들만 모아서 실행합니다.

포함 작업
----------
1. 종목 마스터 갱신     - KR (DART/Naver), US (S&P500 + NASDAQ100)
2. 수급 2년치 백필      - Naver Finance (skip-existing 포함)
3. 전체 종목 컨센서스   - ticker_master에 있는 KR 전체 or --top N
4. US 재무제표          - watchlist (yfinance)
5. KR 재무제표          - DART_API_KEY 있으면 자동 수집 (--skip-kr-financials 로 생략)
6. FRED 매크로 전체 재백필 (옵션, --deep-macro)
7. 대시보드 빌드

소요 시간 예상
--------------
- 기본 실행 (KR 컨센서스 전체 + KR 재무제표) : 3~5시간
- --top 300 모드                               : 30~60분
- --skip-kr-financials 포함                   : 2~4시간 (재무제표 제외)

사용 예시
----------
    # 주 1회 전체 갱신 (권장)
    python scripts/sync_weekly.py

    # 완료 후 git commit + push
    python scripts/sync_weekly.py --auto-push

    # 빠른 모드: 상위 300종목만, US 재무제표 생략
    python scripts/sync_weekly.py --top 300 --skip-us-financials

    # KR 재무제표 생략 (기본은 수집함, DART_API_KEY 없으면 자동 스킵)
    python scripts/sync_weekly.py --skip-kr-financials

    # FRED 매크로 전체 재백필 포함 (최초 1회)
    python scripts/sync_weekly.py --deep-macro

    # 종목 마스터만 갱신
    python scripts/sync_weekly.py --master-only

    # 컨센서스/재무 생략하고 마스터 + 매크로만
    python scripts/sync_weekly.py --skip-stocks
"""

import argparse
import os
import subprocess
import sys
from datetime import date, timedelta
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]


def _git_commit_push(tag: str) -> None:
    """변경된 파일을 git add → commit → push 한다."""
    today = date.today().isoformat()
    msg = f"auto: {tag} {today}"
    print(f"\n[git] ▶  add . → commit '{msg}' → push")
    for cmd in (
        ["git", "add", "."],
        ["git", "commit", "-m", msg],
        ["git", "push"],
    ):
        r = subprocess.run(cmd, cwd=str(ROOT_DIR), capture_output=True, text=True)
        if r.returncode != 0:
            if "nothing to commit" in (r.stdout + r.stderr):
                print("[git] ℹ  nothing to commit, skipping push")
                return
            print(f"[git] ✗  {' '.join(cmd)} failed:\n{r.stderr.strip()}")
            return
        if r.stdout.strip():
            print(r.stdout.strip())
    print("[git] ✓  push 완료")


def _run(label: str, cmd: list[str], skip: bool = False) -> bool:
    if skip:
        print(f"[sync_weekly] ⏭  SKIP  {label}")
        return True
    print(f"\n[sync_weekly] ▶  {label}")
    result = subprocess.run(cmd, cwd=str(ROOT_DIR))
    ok = result.returncode == 0
    icon = "✓" if ok else "✗"
    print(f"[sync_weekly] {icon}  {label} (exit={result.returncode})")
    return ok


def _has_dart_key() -> bool:
    return bool(os.getenv("DART_API_KEY", "").strip())


def _parse_args(run_date: date | None = None) -> argparse.Namespace:
    reference_date = run_date or date.today()
    p = argparse.ArgumentParser(description="주간·정기 무거운 데이터 동기화")
    p.add_argument(
        "--top", type=int, default=0,
        help="KR 컨센서스를 시가총액 상위 N종목만 수집 (0=전체, 기본: 전체)",
    )
    p.add_argument(
        "--resume", action="store_true",
        help="오늘 이미 수집된 종목은 건너뜀 (중단 후 재시작용)",
    )
    p.add_argument(
        "--skip-kr-financials", action="store_true",
        help="KR 재무제표 수집 건너뜀 (기본: DART_API_KEY 있으면 자동 수집)",
    )
    p.add_argument(
        "--year", type=int, default=reference_date.year - 1,
        help="KR 재무제표 연도 (기본: 전년도)",
    )
    p.add_argument(
        "--quarterly", action="store_true",
        help="KR 분기 보고서도 포함",
    )
    p.add_argument(
        "--skip-us-financials", action="store_true",
        help="US 재무제표 수집 건너뜀",
    )
    p.add_argument(
        "--skip-stocks", action="store_true",
        help="컨센서스·재무제표 전부 건너뜀 (마스터 + 매크로만)",
    )
    p.add_argument(
        "--master-only", action="store_true",
        help="종목 마스터 갱신만 하고 종료",
    )
    p.add_argument(
        "--deep-macro", action="store_true",
        help="FRED 매크로 전체 날짜 재백필 (최초 1회용, 매우 느림)",
    )
    p.add_argument(
        "--skip-dashboard", action="store_true",
        help="대시보드 빌드 건너뜀",
    )
    p.add_argument(
        "--skip-industry-cycle", action="store_true",
        help="산업 사이클 주간 파이프라인 전체 건너뜀",
    )
    p.add_argument(
        "--skip-industry-llm", action="store_true",
        help="산업 뉴스는 수집하되 AI 종합의견 생성은 건너뜀",
    )
    p.add_argument(
        "--us-sp500", action="store_true",
        help="US 종목 마스터: S&P 500 포함 (기본 포함)",
    )
    p.add_argument(
        "--us-ndx", action="store_true",
        help="US 종목 마스터: NASDAQ 100 포함 (기본 포함)",
    )
    p.add_argument(
        "--auto-push", action="store_true",
        help="완료 후 git commit + push 자동 실행",
    )
    return p.parse_args()


def main() -> None:
    # Freeze the logical run date once. Long full-universe batches can cross
    # midnight; every downstream cutoff must still belong to one weekly run.
    run_date = date.today()
    args = _parse_args(run_date)
    py = sys.executable
    results: list[tuple[str, bool]] = []

    def step(label: str, cmd: list[str], skip: bool = False) -> None:
        ok = _run(label, cmd, skip=skip)
        results.append((label, ok))

    print("=" * 62)
    print("  sync_weekly: 주간·정기 데이터 동기화 시작")
    print(f"  날짜: {run_date.isoformat()}")
    print("=" * 62)

    # ── 1. 종목 마스터 갱신 ──────────────────────────────────────
    # KR: DART API (DART_API_KEY 있을 때) 또는 Naver Finance 스크래핑
    step(
        "KR 종목 마스터 (ticker_master, KOSPI+KOSDAQ)",
        [py, "scripts/sync_stock_master.py", "--kr"],
    )

    # US: S&P 500 + NASDAQ 100 (Wikipedia 스크래핑, 빠름)
    step(
        "US 종목 마스터 (ticker_master, S&P500 + NASDAQ100)",
        [py, "scripts/sync_stock_master.py", "--us-sp500", "--us-ndx"],
    )

    if args.master_only:
        print("\n[sync_weekly] --master-only 모드: 마스터 갱신 후 종료")
        _print_summary(results, auto_push=args.auto_push)
        return

    # ── 2. 수급 전체 백필 (외국인/기관/개인, 2년치) ──────────────
    # sync_all.py 에서는 최근 7일만 처리하므로, 주간 실행에서 누락 없이 채움.
    _flow_start = (run_date - timedelta(days=365 * 2)).isoformat()
    step(
        "외국인/기관/개인 수급 전체 백필 (market_flow_daily, 2년치)",
        [py, "scripts/backfill_market_flow_history.py",
         "--start-date", _flow_start,
         "--end-date", run_date.isoformat(),
         "--source", "NAVER",
         "--skip-existing"],
        skip=args.skip_stocks,
    )

    # ── 3. FRED 매크로 지표 (옵션: 전체 재백필) ──────────────────
    if args.deep_macro:
        step(
            "매크로 심화 지표 전체 재백필 (FRED)",
            [py, "scripts/backfill_macro_indicators.py", "--days", "0"],
        )

    if args.skip_stocks:
        print("\n[sync_weekly] --skip-stocks 모드: 컨센서스·재무제표 건너뜀")
    else:
        # ── 4. 전체 종목 컨센서스 (재무제표는 별도 스텝 5·6에서 처리) ──
        # sync_all_stocks.py 는 --with-kr-financials 없으면 KR 재무제표 수집 안 함
        consensus_cmd = [py, "scripts/sync_all_stocks.py", "--skip-us-financials"]
        if args.top:
            consensus_cmd += ["--top", str(args.top)]
        if args.resume:
            consensus_cmd.append("--resume")
        if args.skip_us_financials:
            consensus_cmd.append("--skip-us-financials")

        step(
            f"전체 종목 컨센서스{f' (상위 {args.top}종목)' if args.top else ' (전체)'}",
            consensus_cmd,
        )

        # ── 5. US 재무제표 (yfinance, watchlist) ──────────────────
        step(
            "US watchlist 재무제표 (financial_metric)",
            [py, "scripts/sync_financials.py", "--us"],
            skip=args.skip_us_financials,
        )

        # ── 6. KR 재무제표 (DART API) ─────────────────────────────
        # 기본 수집. DART_API_KEY 없으면 자동 스킵, --skip-kr-financials 로 명시적 생략 가능.
        if args.skip_kr_financials:
            print("[sync_weekly] ⏭  SKIP  KR 재무제표 (--skip-kr-financials)")
        elif not _has_dart_key():
            print("[sync_weekly] ⚠  SKIP  KR 재무제표 (DART_API_KEY 없음)")
            print("              환경변수 DART_API_KEY 를 설정하면 자동으로 수집됩니다.")
        else:
            kr_cmd = [
                py, "scripts/sync_financials.py",
                "--year", str(args.year),
            ]
            if args.quarterly:
                kr_cmd.append("--quarterly")
            step(f"KR 재무제표 {args.year}년 (DART)", kr_cmd)

    # ── 7. 산업 사이클 전체 주간 파이프라인 ───────────────────────
    # 기존 Windows 예약 작업이 이 sync_weekly.py를 실행하므로 별도
    # cron/task를 만들지 않는다. 모든 단계는 개별 스크립트의 격리·
    # upsert 계약을 사용하며, AI 의견은 정량 신호를 변경하지 않는다.
    industry_as_of = run_date.isoformat()
    industry_price_start = (run_date - timedelta(days=21)).isoformat()
    if args.skip_industry_cycle:
        print("\n[sync_weekly] ⏭  SKIP  산업 사이클 전체 파이프라인")
    else:
        step(
            "산업 분류·자산·지표 설정 동기화",
            [py, "scripts/sync_industry_master.py", "--execute"],
        )
        step(
            "산업 대표자산 최근 가격 갱신 (21일)",
            [
                py, "scripts/backfill_industry_prices.py",
                "--start-date", industry_price_start,
                "--end-date", industry_as_of,
                "--execute",
            ],
        )
        step(
            "산업 업황 지표 갱신",
            [py, "scripts/backfill_industry_indicators.py", "--execute"],
        )
        step(
            "산업 가격·상대강도·과열 계산",
            [py, "scripts/run_industry_price_factors.py", "--as-of", industry_as_of, "--execute"],
        )
        step(
            "산업 펀더멘털 점수 계산",
            [py, "scripts/run_industry_fundamentals_factors.py", "--as-of", industry_as_of, "--execute"],
        )
        step(
            "산업 ETF·종목 후보 순위 계산",
            [py, "scripts/run_industry_candidates.py", "--as-of", industry_as_of, "--execute"],
        )
        step(
            "산업 사이클 최종 신호 계산",
            [py, "scripts/run_industry_cycle_weekly.py", "--as-of", industry_as_of, "--execute"],
        )
        step(
            "산업 가상 포트폴리오 갱신",
            [py, "scripts/run_industry_virtual_portfolio.py", "--as-of", industry_as_of, "--execute"],
        )
        insight_cmd = [
            py, "scripts/run_industry_weekly_insights.py",
            "--as-of", industry_as_of,
            "--execute",
        ]
        if args.skip_industry_llm:
            insight_cmd.append("--skip-llm")
        step("산업 뉴스·AI 종합의견 생성", insight_cmd)

    # ── 8. 대시보드 빌드 ──────────────────────────────────────────
    step(
        "대시보드 빌드 (docs/dashboard.html)",
        [py, "scripts/build_dashboard.py"],
        skip=args.skip_dashboard,
    )

    _print_summary(results, auto_push=args.auto_push)


def _print_summary(results: list[tuple[str, bool]], auto_push: bool = False, tag: str = "sync_weekly") -> None:
    print("\n" + "=" * 62)
    print("  sync_weekly: 완료 요약")
    print("=" * 62)
    for label, ok in results:
        icon = "✓" if ok else "✗"
        print(f"  {icon}  {label}")
    failed = sum(1 for _, ok in results if not ok)
    print(f"\n  총 {len(results)}단계 / 실패 {failed}개")
    print("=" * 62)

    if auto_push:
        _git_commit_push(tag)


if __name__ == "__main__":
    main()
