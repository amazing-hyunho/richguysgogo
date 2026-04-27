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
from committee.schemas.snapshot import Snapshot


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
    parser.add_argument(
        "--allow-unsafe-live-data",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="(위험) 과거 날짜에도 라이브 수집값으로 snapshot 백필 강행 허용 (기본: false)",
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


def _build_snapshot_from_db(conn: sqlite3.Connection, target_date: date) -> Snapshot | None:
    """Build snapshot for one date from DB history; return None when core rows missing."""
    ds = target_date.isoformat()
    conn.row_factory = sqlite3.Row
    md = conn.execute(
        """
        SELECT date, kospi_pct, kosdaq_pct, sp500_pct, nasdaq_pct, dow_pct,
               kospi, kosdaq, sp500, nasdaq, dow,
               usdkrw, usdkrw_pct, vix
        FROM market_daily
        WHERE date = ?
        LIMIT 1
        """,
        (ds,),
    ).fetchone()
    mf = conn.execute(
        """
        SELECT date, foreign_net, institution_net, retail_net
        FROM market_flow_daily
        WHERE date = ?
        LIMIT 1
        """,
        (ds,),
    ).fetchone()
    dm = conn.execute(
        """
        SELECT date, us10y, us2y, spread_2_10, vix, dxy, usdkrw,
               vix3m, vix_term_spread, oil_wti,
               fed_funds_rate, real_rate, hy_oas, ig_oas, fed_balance_sheet
        FROM daily_macro
        WHERE date = ?
        LIMIT 1
        """,
        (ds,),
    ).fetchone()
    if md is None or mf is None or dm is None:
        return None

    mm = conn.execute(
        """
        SELECT date, unemployment_rate, cpi_yoy, core_cpi_yoy, pce_yoy, pmi,
               retail_sales_mom, nfp_change, wage_level, wage_yoy, export_yoy
        FROM monthly_macro
        WHERE date <= ?
        ORDER BY date DESC
        LIMIT 1
        """,
        (ds,),
    ).fetchone()
    qm = conn.execute(
        """
        SELECT date, real_gdp, gdp_qoq_annualized
        FROM quarterly_macro
        WHERE date <= ?
        ORDER BY date DESC
        LIMIT 1
        """,
        (ds,),
    ).fetchone()

    snapshot_payload = {
        "market_summary": {
            "note": f"KOSPI {float(md['kospi_pct'] or 0.0):+.2f}%, USD/KRW {float(md['usdkrw'] or 0.0):.2f}. DB historical rebuild ({ds}).",
            "kospi_change_pct": float(md["kospi_pct"] or 0.0),
            "usdkrw": float(md["usdkrw"] or 0.0),
        },
        "flow_summary": {
            "note": (
                f"외국인 {float(mf['foreign_net'] or 0.0):+.0f}억, "
                f"기관 {float(mf['institution_net'] or 0.0):+.0f}억, "
                f"개인 {float(mf['retail_net'] or 0.0):+.0f}억 (DB historical rebuild)"
            )[:500],
            "foreign_net": float(mf["foreign_net"] or 0.0),
            "institution_net": float(mf["institution_net"] or 0.0),
            "retail_net": float(mf["retail_net"] or 0.0),
        },
        "korean_market_flow": None,
        "sector_moves": ["n/a", "n/a", "n/a"],
        "news_headlines": [f"historical_rebuild_from_db:{ds}"],
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


def _validate_snapshot_date_fields(*, market_date: date, snapshot_payload: dict) -> None:
    """Guardrail: block known mismatches when live data leaks into historical date."""
    target = market_date.isoformat()
    flow = snapshot_payload.get("korean_market_flow")
    if isinstance(flow, dict):
        flow_date = flow.get("date")
        if isinstance(flow_date, str) and flow_date and flow_date != target:
            raise RuntimeError(
                f"snapshot_date_mismatch[korean_market_flow.date={flow_date} != target={target}]"
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
                snapshot = None
                status: dict[str, str] = {}
                if d != date.today():
                    db_path = ROOT_DIR / "data" / "investment.db"
                    if db_path.exists():
                        with sqlite3.connect(str(db_path)) as conn:
                            snapshot = _build_snapshot_from_db(conn, d)
                if snapshot is None:
                    if d != date.today() and not args.allow_unsafe_live_data:
                        raise RuntimeError(
                            "exclude_ai_historical_not_supported_without_allow_unsafe_live_data: "
                            "과거 날짜는 라이브 수집값이 섞여 잘못 적재될 수 있습니다. "
                            "DB 기반 재구성 실패 시 강행하지 않습니다."
                        )
                    snapshot = build_snapshot(d)
                    status = get_last_snapshot_status() or {}
                    persist_snapshot_metrics(snapshot=snapshot, market_date=d, status=status)
                else:
                    status = {"rebuild_source": "db_history"}
                    print(f"[backfill] db historical rebuild used: {d.isoformat()}")
                _validate_snapshot_date_fields(
                    market_date=d,
                    snapshot_payload=snapshot.model_dump(),
                )
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
