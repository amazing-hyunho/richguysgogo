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
    "name=뉴스 검색용 회사명, market=KR|US, sector=선택 섹터. 텔레그램 /stock add 또는 "
    "`python scripts/sync_stock_news.py`로 갱신됩니다."
)


def _normalize_ticker(ticker: str) -> str:
    return (ticker or "").strip().upper()


def _looks_like_ticker(value: str) -> bool:
    t = _normalize_ticker(value)
    return bool(re.fullmatch(r"\d{6}", t) or re.fullmatch(r"[A-Z][A-Z0-9.\-]{0,11}", t))


def _normalize_market(market: str, ticker: str) -> str:
    m = (market or "").strip().upper()
    if m.startswith("KR"):
        return "KR"
    if m.startswith("US"):
        return "US"
    return detect_market(ticker)


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


def resolve_stock_meta(
    raw_ticker_or_name: str,
    name: str | None = None,
    market: str | None = None,
) -> dict[str, str]:
    """Resolve a user input into canonical ticker/name/market.

    If the first token is not shaped like a ticker (e.g. "하이닉스"), try
    ticker_master.company_name lookup and use the canonical ticker.
    """
    raw = (raw_ticker_or_name or "").strip()
    t = _normalize_ticker(raw)
    mkt = (market or "").strip().upper()
    nm = (name or "").strip()

    try:
        init_db()
        with connect() as conn:
            if _looks_like_ticker(t):
                row = conn.execute(
                    """
                    SELECT ticker, company_name, market
                    FROM ticker_master
                    WHERE ticker = :ticker
                    LIMIT 1;
                    """,
                    {"ticker": t},
                ).fetchone()
            else:
                row = conn.execute(
                    """
                    SELECT ticker, company_name, market
                    FROM ticker_master
                    WHERE company_name LIKE :keyword
                    ORDER BY
                        CASE
                            WHEN company_name = :exact THEN 0
                            WHEN company_name LIKE :prefix THEN 1
                            ELSE 2
                        END,
                        LENGTH(company_name)
                    LIMIT 1;
                    """,
                    {"keyword": f"%{raw}%", "exact": raw, "prefix": f"{raw}%"},
                ).fetchone()
            if row:
                canonical_ticker = str(row["ticker"]).strip().upper()
                return {
                    "ticker": canonical_ticker,
                    "name": nm or str(row["company_name"] or canonical_ticker),
                    "market": _normalize_market(mkt or str(row["market"] or ""), canonical_ticker),
                }
    except Exception:
        pass

    return {
        "ticker": t,
        "name": nm or resolve_company_name(t, mkt or detect_market(t)),
        "market": _normalize_market(mkt, t),
    }


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
    t = resolve_stock_meta(ticker).get("ticker") or _normalize_ticker(ticker)
    for stock in get_stocks():
        if _normalize_ticker(str(stock.get("ticker", ""))) == t:
            return stock
    return None


def add_stock(
    ticker: str,
    name: str | None = None,
    market: str | None = None,
    sector: str | None = None,
) -> tuple[bool, dict[str, str], str]:
    """Add a stock to the watchlist.

    Returns ``(added, stock, message)``. ``added`` is False if it already exists.
    Market and name are auto-resolved when not provided.
    """
    resolved = resolve_stock_meta(ticker, name=name, market=market)
    t = resolved["ticker"]
    if not t:
        return False, {}, "티커가 비어 있습니다."

    existing = find_stock(t)
    if existing:
        return False, existing, f"{t}는 이미 워치리스트에 있습니다."

    mkt = resolved["market"]
    nm = resolved["name"]
    stock = {"ticker": t, "name": nm, "market": mkt}
    sec = (sector or "").strip()
    if sec:
        stock["sector"] = sec

    payload = _read_payload()
    payload.setdefault("stocks", []).append(stock)
    _write_payload(payload)
    return True, stock, f"{t} ({nm}/{mkt}) 등록 완료."


def remove_stock(ticker: str) -> tuple[bool, str]:
    """Remove a stock from the watchlist. Returns ``(removed, message)``."""
    t = resolve_stock_meta(ticker).get("ticker") or _normalize_ticker(ticker)
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
