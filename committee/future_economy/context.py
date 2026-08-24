from __future__ import annotations

"""Read-only access to the latest verified future-economy committee agenda."""

from datetime import date
import json
from pathlib import Path
from typing import Any


def load_latest_committee_agenda(
    *,
    runs_dir: Path,
    as_of: date,
    max_age_days: int = 14,
) -> dict[str, Any]:
    candidates: list[tuple[date, Path, dict[str, Any]]] = []
    for path in runs_dir.glob("*/future_economy/committee_agenda.json"):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
            report_date = date.fromisoformat(str(payload.get("as_of") or ""))
        except (OSError, ValueError, json.JSONDecodeError, AttributeError):
            continue
        if report_date <= as_of and payload.get("schema_version") == "future-economy-committee-agenda-v1":
            candidates.append((report_date, path, payload))
    if not candidates:
        return {"as_of": None, "stale": False, "items": [], "reason": "agenda_not_available"}
    report_date, _, payload = max(candidates, key=lambda row: (row[0], str(row[1])))
    age_days = (as_of - report_date).days
    stale = age_days > max_age_days
    return {
        "as_of": report_date.isoformat(),
        "age_days": age_days,
        "stale": stale,
        "items": [] if stale else list(payload.get("items") or [])[:3],
        "reason": "agenda_too_old" if stale else "latest_verified_weekly_agenda",
    }
