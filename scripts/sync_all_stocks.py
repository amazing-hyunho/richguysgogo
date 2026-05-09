"""
전체 종목 데이터 수집 스크립트 (컨센서스 + 재무제표).

ticker_master에 등록된 모든 KR 종목 + 지정 US 종목을 대상으로
컨센서스(목표주가/투자의견)와 재무제표(매출/이익/ROE 등)를 수집합니다.

소요 시간 안내
--------------
- KR 전체 (~2,500종목) 컨센서스: 약 1~3시간 (종목당 1~3초)
- US 워치리스트 (10종목) 재무제표: 약 1~2분
- KR 재무제표 (DART API): DART_API_KEY 필요, 추가 1~2시간

재시작 지원
-----------
--resume 플래그를 사용하면 오늘 날짜로 이미 수집된 종목은 건너뜁니다.
중단 후 다시 실행할 때 유용합니다.

Usage
-----
# 기본 (KR 전체 컨센서스 + US 재무제표)
    python scripts/sync_all_stocks.py

# 재시작 모드 (이미 수집된 종목 건너뜀)
    python scripts/sync_all_stocks.py --resume

# KR 재무제표도 포함 (DART_API_KEY 필요, 매우 느림)
    python scripts/sync_all_stocks.py --with-kr-financials --year 2024

# 상위 N종목만 (시가총액 순, ticker_master 등록 순)
    python scripts/sync_all_stocks.py --top 300

# 특정 종목만 테스트
    python scripts/sync_all_stocks.py --tickers 005930 000660 035420

# US 종목 추가
    python scripts/sync_all_stocks.py --us-tickers AAPL NVDA MSFT TSLA

# 대시보드 빌드 포함
    python scripts/sync_all_stocks.py --build-dashboard
"""

from __future__ import annotations

import argparse
import os
import sys
import time
from datetime import date as dt_date
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from committee.core.database import (
    connect,
    init_db,
    list_consensus_tickers,
    safe_upsert_stock_consensus,
    upsert_financial_metric,
)
from committee.tools.stock_consensus_provider import fetch_stock_consensus
from committee.tools.us_financial_provider import fetch_us_financials

# ---------------------------------------------------------------------------
# 기본 US 워치리스트 (재무제표)
# ---------------------------------------------------------------------------

DEFAULT_US_TICKERS = [
    "AAPL", "MSFT", "NVDA", "GOOGL", "AMZN",
    "META", "TSLA", "AVGO", "JPM", "V",
    "ORCL", "AMD", "INTC", "QCOM", "MU",
]

# ---------------------------------------------------------------------------
# 헬퍼
# ---------------------------------------------------------------------------


def _get_all_kr_tickers(top: int | None = None) -> list[str]:
    """ticker_master에서 KR 6자리 종목코드 전체 로드."""
    init_db()
    with connect() as conn:
        rows = conn.execute(
            "SELECT ticker FROM ticker_master ORDER BY ticker"
        ).fetchall()
    tickers = [
        str(r["ticker"]).strip().upper()
        for r in rows
        if str(r["ticker"]).strip().isdigit() and len(str(r["ticker"]).strip()) == 6
    ]
    if top:
        tickers = tickers[:top]
    return tickers


def _already_fetched_today(today: str) -> set[str]:
    """오늘 날짜로 이미 저장된 컨센서스 티커 집합."""
    try:
        init_db()
        with connect() as conn:
            rows = conn.execute(
                "SELECT DISTINCT ticker FROM stock_consensus WHERE date = ?",
                (today,),
            ).fetchall()
        return {str(r["ticker"]) for r in rows}
    except Exception:
        return set()


def _fmt_eta(elapsed: float, done: int, total: int) -> str:
    if done == 0:
        return "계산 중..."
    rate = done / elapsed
    remaining = (total - done) / rate
    h, m = divmod(int(remaining), 3600)
    m, s = divmod(m, 60)
    if h > 0:
        return f"약 {h}시간 {m}분 남음"
    if m > 0:
        return f"약 {m}분 {s}초 남음"
    return f"약 {s}초 남음"


# ---------------------------------------------------------------------------
# KR 컨센서스 수집
# ---------------------------------------------------------------------------


