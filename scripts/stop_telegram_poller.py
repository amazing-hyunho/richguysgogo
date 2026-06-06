from __future__ import annotations

"""Stop the background Telegram poller."""

import os
import signal
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from committee.core.telegram_poll_state import clear_poller_pid, is_poller_running, PID_PATH


def main() -> None:
    if not PID_PATH.exists():
        print("[stop_telegram_poller] no pid file")
        return
    try:
        pid = int(PID_PATH.read_text(encoding="utf-8").strip())
    except ValueError:
        clear_poller_pid()
        print("[stop_telegram_poller] invalid pid file removed")
        return

    if not is_poller_running():
        clear_poller_pid()
        print("[stop_telegram_poller] stale pid file removed")
        return

    try:
        if os.name == "nt":
            os.kill(pid, signal.SIGTERM)
        else:
            os.kill(pid, signal.SIGTERM)
        print(f"[stop_telegram_poller] stopped pid={pid}")
    except Exception as exc:  # noqa: BLE001
        print(f"[stop_telegram_poller] failed to stop pid={pid}: {exc}")
    finally:
        clear_poller_pid()


if __name__ == "__main__":
    main()
