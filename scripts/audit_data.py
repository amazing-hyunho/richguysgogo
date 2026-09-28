"""Read-only database inventory and dashboard metric coverage audit."""
from __future__ import annotations

from contextlib import closing
import argparse
from datetime import date
import json
from pathlib import Path
import sqlite3

ROOT = Path(__file__).resolve().parents[1]
METRIC_TABLES = ('market_daily', 'daily_macro', 'monthly_macro', 'quarterly_macro',
                 'market_flow_daily', 'domestic_policy_rate_daily')


def quote(name: str) -> str:
    return '"' + name.replace('"', '""') + '"'


def audit_database(db_path: Path, as_of: date | None = None) -> dict:
    as_of = as_of or date.today()
    with closing(sqlite3.connect(db_path.resolve().as_uri() + '?mode=ro', uri=True)) as conn:
        integrity = [r[0] for r in conn.execute('PRAGMA quick_check')]
        tables, metrics = [], []
        for (table,) in conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"):
            columns = conn.execute(f'PRAGMA table_info({quote(table)})').fetchall()
            count = conn.execute(f'SELECT COUNT(*) FROM {quote(table)}').fetchone()[0]
            dates = {}
            for _, column, *_ in columns:
                if column in ('date', 'trade_date', 'as_of', 'as_of_date', 'updated_at', 'created_at'):
                    dates[column] = conn.execute(f'SELECT MIN({quote(column)}), MAX({quote(column)}) FROM {quote(table)}').fetchone()
            tables.append({'table': table, 'rows': count, 'dates': dates})
            if table not in METRIC_TABLES:
                continue
            for _, column, dtype, *_ in columns:
                if dtype.upper() not in ('REAL', 'FLOAT', 'NUMERIC', 'DOUBLE'):
                    continue
                q = quote(column)
                latest = conn.execute(f'SELECT date, {q} FROM {quote(table)} WHERE date <= ? AND {q} IS NOT NULL ORDER BY date DESC LIMIT 1', (as_of.isoformat(),)).fetchone()
                tail = conn.execute(f'SELECT {q} FROM {quote(table)} WHERE date <= ? ORDER BY date DESC LIMIT 30', (as_of.isoformat(),)).fetchall()
                age = (as_of - date.fromisoformat(latest[0])).days if latest else None
                metrics.append({'table': table, 'metric': column, 'value': latest[1] if latest else None,
                                'last_recorded_date': latest[0] if latest else None,
                                'age_days': age, 'recent_rows': len(tail),
                                'recent_nulls': sum(r[0] is None for r in tail),
                                'status': 'missing' if latest is None else ('stale' if age > 7 else 'available')})
        return {'as_of': as_of.isoformat(), 'integrity': integrity, 'tables': tables, 'metrics': metrics,
                'note': 'Dates are database record dates, not verified source publication dates. Null rows may include market holidays. Empty optional tables are not automatically errors.'}


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--db', type=Path, default=ROOT / 'data/investment.db')
    p.add_argument('--output', type=Path, default=ROOT / 'reports/data_audit.json')
    args = p.parse_args()
    report = audit_database(args.db)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    counts = {s: sum(m['status'] == s for m in report['metrics']) for s in ('available', 'stale', 'missing')}
    print(json.dumps({'integrity': report['integrity'], 'tables': len(report['tables']), 'metrics': counts, 'output': str(args.output)}, ensure_ascii=False))


if __name__ == '__main__':
    main()
