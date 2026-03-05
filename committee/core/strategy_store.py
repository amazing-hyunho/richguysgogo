from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
DEFAULT_DB_PATH = ROOT_DIR / "data" / "investment.db"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _ensure_table(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS strategy_history (
            version INTEGER PRIMARY KEY AUTOINCREMENT,
            strategy_json TEXT NOT NULL,
            source TEXT,
            created_at TEXT NOT NULL
        );
        """
    )


def load_latest_strategy(db_path: Path | None = None) -> tuple[int, dict[str, str]]:
    path = db_path or DEFAULT_DB_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(path) as conn:
        _ensure_table(conn)
        row = conn.execute(
            "SELECT version, strategy_json FROM strategy_history ORDER BY version DESC LIMIT 1"
        ).fetchone()
    if not row:
        return 0, {}
    version = int(row[0])
    try:
        strategy = json.loads(row[1]) if row[1] else {}
        if not isinstance(strategy, dict):
            return version, {}
        safe: dict[str, str] = {}
        for key, value in strategy.items():
            safe[str(key).upper()] = str(value)
        return version, safe
    except Exception:
        return version, {}


def update_strategy(changes: dict[str, str], source: str = "telegram", db_path: Path | None = None) -> tuple[int, dict[str, str]]:
    _, current = load_latest_strategy(db_path)
    next_strategy = dict(current)
    for key, value in changes.items():
        next_strategy[str(key).upper()] = str(value)

    path = db_path or DEFAULT_DB_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(path) as conn:
        _ensure_table(conn)
        cur = conn.execute(
            "INSERT INTO strategy_history(strategy_json, source, created_at) VALUES (?, ?, ?)",
            (json.dumps(next_strategy, ensure_ascii=False, sort_keys=True), source, _utc_now_iso()),
        )
        version = int(cur.lastrowid or 0)
        conn.commit()
    return version, next_strategy