def sync_kr_consensus(
    tickers: list[str],
    today: str,
    resume: bool,
    delay: float = 0.5,
) -> dict:
    already = _already_fetched_today(today) if resume else set()
    targets = [t for t in tickers if t not in already]

    total = len(tickers)
    skip_count = total - len(targets)
    print(f"\n[kr_consensus] 대상 {total}종목 (재시작 건너뜀 {skip_count}종목, 수집 예정 {len(targets)}종목)")
    if not targets:
        print("[kr_consensus] 모두 이미 수집됨")
        return {"ok": 0, "fail": 0, "skip": skip_count}

    ok = fail = 0
    start = time.time()

    for i, ticker in enumerate(targets, 1):
        try:
            result = fetch_stock_consensus(ticker)
            safe_upsert_stock_consensus(
                ticker=result["ticker"],
                date=today,
                market=result.get("market"),
                source=result.get("source"),
                company_name=result.get("company_name"),
                currency=result.get("currency"),
                current_price=result.get("current_price"),
                target_mean_price=result.get("target_mean_price"),
                target_high_price=result.get("target_high_price"),
                target_low_price=result.get("target_low_price"),
                recommendation_key=result.get("recommendation_key"),
                recommendation_mean=result.get("recommendation_mean"),
                num_analysts=result.get("num_analysts"),
                forward_eps=result.get("forward_eps"),
                forward_pe=result.get("forward_pe"),
                revenue_estimate_avg=result.get("revenue_estimate_avg"),
            )
            ok += 1
        except Exception as exc:
            fail += 1
            print(f"  [FAIL] {ticker}: {exc}")

        # 진행률 출력 (50종목마다)
        if i % 50 == 0 or i == len(targets):
            elapsed = time.time() - start
            eta = _fmt_eta(elapsed, i, len(targets))
            pct = i / len(targets) * 100
            print(f"  [{i}/{len(targets)} {pct:.0f}%] ok={ok} fail={fail}  {eta}")

        if delay > 0:
            time.sleep(delay)

    elapsed = time.time() - start
    print(f"[kr_consensus] 완료 ok={ok} fail={fail} skip={skip_count} 소요={elapsed:.0f}초")
    return {"ok": ok, "fail": fail, "skip": skip_count}


# ---------------------------------------------------------------------------
# US 재무제표 수집
# ---------------------------------------------------------------------------


def sync_us_financials(tickers: list[str]) -> dict:
    print(f"\n[us_financials] {len(tickers)}개 US 종목 재무제표 수집")
    ok = fail = 0

    for ticker in tickers:
        try:
            data = fetch_us_financials(ticker, annual_periods=4, quarterly_periods=4)
            for period_type, rows in data.items():
                for row in rows:
                    if not row.get("period_date"):
                        continue
                    upsert_financial_metric({
                        "ticker": ticker,
                        "business_year": (row["period_date"] or "")[:7],
                        "report_code": period_type,
                        "period_type": period_type,
                        "currency": "USD",
                        **{k: row.get(k) for k in [
                            "revenue", "gross_profit", "operating_income", "net_income",
                            "total_assets", "total_liabilities", "total_equity",
                            "shares_outstanding", "eps_basic", "eps_diluted",
                            "cash_and_equivalents", "total_debt",
                            "operating_cashflow", "capital_expenditure", "free_cashflow",
                            "gross_margin", "operating_margin", "net_margin",
                            "roe", "roa", "debt_ratio",
                        ]},
                    })
            ok += 1
            print(f"  ✅ {ticker}")
        except Exception as exc:
            fail += 1
            print(f"  ❌ {ticker}: {exc}")

    print(f"[us_financials] 완료 ok={ok} fail={fail}")
    return {"ok": ok, "fail": fail}


# ---------------------------------------------------------------------------
# KR 재무제표 (DART)
# ---------------------------------------------------------------------------


