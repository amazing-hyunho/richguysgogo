from __future__ import annotations

"""One-shot historical backfill runner with validation.

Runs:
1) market_daily history
2) daily_macro base history
3) market_flow history (strict date match; NULL on miss)
4) macro indicator enrichment
5) runs rebuild from DB
6) dashboard build (optional)

Then validates DB/run coverage for the date range.
"""

import argparse
import json
import sqlite3
import subprocess
import sys
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
DB_PATH = ROOT_DIR / "data" / "investment.db"
RUNS_DIR = ROOT_DIR / "runs"


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run all historical backfills and validate results.")
    parser.add_argument("--start-date", required=True, help="Inclusive start date (YYYY-MM-DD).")
    parser.add_argument("--end-date", required=True, help="Inclusive end date (YYYY-MM-DD).")
    parser.add_argument(
        "--flow-source",
        choices=["AUTO", "KRX", "NAVER"],
        default="AUTO",
        help="Flow source for market_flow backfill.",
    )
    parser.add_argument("--skip-dashboard", action="store_true", help="Skip dashboard build.")
    parser.add_argument("--skip-macro-indicators", action="store_true", help="Skip macro enrichment script.")
    parser.add_argument("--verify-only", action="store_true", help="Only run validation (no backfill).")
    return parser.parse_args()


def _run(cmd: list[str]) -> None:
    print("RUN:", " ".join(cmd))
    result = subprocess.run(cmd, cwd=str(ROOT_DIR), capture_output=True, text=True)
    if result.stdout.strip():
        print(result.stdout.strip())
    if result.returncode != 0:
        err = result.stderr.strip() or "command_failed"
        raise RuntimeError(f"command_failed[{cmd[1] if len(cmd) > 1 else cmd[0]}]: {err}")


def _iter_dates(start_d: date, end_d: date) -> list[date]:
    out: list[date] = []
    cur = start_d
    while cur <= end_d:
        out.append(cur)
        cur += timedelta(days=1)
    return out


@dataclass(frozen=True)
class VerifySummary:
    total_days: int
    runs_found: int
    runs_missing: int
    market_non_null_days: int
    flow_non_null_days: int
    macro_non_null_days: int
    market_date_mismatch_files: int


def _verify(start_d: date, end_d: date) -> VerifySummary:
    days = _iter_dates(start_d, end_d)
    total = len(days)

    runs_found = 0
    runs_missing = 0
    market_non_null = 0
    flow_non_null = 0
    macro_non_null = 0
    mismatch = 0

    for d in days:
        ds = d.isoformat()
        path = RUNS_DIR / f"{ds}.json"
        if not path.exists():
            runs_missing += 1
            continue
        runs_found += 1
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            runs_missing += 1
            continue

        if str(payload.get("market_date", "")) != ds:
            mismatch += 1

        snap = payload.get("snapshot") or {}
        markets = snap.get("markets") or {}
        kr = markets.get("kr") or {}
        us = markets.get("us") or {}
        fx = markets.get("fx") or {}
        if (
            kr.get("kospi") is not None
            and kr.get("kosdaq") is not None
            and us.get("nasdaq") is not None
            and fx.get("usdkrw") is not None
        ):
            market_non_null += 1

        flow = snap.get("flow_summary") or {}
        if (
            flow.get("foreign_net") is not None
            and flow.get("institution_net") is not None
            and flow.get("retail_net") is not None
        ):
            flow_non_null += 1

        macro = snap.get("macro") or {}
        daily = macro.get("daily") if isinstance(macro, dict) else None
        if isinstance(daily, dict):
            keys = ["us10y", "us2y", "dxy", "usdkrw", "oil_wti"]
            if any(daily.get(k) is not None for k in keys):
                macro_non_null += 1

    return VerifySummary(
        total_days=total,
        runs_found=runs_found,
        runs_missing=runs_missing,
        market_non_null_days=market_non_null,
        flow_non_null_days=flow_non_null,
        macro_non_null_days=macro_non_null,
        market_date_mismatch_files=mismatch,
    )


def main() -> None:
    args = _parse_args()
    start_d = date.fromisoformat(str(args.start_date))
    end_d = date.fromisoformat(str(args.end_date))
    if end_d < start_d:
        raise ValueError("end-date must be >= start-date")

    if not args.verify_only:
        _run(
            [
                sys.executable,
                str(ROOT_DIR / "scripts" / "backfill_market_daily_history.py"),
                "--start-date",
                start_d.isoformat(),
                "--end-date",
                end_d.isoformat(),
            ]
        )
        _run(
            [
                sys.executable,
                str(ROOT_DIR / "scripts" / "backfill_daily_macro_history.py"),
                "--start-date",
                start_d.isoformat(),
                "--end-date",
                end_d.isoformat(),
            ]
        )
        _run(
            [
                sys.executable,
                str(ROOT_DIR / "scripts" / "backfill_market_flow_history.py"),
                "--start-date",
                start_d.isoformat(),
                "--end-date",
                end_d.isoformat(),
                "--source",
                str(args.flow_source),
            ]
        )
        if not args.skip_macro_indicators:
            _run([sys.executable, str(ROOT_DIR / "scripts" / "backfill_macro_indicators.py")])
        _run(
            [
                sys.executable,
                str(ROOT_DIR / "scripts" / "rebuild_runs_from_db.py"),
                "--start-date",
                start_d.isoformat(),
                "--end-date",
                end_d.isoformat(),
                "--no-purge-range",
            ]
        )
        if not args.skip_dashboard:
            _run([sys.executable, str(ROOT_DIR / "scripts" / "build_dashboard.py")])

    summary = _verify(start_d, end_d)
    report = {
        "range": f"{start_d.isoformat()}..{end_d.isoformat()}",
        "total_days": summary.total_days,
        "runs_found": summary.runs_found,
        "runs_missing": summary.runs_missing,
        "market_non_null_days": summary.market_non_null_days,
        "flow_non_null_days": summary.flow_non_null_days,
        "macro_non_null_days": summary.macro_non_null_days,
        "market_date_mismatch_files": summary.market_date_mismatch_files,
    }
    print("VERIFY_SUMMARY")
    print(json.dumps(report, ensure_ascii=False, indent=2))

    # Strict pass condition for market/date integrity; flow/macro are informational.
    if summary.runs_missing > 0 or summary.market_date_mismatch_files > 0:
        raise RuntimeError("verification_failed: runs missing or market_date mismatch")
    if summary.market_non_null_days < summary.total_days:
        raise RuntimeError("verification_failed: market fields missing on some days")


if __name__ == "__main__":
    main()
