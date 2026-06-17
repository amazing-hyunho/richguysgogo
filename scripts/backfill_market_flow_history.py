from __future__ import annotations

"""Backfill market_flow_daily by date range with strict date matching.

Policy
- Fetch KRX first, then Naver fallback (AUTO).
- Weekends are skipped entirely (KRX does not trade Sat/Sun).
- If returned flow date != target date, treat as missing and store NULLs
  (handles most public holidays via stale-date detection).
- Holiday heuristic: if fetched values are identical to the previous
  trading day's values, treat the day as a market holiday and store NULLs.
  This catches the edge case where a source returns the prior day's data
  under the holiday's date (i.e., stale-date check passes but data is stale).
"""

import argparse
from datetime import UTC, date, datetime, timedelta
import sqlite3
import time
from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from committee.core.database import init_db
from committee.tools.krx_market_flow_provider import get_korean_market_flow_krx
from committee.tools.naver_market_flow_provider import get_korean_market_flow_naver


DB_PATH = ROOT_DIR / "data" / "investment.db"


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Backfill market_flow_daily history (strict date match).")
    parser.add_argument("--start-date", required=True, help="Inclusive start date (YYYY-MM-DD).")
    parser.add_argument("--end-date", required=True, help="Inclusive end date (YYYY-MM-DD).")
    parser.add_argument(
        "--source",
        choices=["AUTO", "KRX", "NAVER"],
        default="AUTO",
        help="Flow source selection (default: AUTO)",
    )
    parser.add_argument("--sleep-ms", type=int, default=250, help="Sleep between dates.")
    parser.add_argument("--dry-run", action="store_true", help="Print updates without writing DB.")
    parser.add_argument(
        "--skip-existing", action="store_true",
        help="이미 DB에 값이 있는 날짜는 API 호출 없이 건너뜀 (빠른 일별 실행용)",
    )
    return parser.parse_args()


def _iter_dates(start_d: date, end_d: date) -> list[date]:
    """Return weekdays only (Mon–Fri). KRX does not trade on weekends."""
    out: list[date] = []
    cur = start_d
    while cur <= end_d:
        if cur.weekday() < 5:  # 0=Mon … 4=Fri; skip Sat=5, Sun=6
            out.append(cur)
        cur += timedelta(days=1)
    return out


def _aggregate(flow: dict) -> tuple[float, float, float]:
    markets = (flow or {}).get("market", {}) or {}
    kospi = markets.get("KOSPI", {}) or {}
    kosdaq = markets.get("KOSDAQ", {}) or {}
    foreign_total = int(kospi.get("foreign", 0)) + int(kosdaq.get("foreign", 0))
    institution_total = int(kospi.get("institution", 0)) + int(kosdaq.get("institution", 0))
    retail_total = int(kospi.get("individual", 0)) + int(kosdaq.get("individual", 0))
    return float(foreign_total), float(institution_total), float(retail_total)


def _try_source_once(source: str, target: date) -> tuple[dict | None, str | None]:
    target_s = target.isoformat()
    try:
        if source == "KRX":
            flow = get_korean_market_flow_krx(asof=target)
        elif source == "NAVER":
            flow = get_korean_market_flow_naver(asof=target)
        else:
            return None, f"unsupported_source[{source}]"
        got = str((flow or {}).get("date", "")).strip()
        if got != target_s:
            return None, f"{source.lower()}_stale_date[{got}]"
        return flow, None
    except Exception as exc:  # noqa: BLE001
        return None, f"{source.lower()}_error[{exc}]"


def _fetch_flow(target: date, source: str) -> tuple[dict | None, str | None]:
    if source in ("KRX", "NAVER"):
        return _try_source_once(source, target)
    flow, err = _try_source_once("KRX", target)
    if flow is not None:
        return flow, None
    flow2, err2 = _try_source_once("NAVER", target)
    if flow2 is not None:
        return flow2, None
    return None, f"auto_failed[{err}; {err2}]"


