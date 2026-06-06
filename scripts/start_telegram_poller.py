from __future__ import annotations

"""Start background Telegram command polling if not already running."""

import os
import subprocess
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from committee.core.env_loader import load_project_env
from committee.core.telegram_poll_state import (
    clear_poller_pid,
    is_poller_running,
    write_poller_pid,
)

POLL_SCRIPT = ROOT_DIR / "scripts" / "poll_telegram_once.py"
LOG_PATH = ROOT_DIR / "data" / "telegram_poller.log"


def main() -> None:
    load_project_env(ROOT_DIR)
    if is_poller_running():
        print("[start_telegram_poller] already running")
        return

    if not os.getenv("TELEGRAM_BOT_TOKEN", "").strip():
        print("[start_telegram_poller] TELEGRAM_BOT_TOKEN missing, skip")
        return

    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    log_file = open(LOG_PATH, "a", encoding="utf-8")
    log_file.write("\n[start_telegram_poller] launching background poller\n")
    log_file.flush()

    proc = subprocess.Popen(
        [sys.executable, "-u", str(POLL_SCRIPT), "--loop", "--timeout", "10", "--interval", "1"],
        cwd=str(ROOT_DIR),
        stdout=log_file,
        stderr=subprocess.STDOUT,
        close_fds=False,
    )
    write_poller_pid(proc.pid)
    print(f"[start_telegram_poller] started pid={proc.pid}")


if __name__ == "__main__":
    main()
