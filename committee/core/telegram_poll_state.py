from __future__ import annotations

"""Persist Telegram getUpdates offset and background poller PID."""

import json
import os
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
OFFSET_PATH = ROOT_DIR / "data" / "telegram_poll_offset.json"
PID_PATH = ROOT_DIR / "data" / "telegram_poller.pid"


def load_offset() -> int | None:
    if not OFFSET_PATH.exists():
        return None
    try:
        payload = json.loads(OFFSET_PATH.read_text(encoding="utf-8"))
        if isinstance(payload, dict) and payload.get("offset") is not None:
            return int(payload["offset"])
    except Exception:
        return None
    return None


def save_offset(offset: int) -> None:
    OFFSET_PATH.parent.mkdir(parents=True, exist_ok=True)
    OFFSET_PATH.write_text(
        json.dumps({"offset": int(offset)}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def _pid_alive(pid: int) -> bool:
    if pid <= 0:
        return False
    if os.name == "nt":
        import ctypes

        PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
        handle = ctypes.windll.kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid)
        if handle:
            ctypes.windll.kernel32.CloseHandle(handle)
            return True
        return False
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def is_poller_running() -> bool:
    if not PID_PATH.exists():
        return False
    try:
        pid = int(PID_PATH.read_text(encoding="utf-8").strip())
        if _pid_alive(pid):
            return True
    except ValueError:
        pass
    try:
        PID_PATH.unlink(missing_ok=True)
    except Exception:
        pass
    return False


def write_poller_pid(pid: int) -> None:
    PID_PATH.parent.mkdir(parents=True, exist_ok=True)
    PID_PATH.write_text(str(int(pid)), encoding="utf-8")


def clear_poller_pid() -> None:
    try:
        PID_PATH.unlink(missing_ok=True)
    except Exception:
        pass
