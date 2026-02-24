from __future__ import annotations

"""Lightweight JSONL trace logging for pipeline/LLM execution."""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class TraceLogger:
    """Append-only JSONL logger for execution traces."""

    def __init__(self, path: str | Path | None):
        self.path = Path(path) if path else None

    def enabled(self) -> bool:
        return self.path is not None

    def log(self, event: str, payload: dict[str, Any]) -> None:
        """Write one trace event as JSON line."""
        if self.path is None:
            return
        self.path.parent.mkdir(parents=True, exist_ok=True)
        record = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "event": event,
            **payload,
        }
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