def main() -> None:
    args = _parse_args()
    start_d = date.fromisoformat(str(args.start_date))
    end_d = date.fromisoformat(str(args.end_date))
    if end_d < start_d:
        raise ValueError("end-date must be >= start-date")

    init_db(DB_PATH)
    conn = sqlite3.connect(DB_PATH)
    try:
        now_iso = datetime.now(UTC).isoformat().replace("+00:00", "Z")

        # --skip-existing: 이미 값이 있는 날짜의 날짜+수치를 미리 조회.
        # 수치도 함께 로드해 공휴일 휴리스틱(직전 거래일과 동일 수치 판별)에 활용.
        existing_dates: set[str] = set()
        existing_values_map: dict[str, tuple[float, float, float]] = {}
        if args.skip_existing:
            ex_rows = conn.execute(
                "SELECT date, foreign_net, institution_net, retail_net FROM market_flow_daily "
                "WHERE foreign_net IS NOT NULL OR institution_net IS NOT NULL"
            ).fetchall()
            for r in ex_rows:
                existing_dates.add(r[0])
                if r[1] is not None:
                    existing_values_map[r[0]] = (float(r[1]), float(r[2] or 0), float(r[3] or 0))

        # 공휴일 휴리스틱용: 직전 거래일 수치를 DB에서 초기화
        # (start_d 이전 마지막 non-NULL 행)
        _prev_row = conn.execute(
            "SELECT foreign_net, institution_net, retail_net FROM market_flow_daily "
            "WHERE foreign_net IS NOT NULL AND date < ? ORDER BY date DESC LIMIT 1",
            (start_d.isoformat(),),
        ).fetchone()
        PrevVals = tuple[float, float, float] | None
        prev_values: PrevVals = (
            (float(_prev_row[0]), float(_prev_row[1] or 0), float(_prev_row[2] or 0))
            if _prev_row else None
        )

        changed = 0
        missing = 0
        skipped = 0
        holiday_skipped = 0
        for d in _iter_dates(start_d, end_d):
            ds = d.isoformat()
            if ds in existing_dates:
                # 스킵된 날짜의 수치로 prev_values 갱신 (이후 공휴일 판별 정확도 유지)
                if ds in existing_values_map:
                    prev_values = existing_values_map[ds]
                skipped += 1
                continue
            flow, reason = _fetch_flow(d, str(args.source))
            if flow is None:
                foreign_net = None
                institution_net = None
                retail_net = None
                missing += 1
                print(f"flow_missing[{ds}]: {reason}")
            else:
                foreign_net, institution_net, retail_net = _aggregate(flow)
                curr = (foreign_net, institution_net, retail_net)
                # 공휴일 휴리스틱: 직전 거래일과 수치가 완전히 동일하면
                # 소스가 전일 데이터를 그대로 반환한 것으로 간주하고 NULL 처리.
                if prev_values is not None and curr == prev_values:
                    foreign_net = None
                    institution_net = None
                    retail_net = None
                    holiday_skipped += 1
                    missing += 1
                    print(f"flow_holiday_skip[{ds}]: values identical to prev trading day (market closed?)")
                else:
                    prev_values = curr
            if args.dry_run:
                print(
                    f"{ds} foreign={foreign_net} institution={institution_net} "
                    f"retail={retail_net}"
                )
            else:
                conn.execute(
                    """
                    INSERT INTO market_flow_daily (
                        date, foreign_net, institution_net, retail_net, foreign_20d, foreign_60d, created_at
                    ) VALUES (
                        :date, :foreign_net, :institution_net, :retail_net, :foreign_20d, :foreign_60d, :created_at
                    )
                    ON CONFLICT(date) DO UPDATE SET
                        foreign_net=excluded.foreign_net,
                        institution_net=excluded.institution_net,
                        retail_net=excluded.retail_net,
                        foreign_20d=excluded.foreign_20d,
                        foreign_60d=excluded.foreign_60d,
                        created_at=excluded.created_at;
                    """,
                    {
                        "date": ds,
                        "foreign_net": foreign_net,
                        "institution_net": institution_net,
                        "retail_net": retail_net,
                        "foreign_20d": None,
                        "foreign_60d": None,
                        "created_at": now_iso,
                    },
                )
                changed += 1
            time.sleep(max(0, int(args.sleep_ms)) / 1000.0)
        if not args.dry_run:
            conn.commit()
        print(
            f"backfill_market_flow_done changed={changed} missing={missing} "
            f"skipped={skipped} holiday_skipped={holiday_skipped} "
            f"range={start_d.isoformat()}..{end_d.isoformat()} dry_run={args.dry_run}"
        )
    finally:
        conn.close()


if __name__ == "__main__":
    main()
