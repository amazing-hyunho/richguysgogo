from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from committee.adapters.telegram_bot import TelegramQABot
from committee.core.env_loader import load_project_env


def main() -> None:
    load_project_env(ROOT_DIR)
    parser = argparse.ArgumentParser(description="텔레그램 Q&A 봇 폴링 실행")
    parser.add_argument("--timeout", type=int, default=25, help="getUpdates long polling timeout(초)")
    args = parser.parse_args()

    token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    raw_chat_ids = os.getenv("TELEGRAM_CHAT_ID", "").strip()
    allowed_chat_ids = {item.strip() for item in raw_chat_ids.split(",") if item.strip()}

    if not token:
        print("TELEGRAM_BOT_TOKEN 이 없어 봇을 시작할 수 없습니다.")
        return

    bot = TelegramQABot(token=token, allowed_chat_ids=allowed_chat_ids, timeout_sec=args.timeout)
    bot.poll_forever()


if __name__ == "__main__":
    main()
