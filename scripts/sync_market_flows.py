"""Sync verified recent KRX investor flows and trading-observation rolling sums."""
from __future__ import annotations

import argparse
from contextlib import closing
from datetime import date, timedelta, datetime, UTC
import json
from pathlib import Path
import sqlite3
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from committee.core.database import init_db
from committee.tools.naver_market_flow_provider import fetch_korean_market_flow_history, FLOW_API


def save_history(history: list[dict], db_path: Path) -> int:
    if not history or len({r['date'] for r in history}) != len(history):
        raise ValueError('empty_or_duplicate_flow_history')
    ordered = sorted(history, key=lambda r: r['date'])
    totals = [sum(r['market'][m]['foreign'] for m in ('KOSPI', 'KOSDAQ')) for r in ordered]
    init_db(db_path)
    now = datetime.now(UTC).isoformat()
    with closing(sqlite3.connect(db_path)) as conn, conn:
        for i, row in enumerate(ordered):
            kr, kq = row['market']['KOSPI'], row['market']['KOSDAQ']
            conn.execute('''INSERT INTO market_flow_daily
                (date,foreign_net,institution_net,retail_net,kospi_foreign_net,
                 kospi_institution_net,kospi_retail_net,foreign_20d,foreign_60d,created_at)
                VALUES (?,?,?,?,?,?,?,?,?,?)
                ON CONFLICT(date) DO UPDATE SET
                  foreign_net=excluded.foreign_net,institution_net=excluded.institution_net,
                  retail_net=excluded.retail_net,kospi_foreign_net=excluded.kospi_foreign_net,
                  kospi_institution_net=excluded.kospi_institution_net,kospi_retail_net=excluded.kospi_retail_net,
                  foreign_20d=excluded.foreign_20d,foreign_60d=excluded.foreign_60d,
                  created_at=excluded.created_at''',
                (row['date'], totals[i], kr['institution']+kq['institution'],
                 kr['individual']+kq['individual'],kr['foreign'],kr['institution'],kr['individual'],
                 sum(totals[i-19:i+1]) if i >= 19 else None,
                 sum(totals[i-59:i+1]) if i >= 59 else None,now))
    return len(ordered)


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--as-of', type=date.fromisoformat, default=date.today()-timedelta(days=1),
                   help='Latest date to fetch; defaults to yesterday to exclude unfinished sessions.')
    p.add_argument('--rows', type=int, default=100)
    p.add_argument('--dry-run', action='store_true')
    args=p.parse_args()
    history=fetch_korean_market_flow_history(args.as_of, rows=args.rows)
    if (args.as_of-date.fromisoformat(history[-1]['date'])).days > 10:
        raise RuntimeError('stale_flow_history')
    if len(history) < min(args.rows,60):
        raise RuntimeError('insufficient_flow_history')
    if not args.dry_run:
        save_history(history, ROOT/'data/investment.db')
        output=ROOT/'runs/market_flow/latest.json'
        output.parent.mkdir(parents=True,exist_ok=True)
        payload={'source':FLOW_API,'trade_type':'KRX','foreign_definition':'9000 + 9001 (Naver display)',
                 'unit':'억원 (rounded per market)', 'collected_at':datetime.now(UTC).isoformat(),
                 'as_of':args.as_of.isoformat(),'history':history}
        temporary=output.with_suffix('.tmp')
        temporary.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf-8')
        temporary.replace(output)
    print(f"market_flows_synced rows={len(history)} first={history[0]['date']} last={history[-1]['date']} dry_run={args.dry_run}")


if __name__ == '__main__':
    main()
