from __future__ import annotations

"""Shared watchlist manager for the AI stock-analysis feature.

The watchlist lives in ``config/ai_stock_watchlist.json`` and drives which
tickers get news collected and (later) LLM-analyzed. This module is the single
source of truth for reading/adding/removing stocks so the Telegram bot, the CLI
sync script, and the dashboard builder all stay consistent.
"""

import json
import re
from pathlib import Path
from typing import Optional

from committee.core.database import connect, init_db

ROOT_DIR = Path(__file__).resolve().parents[2]
WATCHLIST_PATH = ROOT_DIR / "config" / "ai_stock_watchlist.json"

_DEFAULT_COMMENT = (
    "AI 종목분석 대상 워치리스트. ticker=종목코드(KR 6자리/US 심볼), "
    "name=뉴스 검색용 회사명, market=KR|US. 텔레그램 /stock add 또는 "
    "`python scripts/sync_stock_news.py`로 갱신됩니다."
)


def _normalize_ticker(ticker: str) -> str:
    return (ticker or "").strip().upper()


def detect_market(ticker: str) -> str:
    """Infer market from ticker shape: 6-digit numeric → KR, otherwise US."""
    t = _normalize_ticker(ticker)
    if re.fullmatch(r"\d{6}", t):
        return "KR"
    return "US"


def resolve_company_name(ticker: str, market: str) -> str:
    """Best-effort company name lookup from ticker_master; fallback to ticker."""
    t = _normalize_ticker(ticker)
    try:
        init_db()
        with connect() as conn:
            row = conn.execute(
                "SELECT company_name FROM ticker_master WHERE ticker = :t LIMIT 1;",
                {"t": t},
            ).fetchone()
            if row and row["company_name"]:
                return str(row["company_name"])
    except Exception:
        pass
    return t


def _read_payload() -> dict:
    if not WATCHLIST_PATH.exists():
        return {"_comment": _DEFAULT_COMMENT, "stocks": []}
    try:
        payload = json.loads(WATCHLIST_PATH.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            return {"_comment": _DEFAULT_COMMENT, "stocks": []}
        payload.setdefault("stocks", [])
        return payload
    except Exception:
        return {"_comment": _DEFAULT_COMMENT, "stocks": []}


def _write_payload(payload: dict) -> None:
    WATCHLIST_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload.setdefault("_comment", _DEFAULT_COMMENT)
    WATCHLIST_PATH.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def get_stocks() -> list[dict[str, str]]:
    """Return the list of watchlist stocks (each: ticker/name/market)."""
    payload = _read_payload()
    stocks = payload.get("stocks", [])
    return [s for s in stocks if isinstance(s, dict) and s.get("ticker")]


def find_stock(ticker: str) -> Optional[dict[str, str]]:
    t = _normalize_ticker(ticker)
    for stock in get_stocks():
        if _normalize_ticker(str(stock.get("ticker", ""))) == t:
            return stock
    return None


def add_stock(
    ticker: str,
    name: str | None = None,
    market: str | None = None,
) -> tuple[bool, dict[str, str], str]:
    """Add a stock to the watchlist.

    Returns ``(added, stock, message)``. ``added`` is False if it already exists.
    Market and name are auto-resolved when not provided.
    """
    t = _normalize_ticker(ticker)
    if not t:
        return False, {}, "티커가 비어 있습니다."

    existing = find_stock(t)
    if existing:
        return False, existing, f"{t}는 이미 워치리스트에 있습니다."

    mkt = (market or "").strip().upper() or detect_market(t)
    nm = (name or "").strip() or resolve_company_name(t, mkt)
    stock = {"ticker": t, "name": nm, "market": mkt}

    payload = _read_payload()
    payload.setdefault("stocks", []).append(stock)
    _write_payload(payload)
    return True, stock, f"{t} ({nm}/{mkt}) 등록 완료."


def remove_stock(ticker: str) -> tuple[bool, str]:
    """Remove a stock from the watchlist. Returns ``(removed, message)``."""
    t = _normalize_ticker(ticker)
    if not t:
        return False, "티커가 비어 있습니다."

    payload = _read_payload()
    stocks = payload.get("stocks", [])
    kept = [s for s in stocks if _normalize_ticker(str(s.get("ticker", ""))) != t]
    if len(kept) == len(stocks):
        return False, f"{t}는 워치리스트에 없습니다."
    payload["stocks"] = kept
    _write_payload(payload)
    return True, f"{t} 등록 해제 완료."
