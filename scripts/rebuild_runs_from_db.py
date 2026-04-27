from __future__ import annotations

"""Rebuild run snapshot files from historical DB rows.

Purpose
- Fix polluted run files created with live values on historical dates.
- Reconstruct `runs/YYYY-MM-DD/snapshot.json` and `runs/YYYY-MM-DD.json`
  using date-aligned values from `data/investment.db`.
"""

import argparse
import json
import sqlite3
import subprocess
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from committee.schemas.snapshot import Snapshot


DB_PATH = ROOT_DIR / "data" / "investment.db"
RUNS_DIR = ROOT_DIR / "runs"


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="DB 히스토리 기반 run snapshot 재구성")
    parser.add_argument("--start-date", required=True, help="시작일 (YYYY-MM-DD)")
    parser.add_argument("--end-date", required=True, help="종료일 (YYYY-MM-DD)")
    parser.add_argument(
        "--refresh-market-daily",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="재구성 전에 Yahoo 히스토리로 market_daily를 갱신",
    )
    parser.add_argument(
        "--purge-range",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="재구성 전 대상 구간의 오염된 일별 행 삭제 (기본: true)",
    )
    parser.add_argument("--dry-run", action="store_true", help="쓰기 없이 대상/상태만 출력")
    return parser.parse_args()


def _iter_dates(start_d: date, end_d: date) -> list[date]:
    out: list[date] = []
    cur = start_d
    while cur <= end_d:
        out.append(cur)
        cur += timedelta(days=1)
    return out


def _fetch_one(conn: sqlite3.Connection, query: str, params: tuple) -> sqlite3.Row | None:
    return conn.execute(query, params).fetchone()


def _fmt_pct(v: float | None) -> str:
    if v is None:
        return "n/a"
    return f"{v:+.2f}%"


def _fmt_num(v: float | None, digits: int = 2) -> str:
    if v is None:
        return "n/a"
    return f"{v:.{digits}f}"