def sync_kr_financials(tickers: list[str], year: int, quarterly: bool) -> dict:
    """DART API를 사용한 KR 재무제표 수집."""
    # sync_financials.py의 로직을 재사용
    import subprocess
    cmd = [sys.executable, "scripts/sync_financials.py", "--year", str(year)]
    if quarterly:
        cmd.append("--quarterly")
    if tickers:
        cmd += ["--kr-tickers"] + tickers
    print(f"\n[kr_financials] DART 재무제표 수집: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=str(ROOT_DIR))
    ok = result.returncode == 0
    print(f"[kr_financials] {'완료' if ok else '실패'} (exit {result.returncode})")
    return {"ok": 1 if ok else 0, "fail": 0 if ok else 1}


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="전체 종목 컨센서스+재무제표 수집")
    p.add_argument("--tickers", nargs="+", metavar="TICKER",
                   help="특정 KR 종목만 지정 (기본: ticker_master 전체)")
    p.add_argument("--top", type=int, default=None,
                   help="ticker_master 등록 순 상위 N종목만 (예: --top 300)")
    p.add_argument("--resume", action="store_true",
                   help="오늘 이미 수집한 종목 건너뜀 (재시작 모드)")
    p.add_argument("--delay", type=float, default=0.5,
                   help="종목당 요청 간격(초), 기본 0.5초")
    p.add_argument("--skip-consensus", action="store_true",
                   help="컨센서스 수집 건너뜀")
    p.add_argument("--us-tickers", nargs="+", metavar="TICKER",
                   help="US 재무제표 대상 티커 (기본: 내장 워치리스트)")
    p.add_argument("--skip-us-financials", action="store_true",
                   help="US 재무제표 건너뜀")
    p.add_argument("--with-kr-financials", action="store_true",
                   help="KR 재무제표도 수집 (DART_API_KEY 필요)")
    p.add_argument("--year", type=int, default=dt_date.today().year - 1,
                   help="KR 재무제표 연도 (기본: 전년도)")
    p.add_argument("--quarterly", action="store_true",
                   help="KR 분기 보고서 포함")
    p.add_argument("--build-dashboard", action="store_true",
                   help="수집 완료 후 대시보드 빌드")
    p.add_argument("--date", default=None,
                   help="저장 기준 날짜 (YYYY-MM-DD, 기본: 오늘)")
    return p.parse_args()


def main() -> None:
    args = _parse_args()
    today = args.date or dt_date.today().isoformat()
    results: list[tuple[str, dict]] = []

    print("=" * 60)
    print("  sync_all_stocks: 전체 종목 데이터 수집")
    print(f"  날짜: {today}")
    print("=" * 60)

    # ── KR 컨센서스 ─────────────────────────────────────────────
    if not args.skip_consensus:
        if args.tickers:
            kr_tickers = [t.strip().upper() for t in args.tickers]
            print(f"\n[setup] 지정 종목 {len(kr_tickers)}개 사용")
        else:
            kr_tickers = _get_all_kr_tickers(top=args.top)
            label = f"전체 {len(kr_tickers)}종목" if not args.top else f"상위 {len(kr_tickers)}종목"
            print(f"\n[setup] ticker_master에서 KR 종목 로드: {label}")

        if not kr_tickers:
            print("[setup] ⚠  종목 없음. 먼저 실행: python scripts/sync_stock_master.py")
        else:
            r = sync_kr_consensus(kr_tickers, today=today, resume=args.resume, delay=args.delay)
            results.append(("KR 컨센서스", r))

    # ── US 재무제표 ──────────────────────────────────────────────
    if not args.skip_us_financials:
        us_tickers = [t.strip().upper() for t in args.us_tickers] if args.us_tickers else DEFAULT_US_TICKERS
        r = sync_us_financials(us_tickers)
        results.append(("US 재무제표", r))

    # ── KR 재무제표 (DART) ───────────────────────────────────────
    if args.with_kr_financials:
        dart_key = os.getenv("DART_API_KEY", "").strip() or os.getenv("OPEN_DART_API_KEY", "").strip()
        if not dart_key:
            print("\n[kr_financials] ⚠  DART_API_KEY 없음 → 건너뜀")
            print("  환경변수 DART_API_KEY 를 설정하세요. (https://opendart.fss.or.kr)")
            results.append(("KR 재무제표 (DART)", {"ok": 0, "fail": 1}))
        else:
            kr_fin_tickers = [t.strip().upper() for t in args.tickers] if args.tickers else []
            r = sync_kr_financials(kr_fin_tickers, year=args.year, quarterly=args.quarterly)
            results.append(("KR 재무제표 (DART)", r))

    # ── 대시보드 빌드 ────────────────────────────────────────────
    if args.build_dashboard:
        import subprocess
        print("\n[dashboard] 빌드 중...")
        proc = subprocess.run([sys.executable, "scripts/build_dashboard.py"], cwd=str(ROOT_DIR))
        ok = proc.returncode == 0
        results.append(("대시보드 빌드", {"ok": 1 if ok else 0, "fail": 0 if ok else 1}))
        print(f"[dashboard] {'✅ 완료' if ok else '❌ 실패'}")

    # ── 요약 ─────────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("  완료 요약")
    print("=" * 60)
    for label, r in results:
        ok = r.get("ok", 0)
        fail = r.get("fail", 0)
        skip = r.get("skip", 0)
        print(f"  {label}: 성공 {ok} / 실패 {fail}" + (f" / 건너뜀 {skip}" if skip else ""))
    print("=" * 60)


if __name__ == "__main__":
    main()
