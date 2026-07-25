from __future__ import annotations

"""Phase 4 repository for `industry_alert_dispatch_log` (Telegram dedup).

The single source of truth for "has this exact alert already been sent" is
the DB row, not in-memory state -- so dedup survives process restarts and
works correctly even if the weekly/urgent CLI is re-run by mistake (design
doc section 13: "텔레그램 중복 알림 방지").
"""

from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from committee.core.database import connect, init_db

WEEKLY_DIGEST_KEY = "__WEEKLY__"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def has_been_dispatched(
    industry_id: str, as_of: str, model_version: str, alert_type: str, db_path: Path | None = None
) -> bool:
    init_db(db_path)
    with connect(db_path) as conn:
        row = conn.execute(
            """
            SELECT 1 FROM industry_alert_dispatch_log
            WHERE industry_id = :industry_id AND as_of = :as_of AND model_version = :model_version
              AND alert_type = :alert_type;
            """,
            {"industry_id": industry_id, "as_of": as_of, "model_version": model_version, "alert_type": alert_type},
        ).fetchone()
        return row is not None


def record_dispatched(
    industry_id: str, as_of: str, model_version: str, alert_type: str, db_path: Path | None = None
) -> bool:
    """Record that this exact alert was just dispatched.

    Returns `True` if this is a NEW record (i.e. this alert had not been
    sent before), `False` if the exact key already existed (caller should
    treat this as "already sent, do not send again"). Uses `INSERT OR
    IGNORE` against the table's UNIQUE constraint rather than a
    check-then-insert, so this is safe even under concurrent callers.
    """
    init_db(db_path)
    with connect(db_path) as conn:
        cur = conn.execute(
            """
            INSERT OR IGNORE INTO industry_alert_dispatch_log (
                industry_id, as_of, model_version, alert_type, dispatched_at
            ) VALUES (:industry_id, :as_of, :model_version, :alert_type, :dispatched_at);
            """,
            {
                "industry_id": industry_id,
                "as_of": as_of,
                "model_version": model_version,
                "alert_type": alert_type,
                "dispatched_at": _now_iso(),
            },
        )
        return cur.rowcount > 0