def _build_snapshot_from_db(conn: sqlite3.Connection, target_date: str) -> Snapshot:
    md = _fetch_one(
        conn,
        """
        SELECT date, kospi_pct, kosdaq_pct, sp500_pct, nasdaq_pct, dow_pct,
               kospi, kosdaq, sp500, nasdaq, dow,
               usdkrw, usdkrw_pct, vix
        FROM market_daily
        WHERE date <= ?
        ORDER BY date DESC
        LIMIT 1
        """,
        (target_date,),
    )
    if md is None:
        raise RuntimeError(f"market_daily_missing[{target_date}]")

    mf = _fetch_one(
        conn,
        """
        SELECT date, foreign_net, institution_net, retail_net
        FROM market_flow_daily
        WHERE date <= ?
        ORDER BY date DESC
        LIMIT 1
        """,
        (target_date,),
    )
    flow_missing = mf is None
    if mf is None:
        # Keep rebuild resilient: market data can still be reconstructed even when
        # historical flow rows were never backfilled.
        mf = {"date": None, "foreign_net": 0.0, "institution_net": 0.0, "retail_net": 0.0}

    dm = _fetch_one(
        conn,
        """
        SELECT date, us10y, us2y, spread_2_10, vix, dxy, usdkrw,
               vix3m, vix_term_spread, oil_wti,
               fed_funds_rate, real_rate, hy_oas, ig_oas, fed_balance_sheet
        FROM daily_macro
        WHERE date <= ?
        ORDER BY date DESC
        LIMIT 1
        """,
        (target_date,),
    )
    macro_missing = dm is None
    if dm is None:
        # Keep reconstruction available for market index validation even when
        # daily_macro history is missing for this range.
        dm = {
            "date": None,
            "us10y": None,
            "us2y": None,
            "spread_2_10": None,
            "vix": None,
            "dxy": None,
            "usdkrw": None,
            "vix3m": None,
            "vix_term_spread": None,
            "oil_wti": None,
            "fed_funds_rate": None,
            "real_rate": None,
            "hy_oas": None,
            "ig_oas": None,
            "fed_balance_sheet": None,
        }

    mm = _fetch_one(
        conn,
        """
        SELECT date, unemployment_rate, cpi_yoy, core_cpi_yoy, pce_yoy, pmi,
               retail_sales_mom, nfp_change, wage_level, wage_yoy, export_yoy
        FROM monthly_macro
        WHERE date <= ?
        ORDER BY date DESC
        LIMIT 1
        """,
        (target_date,),
    )

    qm = _fetch_one(
        conn,
        """
        SELECT date, real_gdp, gdp_qoq_annualized
        FROM quarterly_macro
        WHERE date <= ?
        ORDER BY date DESC
        LIMIT 1
        """,
        (target_date,),
    )

    kospi_pct = float(md["kospi_pct"]) if md["kospi_pct"] is not None else 0.0
    usdkrw = float(md["usdkrw"]) if md["usdkrw"] is not None else 0.0
    if flow_missing:
        flow_note = "수급 데이터 없음 (market_flow_daily missing)"
    else:
        flow_note = (
            f"외국인 {float(mf['foreign_net'] or 0.0):+.0f}억, "
            f"기관 {float(mf['institution_net'] or 0.0):+.0f}억, "
            f"개인 {float(mf['retail_net'] or 0.0):+.0f}억"
        )
    market_note = (
        f"KOSPI {_fmt_pct(md['kospi_pct'])}, "
        f"USD/KRW {_fmt_num(md['usdkrw'], 2)}. "
        f"DB historical rebuild ({target_date}, market_asof={md['date']})."
    )
    if macro_missing:
        market_note = (market_note + " macro_missing").strip()

    snapshot_payload = {
        "market_summary": {
            "note": market_note[:500],
            "kospi_change_pct": kospi_pct,
            "usdkrw": usdkrw,
        },
        "flow_summary": {
            "note": flow_note[:500],
            "foreign_net": float(mf["foreign_net"] or 0.0),
            "institution_net": float(mf["institution_net"] or 0.0),
            "retail_net": float(mf["retail_net"] or 0.0),
        },
        "korean_market_flow": None,
        "sector_moves": ["n/a", "n/a", "n/a"],
        "news_headlines": [f"historical_rebuild_from_db:{target_date}"],
        "watchlist": ["SPY", "QQQ", "XLK"],
        "markets": {
            "kr": {
                "kospi": md["kospi"],
                "kosdaq": md["kosdaq"],
                "kospi_pct": float(md["kospi_pct"] or 0.0),
                "kosdaq_pct": float(md["kosdaq_pct"] or 0.0),
            },
            "us": {
                "sp500": md["sp500"],
                "nasdaq": md["nasdaq"],
                "dow": md["dow"],
                "sp500_pct": float(md["sp500_pct"] or 0.0),
                "nasdaq_pct": float(md["nasdaq_pct"] or 0.0),
                "dow_pct": float(md["dow_pct"] or 0.0),
            },
            "fx": {
                "usdkrw": float(md["usdkrw"] or 0.0),
                "usdkrw_pct": float(md["usdkrw_pct"] or 0.0),
            },
            "volatility": {
                "vix": float(md["vix"] or 0.0),
            },
        },
        "macro": {
            "daily": {
                "us10y": dm["us10y"],
                "us2y": dm["us2y"],
                "spread_2_10": dm["spread_2_10"],
                "vix": dm["vix"],
                "dxy": dm["dxy"],
                "usdkrw": dm["usdkrw"],
                "vix3m": dm["vix3m"],
                "vix_term_spread": dm["vix_term_spread"],
                "oil_wti": dm["oil_wti"],
            },
            "monthly": {
                "unemployment_rate": mm["unemployment_rate"] if mm else None,
                "cpi_yoy": mm["cpi_yoy"] if mm else None,
                "core_cpi_yoy": mm["core_cpi_yoy"] if mm else None,
                "pce_yoy": mm["pce_yoy"] if mm else None,
                "pmi": mm["pmi"] if mm else None,
                "retail_sales_mom": mm["retail_sales_mom"] if mm else None,
                "nfp_change": mm["nfp_change"] if mm else None,
                "wage_growth": mm["wage_level"] if mm else None,
                "wage_level": mm["wage_level"] if mm else None,
                "wage_yoy": mm["wage_yoy"] if mm else None,
                "export_yoy": mm["export_yoy"] if mm else None,
            },
            "quarterly": {
                "real_gdp": qm["real_gdp"] if qm else None,
                "gdp_qoq_annualized": qm["gdp_qoq_annualized"] if qm else None,
            },
            "structural": {
                "fed_funds_rate": dm["fed_funds_rate"],
                "real_rate": dm["real_rate"],
                "hy_oas": dm["hy_oas"],
                "ig_oas": dm["ig_oas"],
                "fed_balance_sheet": dm["fed_balance_sheet"],
            },
        },
    }
    return Snapshot.model_validate(snapshot_payload)


