from __future__ import annotations

"""KRX/US 전종목 마스터 동기화.

한국 데이터 소스 우선순위
--------------------------
1. DART corpCode.xml API (DART_API_KEY 있을 때)
2. Naver Finance HTML 스크래핑

미국 데이터 소스
----------------
- Wikipedia S&P 500 / NASDAQ 100 목록 (--us 또는 --us-sp500 / --us-ndx)
- 전체 NASDAQ/NYSE: --us-all (NASDAQ FTP에서 다운로드)
"""

import argparse
import re
import sys
from pathlib import Path

import requests

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from committee.core.database import upsert_ticker_master

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}


# ── 한국 ──────────────────────────────────────────────────────────

def _fetch_from_dart() -> list[dict]:
    try:
        from committee.tools.dart_client import fetch_dart_company_codes
        all_corps = fetch_dart_company_codes()
    except Exception as exc:
        print(f"dart_corp_code_fetch_failed: {exc}")
        return []
    rows = []
    for corp in all_corps:
        stock_code = (corp.get("stock_code") or "").strip()
        if not stock_code or len(stock_code) != 6:
            continue
        rows.append({
            "ticker": stock_code,
            "company_name": corp.get("company_name"),
            "market": "KR",
            "isin": None,
            "dart_corp_code": corp.get("dart_corp_code"),
        })
    return rows


def _fetch_from_naver() -> list[dict]:
    from committee.tools.krx_client import fetch_stock_master
    return fetch_stock_master()


# ── 미국 ──────────────────────────────────────────────────────────

def _parse_wikipedia_tickers(url: str, market: str) -> list[dict]:
    """Wikipedia 지수 구성종목 테이블에서 티커 파싱."""
    try:
        resp = requests.get(url, headers=_HEADERS, timeout=20)
        resp.raise_for_status()
        html = resp.text
    except Exception as exc:
        print(f"wikipedia_fetch_error[{market}]: {exc}")
        return []

    # <td><a href="...">AAPL</a></td> 또는 <td>AAPL</td> 패턴
    # Wikipedia S&P500 테이블: 첫 번째 컬럼이 티커
    ticker_pattern = re.compile(
        r'<td[^>]*>\s*<a[^>]*href="[^"]*"\s*[^>]*>\s*([A-Z]{1,5}(?:\.[A-Z])?)\s*</a>\s*</td>'
    )
    name_rows = re.findall(
        r'<tr[^>]*>(.*?)</tr>', html, re.DOTALL
    )

    results = []
    seen: set[str] = set()
    for row_html in name_rows:
        cells = re.findall(r'<td[^>]*>(.*?)</td>', row_html, re.DOTALL)
        if len(cells) < 2:
            continue
        # 첫 번째 셀에서 티커 추출
        raw_ticker = re.sub(r'<[^>]+>', '', cells[0]).strip()
        # 두 번째 셀에서 종목명 추출
        raw_name = re.sub(r'<[^>]+>', '', cells[1]).strip()
        # 티커 검증: 1~5 대문자 알파벳
        if not re.fullmatch(r'[A-Z]{1,5}', raw_ticker):
            continue
        if raw_ticker in seen:
            continue
        seen.add(raw_ticker)
        results.append({
            "ticker": raw_ticker,
            "company_name": raw_name or None,
            "market": market,
            "isin": None,
            "dart_corp_code": None,
        })
    return results


def _fetch_sp500() -> list[dict]:
    print("US: S&P 500 종목 수집 (Wikipedia)...")
    rows = _parse_wikipedia_tickers(
        "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies",
        "US_SP500",
    )
    print(f"  S&P 500 수집 완료: {len(rows)}개")
    return rows


def _fetch_nasdaq100() -> list[dict]:
    print("US: NASDAQ 100 종목 수집 (Wikipedia)...")
    rows = _parse_wikipedia_tickers(
        "https://en.wikipedia.org/wiki/Nasdaq-100",
        "US_NDX100",
    )
    print(f"  NASDAQ 100 수집 완료: {len(rows)}개")
    return rows


