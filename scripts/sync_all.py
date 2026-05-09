from __future__ import annotations

"""전체 데이터 한방 동기화 스크립트.

사용 예시
---------
    # 일반 일별 실행 (권장)
    python scripts/sync_all.py

    # 대시보드 빌드 생략
    python scripts/sync_all.py --skip-dashboard

    # 빠른 모드 (시장/매크로/수급만, 컨센서스·재무 생략)
    python scripts/sync_all.py --fast

    # 한국 재무제표 포함 (DART_API_KEY 필요)
    python scripts/sync_all.py --with-kr-financials

    # FRED 지표 전체 재백필 (최초 1회)
    python scripts/sync_all.py --backfill-macro-all
"""

import argparse
import os
import subprocess
import sys
from datetime import date, timedelta
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]


def _run(label: str, cmd: list[str], skip: bool = False) -> bool:
    if skip:
        print(f"[sync_all] ⏭  SKIP  {label}")
        return True
    print(f"\n[sync_all] ▶  {label}")
    result = subprocess.run(cmd, cwd=str(ROOT_DIR))
    ok = result.returncode == 0
    status = "✓" if ok else "✗"
    print(f"[sync_all] {status}  {label} (exit={result.returncode})")
    return ok


def _has_dart_key() -> bool:
    return bool(os.getenv("DART_API_KEY", "").strip())


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="전체 데이터 한방 동기화")
    p.add_argument("--fast", action="store_true", help="빠른 모드: 컨센서스·재무제표 생략 (시장/매크로/수급만)")
    p.add_argument("--with-kr-financials", action="store_true", help="KR 재무제표 포함 (DART_API_KEY 필요)")
    p.add_argument("--year", type=int, default=date.today().year - 1, help="KR 재무제표 연도 (기본: 전년도)")
    p.add_argument("--quarterly", action="store_true", help="KR 분기 보고서도 포함")
    p.add_argument("--skip-dashboard", action="store_true", help="대시보드 빌드 건너뜀")
    p.add_argument("--skip-consensus", action="store_true", help="컨센서스 수집 건너뜀")
    p.add_argument("--skip-us-financials", action="store_true", help="US 재무제표 건너뜀")
    p.add_argument("--backfill-macro-all", action="store_true", help="FRED 지표 전체 날짜 재백필 (최초 1회용)")
    return p.parse_args()


def main() -> None:
    args = _parse_args()
    py = sys.executable
    results: list[tuple[str, bool]] = []

    def step(label: str, cmd: list[str], skip: bool = False) -> None:
        ok = _run(label, cmd, skip=skip)
        results.append((label, ok))

    print("=" * 60)
    print("  sync_all: 전체 데이터 동기화 시작")
    print(f"  날짜: {date.today().isoformat()}")
    print("=" * 60)

    # ── 1. 시장 지수 (최근 2년치, Yahoo Finance) ─────────────────
    step(
        "시장 지수 일별 (market_daily)",
        [py, "scripts/backfill_market_daily_history.py",
         "--start-date", f"{date.today().year - 2}-01-01",
         "--end-date", date.today().isoformat()],
    )

    # ── 2. 매크로 지표 기본 (daily_macro) ────────────────────────
    step(
        "매크로 일별 기본 (daily_macro)",
        [py, "scripts/backfill_daily_macro_history.py",
         "--start-date", f"{date.today().year - 2}-01-01",
         "--end-date", date.today().isoformat()],
    )

    # ── 3. 매크로 지표 심화 (FRED: CPI/PMI/GDP/금리 등) ──────────
    # --days 7: 최근 7일치 NULL만 채움. 전체 백필이 필요하면 --backfill-macro-all 플래그 사용.
    step(
        "매크로 심화 지표 (FRED: CPI/PMI/GDP/금리)",
        [py, "scripts/backfill_macro_indicators.py",
         "--days", "0" if args.backfill_macro_all else "7"],
    )

    # ── 4. 수급 (외국인/기관/개인) ── 최근 7일 누락분만 ────────
    # 전체 백필은 sync_weekly.py 에서 수행.
    # 여기선 최근 7일 범위에서 DB에 없는 날짜만 빠르게 채움.
    _flow_start = (date.today() - timedelta(days=6)).isoformat()
    step(
        "외국인/기관/개인 수급 (market_flow_daily, 최근 7일 누락분)",
        [py, "scripts/backfill_market_flow_history.py",
         "--start-date", _flow_start,
         "--end-date", date.today().isoformat(),
         "--source", "NAVER",
         "--skip-existing"],
    )

    # ── 5. 종목 컨센서스 ─────────────────────────────────────────
    step(
        "종목 애널리스트 컨센서스 (stock_consensus)",
        [py, "scripts/sync_stock_consensus.py"],
        skip=args.fast or args.skip_consensus,
    )

    # ── 6. 미국 주식 재무제표 (yfinance, 무료) ────────────────────
    step(
        "미국 주식 재무제표 (financial_metric, US)",
        [py, "scripts/sync_financials.py", "--us"],
        skip=args.fast or args.skip_us_financials,
    )

    # ── 7. 한국 주식 재무제표 (DART API) ─────────────────────────
    if args.with_kr_financials:
        if not _has_dart_key():
            print("[sync_all] ⚠  DART_API_KEY 없음 → KR 재무제표 건너뜀")
            print("           환경변수 DART_API_KEY 를 설정하세요.")
            results.append(("KR 재무제표 (financial_metric, KR)", False))
        else:
            kr_cmd = [py, "scripts/sync_financials.py", "--year", str(args.year)]
            if args.quarterly:
                kr_cmd.append("--quarterly")
            step("KR 주식 재무제표 (financial_metric, KR)", kr_cmd)
    else:
        print("[sync_all] ⏭  SKIP  KR 재무제표 (--with-kr-financials 플래그 없음)")

    # ── 8. 대시보드 빌드 ──────────────────────────────────────────
    step(
        "대시보드 빌드 (docs/dashboard.html)",
        [py, "scripts/build_dashboard.py"],
        skip=args.skip_dashboard,
    )

    # ── 결과 요약 ────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("  sync_all: 완료 요약")
    print("=" * 60)
    for label, ok in results:
        icon = "✓" if ok else "✗"
        print(f"  {icon}  {label}")

    failed = sum(1 for _, ok in results if not ok)
    print(f"\n  총 {len(results)}단계 / 실패 {failed}개")
    print("=" * 60)


if __name__ == "__main__":
    main()