def _purge_range_rows(*, start_date: str, end_date: str) -> None:
    if not DB_PATH.exists():
        return
    conn = sqlite3.connect(str(DB_PATH))
    try:
        cur1 = conn.execute(
            "DELETE FROM market_daily WHERE date >= ? AND date <= ?",
            (start_date, end_date),
        )
        cur2 = conn.execute(
            "DELETE FROM market_flow_daily WHERE date >= ? AND date <= ?",
            (start_date, end_date),
        )
        conn.commit()
        print(
            "purge_range_done "
            f"market_daily={int(cur1.rowcount or 0)} "
            f"market_flow_daily={int(cur2.rowcount or 0)}"
        )
    finally:
        conn.close()


def _write_artifacts(*, target_date: str, snapshot: Snapshot) -> None:
    run_dir = RUNS_DIR / target_date
    run_dir.mkdir(parents=True, exist_ok=True)
    snapshot_json = snapshot.model_dump()

    (run_dir / "snapshot.json").write_text(
        json.dumps(snapshot_json, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    summary_json = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "market_date": target_date,
        "snapshot": snapshot_json,
    }
    (RUNS_DIR / f"{target_date}.json").write_text(
        json.dumps(summary_json, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def _refresh_market_daily_history(*, start_date: str, end_date: str) -> None:
    cmd = [
        sys.executable,
        str(ROOT_DIR / "scripts" / "backfill_market_daily_history.py"),
        "--start-date",
        start_date,
        "--end-date",
        end_date,
    ]
    result = subprocess.run(cmd, cwd=str(ROOT_DIR), capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "refresh_market_daily_failed")
    if result.stdout.strip():
        print(result.stdout.strip())


def main() -> None:
    args = _parse_args()
    start_d = date.fromisoformat(str(args.start_date))
    end_d = date.fromisoformat(str(args.end_date))
    if end_d < start_d:
        raise ValueError("end-date must be >= start-date")
    if not DB_PATH.exists():
        raise RuntimeError(f"db_not_found[{DB_PATH}]")
    if args.purge_range:
        print(f"purge_range[{start_d.isoformat()}..{end_d.isoformat()}]: start")
        _purge_range_rows(
            start_date=start_d.isoformat(),
            end_date=end_d.isoformat(),
        )
    if args.refresh_market_daily:
        print(f"refresh_market_daily[{start_d.isoformat()}..{end_d.isoformat()}]: start")
        _refresh_market_daily_history(
            start_date=start_d.isoformat(),
            end_date=end_d.isoformat(),
        )
        print("refresh_market_daily: done")

    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    try:
        targets = _iter_dates(start_d, end_d)
        ok = 0
        fail = 0
        for d in targets:
            ds = d.isoformat()
            try:
                snapshot = _build_snapshot_from_db(conn, ds)
                if not args.dry_run:
                    _write_artifacts(target_date=ds, snapshot=snapshot)
                print(f"rebuild_ok[{ds}]")
                ok += 1
            except Exception as exc:  # noqa: BLE001
                print(f"rebuild_fail[{ds}]: {exc}")
                fail += 1
        print(f"rebuild_done ok={ok} fail={fail} dry_run={args.dry_run}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
