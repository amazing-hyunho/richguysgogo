from __future__ import annotations

"""Lightweight KRX ingestion helpers (no pandas / no new frameworks)."""

from datetime import date as dt_date
from typing import Any

import requests

_KRX_JSON_URL = "https://data.krx.co.kr/comm/bldAttendant/getJsonData.cmd"
_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Referer": "https://data.krx.co.kr/contents/MDC/MDI/mdiLoader/index.cmd",
    "Origin": "https://data.krx.co.kr",
    "Content-Type": "application/x-www-form-urlencoded",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
    "X-Requested-With": "XMLHttpRequest",
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


_KRX_OTP_URL = "http://data.krx.co.kr/comm/fileDn/GenerateOTP/generate.cmd"
_KRX_CSV_URL = "http://data.krx.co.kr/comm/fileDn/download_csv.cmd"
_KRX_OTP_HEADERS = {
    "User-Agent": _HEADERS["User-Agent"],
    "Referer": "https://data.krx.co.kr/contents/MDC/MDI/mdiLoader/index.cmd",
}


def _fetch_krx_listing_csv(mkt_id: str) -> list[dict[str, Any]]:
    """KRX OTP 방식으로 상장종목 CSV 다운로드.

    data.krx.co.kr JSON API는 브라우저 쿠키 없으면 403이지만,
    OTP→CSV 다운로드 경로는 쿠키 없이도 동작한다.
    """
    import csv
    import io

    # 1단계: OTP 발급
    try:
        otp_resp = requests.post(
            _KRX_OTP_URL,
            headers=_KRX_OTP_HEADERS,
            data={
                "locale": "ko_KR",
                "mktId": mkt_id,
                "share": "1",
                "money": "1",
                "csvxls_isNo": "false",
                "name": "fileDown",
                "url": "dbms/MDC/STAT/standard/MDCSTAT01901",
            },
            timeout=15,
        )
        otp_resp.raise_for_status()
        otp = otp_resp.text.strip()
        if not otp:
            print(f"krx_otp_empty[{mkt_id}]")
            return []
    except Exception as exc:
        print(f"krx_otp_error[{mkt_id}]: {exc}")
        return []

    # 2단계: CSV 다운로드
    try:
        csv_resp = requests.post(
            _KRX_CSV_URL,
            headers=_KRX_OTP_HEADERS,
            data={"code": otp},
            timeout=30,
        )
        csv_resp.raise_for_status()
        # EUC-KR 또는 UTF-8-sig 인코딩 시도
        for enc in ("utf-8-sig", "euc-kr", "cp949"):
            try:
                text = csv_resp.content.decode(enc)
                break
            except UnicodeDecodeError:
                continue
        else:
            print(f"krx_csv_decode_error[{mkt_id}]")
            return []
    except Exception as exc:
        print(f"krx_csv_error[{mkt_id}]: {exc}")
        return []

    rows: list[dict[str, Any]] = []
    reader = csv.DictReader(io.StringIO(text))
    for row in reader:
        rows.append(dict(row))
    return rows


def fetch_stock_master() -> list[dict[str, Any]]:
    """KRX 전종목 마스터 수집 (OTP→CSV 방식, 쿠키 불필요)."""
    market_map = {
        "STK": "KOSPI",
        "KSQ": "KOSDAQ",
        "KNX": "KONEX",
    }
    normalized: list[dict[str, Any]] = []
    seen: set[str] = set()

    for mkt_id, market_name in market_map.items():
        rows = _fetch_krx_listing_csv(mkt_id)
        if not rows:
            print(f"krx_stock_master_empty[{mkt_id}]")
            continue

        count = 0
        for row in rows:
            ticker_raw = _first(row, ["단축코드", "ISU_SRT_CD", "종목코드", "Symbol"])
            ticker = (_clean_text(ticker_raw) or "").strip().zfill(6)
            if not ticker or ticker == "000000" or ticker in seen:
                continue
            seen.add(ticker)
            count += 1
            normalized.append(
                {
                    "ticker": ticker,
                    "company_name": _clean_text(
                        _first(row, ["한글 종목약명", "종목명", "ISU_ABBRV", "Name"])
                    ),
                    "market": market_name,
                    "isin": _clean_text(
                        _first(row, ["표준코드", "ISU_CD", "ISIN"])
                    ),
                    "dart_corp_code": None,
                }
            )
        print(f"krx_stock_master_ok[{mkt_id}={market_name}] count={count}")

    return normalized


def fetch_daily_prices(trade_date: str) -> list[dict[str, Any]]:
    """Fetch KRX OHLCV rows mapped to daily_price_kr schema."""
    ymd = _to_ymd(trade_date)
    iso_date = f"{ymd[:4]}-{ymd[4:6]}-{ymd[6:8]}"

    session = requests.Session()
    _init_krx_session(session)
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
