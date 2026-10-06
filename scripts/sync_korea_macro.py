"""Collect official monthly histories, retain last good data, export for Pages."""
from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone
import json
import os
from pathlib import Path
import sqlite3
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from committee.core.env_loader import load_project_env
from committee.tools.korea_macro_provider import fetch_history, month_offset

KST = timezone(timedelta(hours=9))


def collect(conn, catalog, now, fetcher=fetch_history):
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS korea_macro_observation (
          indicator_id TEXT NOT NULL, period TEXT NOT NULL, value REAL NOT NULL,
          collected_at TEXT NOT NULL, PRIMARY KEY(indicator_id, period));
        CREATE TABLE IF NOT EXISTS korea_macro_collection (
          indicator_id TEXT PRIMARY KEY, attempted_at TEXT NOT NULL,
          succeeded_at TEXT, error TEXT);
    """)
    end = now.strftime("%Y%m")
    start = month_offset(end, -71)
    stamp = now.isoformat()
    failed = 0
    for spec in catalog:
        ident = spec["id"]
        try:
            history = fetcher(spec, start, end)
            if len(history) < 60:
                raise ValueError("history_too_short")
            prior = conn.execute("SELECT MAX(period) FROM korea_macro_observation WHERE indicator_id=?", (ident,)).fetchone()[0]
            if prior and history[-1]["period"] < prior:
                raise ValueError("source_regressed")
            with conn:
                conn.executemany("""INSERT INTO korea_macro_observation VALUES(?,?,?,?)
                    ON CONFLICT(indicator_id,period) DO UPDATE SET value=excluded.value,collected_at=excluded.collected_at""",
                    [(ident, r["period"], r["value"], stamp) for r in history])
                conn.execute("""INSERT INTO korea_macro_collection VALUES(?,?,?,NULL)
                    ON CONFLICT(indicator_id) DO UPDATE SET attempted_at=excluded.attempted_at,
                    succeeded_at=excluded.succeeded_at,error=NULL""", (ident, stamp, stamp))
            print(ident, "ok", len(history), history[-1]["period"])
        except Exception as exc:
            # Only fixed, credential-free reason codes may leave this collector.
            allowed = {"history_too_short", "source_regressed", "missing_api_key", "source_request_failed",
                       "empty_or_truncated_response", "series_identity_mismatch", "unit_changed",
                       "invalid_period", "invalid_or_duplicate_value", "history_gap"}
            reason = str(exc) if isinstance(exc, ValueError) and str(exc) in allowed else "collection_failed"
            with conn:
                conn.execute("""INSERT INTO korea_macro_collection VALUES(?,?,NULL,?)
                    ON CONFLICT(indicator_id) DO UPDATE SET attempted_at=excluded.attempted_at,error=excluded.error""",
                    (ident, stamp, reason))
            failed += 1
            print(ident, reason)
    result = {"generated_at": stamp, "source": "한국은행 ECOS", "source_url": "https://ecos.bok.or.kr/",
              "history_note": "현재 공개된 수정치 기준 이력입니다. 과거 시점에 알려졌던 값의 재현 자료가 아닙니다.", "indicators": []}
    for spec in catalog:
        rows = conn.execute("SELECT period,value FROM korea_macro_observation WHERE indicator_id=? AND period>=? ORDER BY period", (spec["id"], start)).fetchall()
        state = conn.execute("SELECT attempted_at,succeeded_at,error FROM korea_macro_collection WHERE indicator_id=?", (spec["id"],)).fetchone()
        history = [{"period": p, "value": v} for p, v in rows]
        result["indicators"].append({**spec, "history": history, "attempted_at": state[0], "succeeded_at": state[1], "error": state[2]})
    return result, failed


def atomic_json(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(dir=path.parent, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2, allow_nan=False)
            handle.write("\n")
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", type=Path, default=ROOT / "data/investment.db")
    parser.add_argument("--output", type=Path, default=ROOT / "runs/korea_macro/latest.json")
    args = parser.parse_args()
    load_project_env(ROOT)
    catalog = json.loads((ROOT / "config/korea_macro_indicators.json").read_text(encoding="utf-8"))
    with sqlite3.connect(args.db, timeout=30) as conn:
        payload, failed = collect(conn, catalog, datetime.now(KST))
    atomic_json(args.output, payload)
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
