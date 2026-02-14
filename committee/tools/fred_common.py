from __future__ import annotations

"""
Common FRED helpers (best-effort, NULL-based).

Rules
-----
- Never crash the pipeline.
- On failure return None (caller stores NULL in DB).
- If FRED_API_KEY is missing, log once and return None.
"""

import os
import re

import requests


FRED_BASE = "https://api.stlouisfed.org/fred/series/observations"
_WARNED_NO_KEY = False
_WARNED_BAD_KEY_FORMAT = False


def _fred_key() -> str | None:
    raw = os.getenv("FRED_API_KEY")
    if not raw:
        return None
    key = raw.strip().strip('"').strip("'").strip()
    global _WARNED_BAD_KEY_FORMAT  # noqa: PLW0603
    if not _WARNED_BAD_KEY_FORMAT and not re.fullmatch(r"[a-z0-9]{32}", key):
        _WARNED_BAD_KEY_FORMAT = True
        print("fred_api_key_suspicious_format (expected 32 lowercase alnum)")
    return key


def _warn_no_key_once() -> None:
    global _WARNED_NO_KEY  # noqa: PLW0603
    if _WARNED_NO_KEY:
        return
    _WARNED_NO_KEY = True
    print("fred_api_key_missing")


def fetch_fred_latest(series_id: str) -> float | None:
    """Fetch latest value for a FRED series."""
    api_key = _fred_key()
    if not api_key:
        _warn_no_key_once()
        return None
    try:
        resp = requests.get(
            FRED_BASE,
            params={
                "series_id": series_id,
                "api_key": api_key,
                "file_type": "json",
                "sort_order": "desc",
                "limit": 1,
            },
            timeout=10,
        )
        if resp.status_code != 200:
            msg = ""
            try:
                payload = resp.json()
                msg = str(payload.get("error_message") or "").strip()
            except Exception:
                msg = (resp.text or "").strip()
            if msg:
                print(f"fred_http_error[{series_id}]: {resp.status_code} {msg}")
            else:
                print(f"fred_http_error[{series_id}]: {resp.status_code}")
            return None
        payload = resp.json()
        obs = payload.get("observations", [])
        if not obs:
            return None
        raw = obs[0].get("value")
        if raw in (None, ".", ""):
            return None
        return float(raw)
    except Exception as exc:  # noqa: BLE001
        print(f"fred_fetch_failed[{series_id}]: {exc}")
        return None

