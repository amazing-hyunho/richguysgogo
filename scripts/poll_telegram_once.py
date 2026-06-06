from __future__ import annotations

"""Process Telegram bot commands.

Modes
-----
once (default)
    Process one batch of pending updates and exit.
loop
    Keep polling in the background for near-real-time replies.
    Offset is persisted in `data/telegram_poll_offset.json`.
"""

import argparse
import os
import sys
import time
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from committee.adapters.telegram_bot import TelegramQABot
from committee.core.env_loader import load_project_env
from committee.core.telegram_poll_state import clear_poller_pid, load_offset, save_offset


def _poll_batch(bot: TelegramQABot, offset: int | None, timeout_sec: int) -> int | None:
    next_offset = bot.poll_once(offset=offset, timeout_sec=timeout_sec)
    if next_offset is not None and next_offset != offset:
        save_offset(next_offset)
        print(f"[telegram_poll] processed updates, offset={next_offset}")
        return next_offset
    return offset


def main() -> None:
    parser = argparse.ArgumentParser(description="텔레그램 봇 명령 처리")
    parser.add_argument(
        "--loop",
        action="store_true",
        help="백그라운드 폴링 루프 (즉시 응답용, Ctrl+C로 종료)",
    )
    parser.add_argument(
        "--interval",
        type=float,
        default=1.0,
        help="loop 모드에서 배치 사이 대기 초 (기본 1초)",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=10,
        help="getUpdates long-poll timeout 초 (기본 10)",
    )
    args = parser.parse_args()

    load_project_env(ROOT_DIR)
    token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    raw_chat_ids = os.getenv("TELEGRAM_CHAT_ID", "").strip()
    allowed_chat_ids = {item.strip() for item in raw_chat_ids.split(",") if item.strip()}

    if not token:
        print("[telegram_poll] TELEGRAM_BOT_TOKEN missing, skip")
        return

    bot = TelegramQABot(token=token, allowed_chat_ids=allowed_chat_ids, timeout_sec=args.timeout)
    offset = load_offset()

    if not args.loop:
        _poll_batch(bot, offset=offset, timeout_sec=0)
        if offset == load_offset():
            print("[telegram_poll] no pending updates")
        return

    print(f"[telegram_poll] loop started pid={os.getpid()} timeout={args.timeout}s", flush=True)
    try:
        while True:
            try:
                offset = load_offset()
                _poll_batch(bot, offset=offset, timeout_sec=args.timeout)
            except Exception as exc:  # noqa: BLE001
                print(f"[telegram_poll] loop_error: {exc}", flush=True)
                time.sleep(2)
            if args.interval > 0:
                time.sleep(args.interval)
    except KeyboardInterrupt:
        print("[telegram_poll] loop stopped", flush=True)
    finally:
        clear_poller_pid()


if __name__ == "__main__":
    main()
