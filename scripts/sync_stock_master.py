from __future__ import annotations

"""KRX 전종목 마스터 동기화.

데이터 소스 우선순위
--------------------
1. DART corpCode.xml API (DART_API_KEY 있을 때) — 상장/비상장 전체, dart_corp_code 포함
2. Naver Finance 시총순위 HTML 스크래핑 — KOSPI/KOSDAQ, 인증 불필요
"""

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from committee.core.database import upsert_ticker_master


def _fetch_from_dart() -> list[dict]:
    """DART corpCode.xml에서 상장 종목만 추출하여 ticker_master 형식으로 반환."""
    try:
        from committee.tools.dart_client import fetch_dart_company_codes
        all_corps = fetch_dart_company_codes()
    except Exception as exc:
        print(f"dart_corp_code_fetch_failed: {exc}")
        return []

    # stock_code 있는 것만 상장사
    rows = []
    for corp in all_corps:
        stock_code = (corp.get("stock_code") or "").strip()
        if not stock_code or len(stock_code) != 6:
            continue
        rows.append({
            "ticker": stock_code,
            "company_name": corp.get("company_name"),
            "market": "KR",          # DART는 시장구분 없음 → 'KR' 통합
            "isin": None,
            "dart_corp_code": corp.get("dart_corp_code"),
        })
    return rows


def _fetch_from_naver() -> list[dict]:
    """Naver Finance 시총순위 HTML 스크래핑 (DART_API_KEY 없을 때 fallback)."""
    from committee.tools.krx_client import fetch_stock_master
    return fetch_stock_master()


def main() -> None:
    import os

    has_dart_key = bool(os.getenv("DART_API_KEY", "").strip())

    if has_dart_key:
        print("sync_stock_master: DART API 사용")
        rows = _fetch_from_dart()
        source = "dart"
    else:
        print("sync_stock_master: DART_API_KEY 없음 → Naver Finance HTML 사용")
        rows = _fetch_from_naver()
        source = "naver"

    total = len(rows)
    success = 0
    failed = 0

    print(f"sync_stock_master_fetched={total} source={source}")
    for row in rows:
        try:
            upsert_ticker_master(row)
            success += 1
        except Exception as exc:  # noqa: BLE001
            failed += 1
            ticker = row.get("ticker")
            print(f"sync_stock_master_upsert_failed[{ticker}]: {exc}")

    print(f"sync_stock_master_done total={total} success={success} failed={failed}")


if __name__ == "__main__":
    main()
