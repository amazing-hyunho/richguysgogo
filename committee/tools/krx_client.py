from __future__ import annotations

"""Lightweight KRX ingestion helpers (no pandas / no new frameworks)."""

from datetime import date as dt_date
from typing import Any

import requests

_KRX_JSON_URL = "https://data.krx.co.kr/comm/bldAttendant/getJsonData.cmd"
_HEADERS = {
    "User-Agent": "DailyAIInvestmentCommittee/1.0",
    "Referer": "https://data.krx.co.kr/",
}


def _to_ymd(trade_date: str) -> str:
    raw = str(trade_date).strip()
    if len(raw) == 10 and "-" in raw:
        return dt_date.fromisoformat(raw).strftime("%Y%m%d")
    if len(raw) == 8 and raw.isdigit():
        return raw
    raise ValueError(f"invalid_trade_date: {trade_date}")


def _num_or_none(value: Any) -> float | None:
    if value is None:
        return None
    s = str(value).strip()
    if not s or s in {"-", "--", "N/A"}:
        return None
    s = s.replace(",", "")
    try:
        return float(s)
    except Exception:
        return None


def _clean_text(value: Any) -> str | None:
    if value is None:
        return None
    s = str(value).strip()
    return s or None


def _first(row: dict[str, Any], keys: list[str]) -> Any:
    for k in keys:
        if k in row and row.get(k) not in (None, ""):
            return row.get(k)
    return None


def _request_krx_rows(*, bld: str, params: dict[str, Any], session: requests.Session) -> list[dict[str, Any]]:
    payload = {"bld": bld, "csvxls_isNo": "false", **params}
    resp = session.post(_KRX_JSON_URL, headers=_HEADERS, data=payload, timeout=15)
    resp.raise_for_status()
    body = resp.json() or {}

    for key in ("OutBlock_1", "output", "block1", "result"):
        block = body.get(key)
        if isinstance(block, list):
            return [r for r in block if isinstance(r, dict)]
    return []


def fetch_stock_master() -> list[dict[str, Any]]:
    """Fetch KRX listed stock master rows mapped to ticker_master schema."""
    session = requests.Session()
    markets = ("STK", "KSQ", "KNX")
    bld_candidates = (
        "dbms/MDC/STAT/standard/MDCSTAT01901",
        "dbms/MDC/STAT/standard/MDCSTAT00601",
    )

    normalized: list[dict[str, Any]] = []
    seen: set[str] = set()

    for market in markets:
        rows: list[dict[str, Any]] = []
        for bld in bld_candidates:
            try:
                rows = _request_krx_rows(
                    bld=bld,
                    params={"mktId": market, "share": "1", "money": "1"},
                    session=session,
                )
                if rows:
                    break
            except requests.RequestException as exc:
                print(f"krx_stock_master_http_error[{market}][{bld}]: {exc}")
            except Exception as exc:  # noqa: BLE001
                print(f"krx_stock_master_parse_error[{market}][{bld}]: {exc}")

        if not rows:
            print(f"krx_stock_master_empty[{market}]")
            continue

        for row in rows:
            ticker_raw = _first(row, ["ISU_SRT_CD", "종목코드", "short_code", "isu_cd"])
            ticker = (_clean_text(ticker_raw) or "").upper()
            if not ticker:
                continue
            if ticker in seen:
                continue
            seen.add(ticker)

            normalized.append(
                {
                    "ticker": ticker,
                    "company_name": _clean_text(_first(row, ["ISU_ABBRV", "종목명", "한글 종목약명", "corp_name"])),
                    "market": _clean_text(_first(row, ["MKT_NM", "시장구분", "market", "mkt_nm"])) or market,
                    "isin": _clean_text(_first(row, ["ISU_CD", "표준코드", "isin"])),
                    "dart_corp_code": None,
                }
            )

    return normalized


def fetch_daily_prices(trade_date: str) -> list[dict[str, Any]]:
    """Fetch KRX OHLCV rows mapped to daily_price_kr schema."""
    ymd = _to_ymd(trade_date)
    iso_date = f"{ymd[:4]}-{ymd[4:6]}-{ymd[6:8]}"

    session = requests.Session()
    markets = ("STK", "KSQ", "KNX")
    bld_candidates = (
        "dbms/MDC/STAT/standard/MDCSTAT01501",
        "dbms/MDC/STAT/standard/MDCSTAT03901",
    )

    normalized: list[dict[str, Any]] = []
    seen: set[str] = set()

    for market in markets:
        rows: list[dict[str, Any]] = []
        for bld in bld_candidates:
            try:
                rows = _request_krx_rows(
                    bld=bld,
                    params={"mktId": market, "trdDd": ymd, "share": "1", "money": "1"},
                    session=session,
                )
                if rows:
                    break
            except requests.RequestException as exc:
                print(f"krx_daily_price_http_error[{ymd}][{market}][{bld}]: {exc}")
            except Exception as exc:  # noqa: BLE001
                print(f"krx_daily_price_parse_error[{ymd}][{market}][{bld}]: {exc}")

        if not rows:
            print(f"krx_daily_price_empty[{ymd}][{market}]")
            continue

        for row in rows:
            ticker_raw = _first(row, ["ISU_SRT_CD", "종목코드", "short_code", "isu_cd"])
            ticker = (_clean_text(ticker_raw) or "").upper()
            if not ticker:
                continue
            unique_key = f"{ticker}:{iso_date}"
            if unique_key in seen:
                continue
            seen.add(unique_key)

            record = {
                "ticker": ticker,
                "trade_date": iso_date,
                "open_price": _num_or_none(_first(row, ["TDD_OPNPRC", "시가", "open", "open_price"])),
                "high_price": _num_or_none(_first(row, ["TDD_HGPRC", "고가", "high", "high_price"])),
                "low_price": _num_or_none(_first(row, ["TDD_LWPRC", "저가", "low", "low_price"])),
                "close_price": _num_or_none(_first(row, ["TDD_CLSPRC", "종가", "close", "close_price"])),
                "volume": _num_or_none(_first(row, ["ACC_TRDVOL", "거래량", "volume"])),
            }
            if record["close_price"] is None:
                continue
            normalized.append(record)

    return normalized
