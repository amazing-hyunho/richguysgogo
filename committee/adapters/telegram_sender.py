from __future__ import annotations

# Telegram sender adapter with console fallback.

import json
import os
import urllib.error
import urllib.request


def send_report(text: str) -> bool:
    """Send report text to Telegram or print to console.
    TELEGRAM_CHAT_ID can be a single id or comma-separated (e.g. 123,-456,789).
    """
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    raw = os.getenv("TELEGRAM_CHAT_ID", "").strip()
    chat_ids = [c.strip() for c in raw.split(",") if c.strip()]
    if not token or not chat_ids:
        print(text)
        return True

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    parts = _split_message(text, max_length=3500)
    if not parts:
        return True

    total = len(parts)
    success = True
    for index, part in enumerate(parts, start=1):
        if not part.strip():
            continue
        prefixed = f"({index}/{total}) {part}"
        for chat_id in chat_ids:
            ok = _send_message(url, chat_id, prefixed)
            if not ok:
                print(f"telegram_send_failed: chat_id={chat_id} part {index}/{total}")
                success = False
    return success


def _send_message(url: str, chat_id: str, text: str) -> bool:
    """Send a single Telegram message."""
    payload = json.dumps({"chat_id": chat_id, "text": text})
    data = payload.encode("utf-8")
    request = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=15) as response:  # noqa: S310 - controlled URL
            return 200 <= response.status < 300
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="ignore") if exc.fp else ""
        print(f"telegram_http_error: {exc.code} {body}".strip())
        return False
    except Exception as exc:
        print(f"telegram_send_exception: {exc}")
        return False


def _split_message(text: str, max_length: int) -> list[str]:
    """Split text into parts by lines without exceeding max length."""
    lines = text.splitlines()
    parts: list[str] = []
    current: list[str] = []
    current_len = 0

    for line in lines:
        separator = "\n" if current else ""
        additional = len(separator) + len(line)
        if current and current_len + additional > max_length:
            part = "\n".join(current)
            if part.strip():
                parts.append(part)
            current = [line]
            current_len = len(line)
            continue
        current.append(line)
        current_len += additional

    if current:
        part = "\n".join(current)
        if part.strip():
            parts.append(part)

    return parts
