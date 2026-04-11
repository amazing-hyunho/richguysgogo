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
import json
from pathlib import Path
import re
import time

import requests


FRED_BASE = "https://api.stlouisfed.org/fred/series/observations"
_TRANSIENT_HTTP_STATUSES = frozenset({429, 500, 502, 503, 504})
_TRANSIENT_BACKOFF_SECS = (0.8, 1.6)
_WARNED_NO_KEY = False
_WARNED_BAD_KEY_FORMAT = False
_WARNED_MISSING_SERIES: set[str] = set()


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


def _cache_path() -> Path:
    configured = os.getenv("FRED_CACHE_PATH", "").strip()
    if configured:
        return Path(configured)
    return Path(__file__).resolve().parents[2] / "data" / "fred_last_good_cache.json"


def _load_cache() -> dict:
    path = _cache_path()
    try:
        if not path.exists():
            return {"series": {}}
        payload = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            return {"series": {}}
        series = payload.get("series")
        if not isinstance(series, dict):
            payload["series"] = {}
        return payload
    except Exception:
        return {"series": {}}


def _save_cache(payload: dict) -> None:
    path = _cache_path()
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, ensure_ascii=True), encoding="utf-8")
    except Exception:
        # Cache write failure must not break the pipeline.
        return


def _read_cached_values(series_id: str, n: int) -> list[float] | None:
    payload = _load_cache()
    series = payload.get("series")
    if not isinstance(series, dict):
        return None
    rec = series.get(series_id)
    if not isinstance(rec, dict):
        return None
    vals = rec.get("values")
    if not isinstance(vals, list):
        return None
    out: list[float] = []
    for v in vals:
        try:
            out.append(float(v))
        except Exception:
            continue
        if len(out) >= n:
            break
    return out if len(out) >= n else None


def _write_cached_values(series_id: str, values: list[float]) -> None:
    if not values:
        return
    payload = _load_cache()
    series = payload.get("series")
    if not isinstance(series, dict):
        series = {}
        payload["series"] = series
    series[series_id] = {
        "values": [float(v) for v in values[:240]],
        "updated_at": int(time.time()),
    }
    _save_cache(payload)


def fetch_fred_last_n_values(series_id: str, n: int) -> list[float] | None:
    """Fetch last N numeric values for a FRED series (descending, with cache fallback)."""
    if n < 1:
        return None
    api_key = _fred_key()
    if not api_key:
        _warn_no_key_once()
        cached = _read_cached_values(series_id, n)
        if cached:
            print(f"fred_cache_fallback[{series_id}]: no_api_key")
            return cached
        return None
    try:
        resp = None
        for attempt in range(3):
            resp = requests.get(
                FRED_BASE,
                params={
                    "series_id": series_id,
                    "api_key": api_key,
                    "file_type": "json",
                    "sort_order": "desc",
                    "limit": max(int(n) * 2, 24),
                },
                timeout=10,
            )
            if resp.status_code == 200:
                break
            if resp.status_code in _TRANSIENT_HTTP_STATUSES and attempt < 2:
                time.sleep(_TRANSIENT_BACKOFF_SECS[attempt])
                continue
            msg = ""
            try:
                payload_err = resp.json()
                msg = str(payload_err.get("error_message") or "").strip()
            except Exception:
                msg = (resp.text or "").strip()
            cached = _read_cached_values(series_id, n)
            if cached:
                print(f"fred_cache_fallback[{series_id}]: http_{resp.status_code}")
                return cached
            if msg:
                if "series does not exist" in msg.lower():
                    if series_id not in _WARNED_MISSING_SERIES:
                        _WARNED_MISSING_SERIES.add(series_id)
                        print(f"fred_http_error[{series_id}]: {resp.status_code} {msg}")
                else:
                    print(f"fred_http_error[{series_id}]: {resp.status_code} {msg}")
            else:
                print(f"fred_http_error[{series_id}]: {resp.status_code}")
            return None
        if resp is None or resp.status_code != 200:
            cached = _read_cached_values(series_id, n)
            if cached:
                print(f"fred_cache_fallback[{series_id}]: bad_response")
                return cached
            return None
        payload = resp.json()
        obs = payload.get("observations", [])
        values: list[float] = []
        for item in obs:
            raw = item.get("value")
            if raw in (None, ".", ""):
                continue
            try:
                values.append(float(raw))
            except Exception:
                continue
        if values:
            _write_cached_values(series_id, values)
        if len(values) >= n:
            return values[:n]
        cached = _read_cached_values(series_id, n)
        if cached:
            print(f"fred_cache_fallback[{series_id}]: insufficient_live_values")
            return cached
        return None
    except Exception as exc:  # noqa: BLE001
        cached = _read_cached_values(series_id, n)
        if cached:
            print(f"fred_cache_fallback[{series_id}]: exception")
            return cached
        print(f"fred_fetch_failed[{series_id}]: {exc}")
        return None


def fetch_fred_latest(series_id: str) -> float | None:
    """Fetch latest value for a FRED series (with cache fallback)."""
    values = fetch_fred_last_n_values(series_id, 1)
    if not values:
        return None
    return values[0]