def _fetch_nasdaq_all() -> list[dict]:
    """NASDAQ FTP에서 전체 NASDAQ/NYSE 상장 종목 다운로드 (약 1만개)."""
    print("US: NASDAQ 전체 종목 수집 (NASDAQ FTP)...")
    results = []
    seen: set[str] = set()

    urls = {
        "NASDAQ": "https://api.nasdaq.com/api/screener/stocks?tableonly=true&limit=10000&exchange=nasdaq",
        "NYSE":   "https://api.nasdaq.com/api/screener/stocks?tableonly=true&limit=10000&exchange=nyse",
        "AMEX":   "https://api.nasdaq.com/api/screener/stocks?tableonly=true&limit=10000&exchange=amex",
    }
    headers = {**_HEADERS, "Accept": "application/json, text/plain, */*"}

    for market_name, url in urls.items():
        try:
            resp = requests.get(url, headers=headers, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            rows_data = (data.get("data") or {}).get("table", {}).get("rows") or []
            for item in rows_data:
                ticker = (item.get("symbol") or "").strip().upper()
                if not ticker or ticker in seen:
                    continue
                # ETF/펀드 제외
                if item.get("netchange") == "" and item.get("pctchange") == "":
                    continue
                seen.add(ticker)
                results.append({
                    "ticker": ticker,
                    "company_name": (item.get("name") or "").strip() or None,
                    "market": f"US_{market_name}",
                    "isin": None,
                    "dart_corp_code": None,
                })
            print(f"  {market_name}: {len(rows_data)}개")
        except Exception as exc:
            print(f"  nasdaq_api_error[{market_name}]: {exc}")

    print(f"  US 전체 수집 완료: {len(results)}개")
    return results


# ── 메인 ──────────────────────────────────────────────────────────

def main() -> None:
    import os

    parser = argparse.ArgumentParser(description="종목 마스터 동기화 (KR + US)")
    parser.add_argument("--kr", action="store_true", default=False, help="한국 종목 수집 (기본: DART 또는 Naver)")
    parser.add_argument("--us", action="store_true", default=False, help="미국 S&P500 + NASDAQ100 수집")
    parser.add_argument("--us-sp500", action="store_true", help="S&P 500만")
    parser.add_argument("--us-ndx", action="store_true", help="NASDAQ 100만")
    parser.add_argument("--us-all", action="store_true", help="NASDAQ/NYSE/AMEX 전체 (~1만개)")
    args = parser.parse_args()

    # 아무 플래그도 없으면 KR만 수집 (기존 동작 유지)
    do_kr = args.kr or not any([args.us, args.us_sp500, args.us_ndx, args.us_all])
    do_us = args.us or args.us_sp500 or args.us_ndx or args.us_all

    all_rows: list[dict] = []

    if do_kr:
        has_dart_key = bool(os.getenv("DART_API_KEY", "").strip())
        if has_dart_key:
            print("KR: DART API 사용")
            kr_rows = _fetch_from_dart()
        else:
            print("KR: DART_API_KEY 없음 → Naver Finance HTML 사용")
            kr_rows = _fetch_from_naver()
        print(f"  KR 수집 완료: {len(kr_rows)}개")
        all_rows.extend(kr_rows)

    if do_us:
        if args.us_all:
            all_rows.extend(_fetch_nasdaq_all())
        else:
            if args.us or args.us_sp500:
                all_rows.extend(_fetch_sp500())
            if args.us or args.us_ndx:
                all_rows.extend(_fetch_nasdaq100())

    total = len(all_rows)
    success = 0
    failed = 0

    print(f"\nsync_stock_master_fetched={total}")
    for row in all_rows:
        try:
            upsert_ticker_master(row)
            success += 1
        except Exception as exc:  # noqa: BLE001
            failed += 1
            print(f"sync_stock_master_upsert_failed[{row.get('ticker')}]: {exc}")

    print(f"sync_stock_master_done total={total} success={success} failed={failed}")


if __name__ == "__main__":
    main()
