from __future__ import annotations

"""Lightweight DART ingestion helpers (no pandas / no ORM)."""

from io import BytesIO
from typing import Any
import os
import xml.etree.ElementTree as ET
import zipfile

import requests

_DART_BASE_URL = "https://opendart.fss.or.kr/api"
_HEADERS = {
    "User-Agent": "DailyAIInvestmentCommittee/1.0",
}


def _get_api_key() -> str:
    key = os.getenv("DART_API_KEY", "").strip() or os.getenv("OPEN_DART_API_KEY", "").strip()
    if not key:
        raise ValueError("missing_dart_api_key: set DART_API_KEY or OPEN_DART_API_KEY")
    return key


def _clean_text(value: Any) -> str | None:
    if value is None:
        return None
    s = str(value).strip()
    return s or None


def _num_or_none(value: Any) -> float | None:
    if value is None:
        return None
    s = str(value).strip()
    if not s or s in {"-", "--", "N/A", "null", "None"}:
        return None
    s = s.replace(",", "")
    try:
        return float(s)
    except Exception:
        return None


def _request_dart_json(path: str, params: dict[str, Any], *, timeout: int = 20) -> dict[str, Any]:
    api_key = _get_api_key()
    response = requests.get(
        f"{_DART_BASE_URL}/{path}",
        params={"crtfc_key": api_key, **params},
        headers=_HEADERS,
        timeout=timeout,
    )
    response.raise_for_status()
    payload = response.json() or {}
    status = str(payload.get("status", "")).strip()
    if status not in {"000", "013"}:  # 013 = no data
        message = str(payload.get("message", "unknown_error"))
        raise ValueError(f"dart_api_error[{path}] status={status} message={message}")
    return payload


def fetch_dart_company_codes() -> list[dict[str, Any]]:
    """Fetch DART corp code list mapped to `dart_company_code` schema."""
    api_key = _get_api_key()
    response = requests.get(
        f"{_DART_BASE_URL}/corpCode.xml",
        params={"crtfc_key": api_key},
        headers=_HEADERS,
        timeout=30,
    )
    response.raise_for_status()

    with zipfile.ZipFile(BytesIO(response.content)) as archive:
        xml_names = [name for name in archive.namelist() if name.lower().endswith(".xml")]
        if not xml_names:
            return []
        with archive.open(xml_names[0]) as xml_file:
            xml_bytes = xml_file.read()

    root = ET.fromstring(xml_bytes)

    normalized: list[dict[str, Any]] = []
    for row in root.findall(".//list"):
        dart_corp_code = _clean_text(row.findtext("corp_code"))
        if not dart_corp_code:
            continue

        normalized.append(
            {
                "dart_corp_code": dart_corp_code,
                "company_name": _clean_text(row.findtext("corp_name")),
                "stock_code": _clean_text(row.findtext("stock_code")),
            }
        )

    return normalized


# DART 보고서 코드 (reprt_code) 매핑
DART_REPORT_CODES = {
    "annual": "11011",   # 사업보고서 (연간)
    "q3": "11014",       # 3분기 보고서
    "half": "11012",     # 반기 보고서 (2Q)
    "q1": "11013",       # 1분기 보고서
}
DART_PERIOD_LABELS = {
    "11011": "annual",
    "11014": "q3",
    "11012": "half",
    "11013": "q1",
}


def fetch_financials(
    dart_corp_code: str,
    year: int,
    report_type: str = "annual",
) -> list[dict[str, Any]]:
    """Fetch DART account-level financials for one company/year/period.

    Parameters
    ----------
    dart_corp_code : str
        DART 기업 고유번호
    year : int
        사업연도 (예: 2024)
    report_type : str
        'annual' | 'q1' | 'half' | 'q3'
        기본값 'annual' → 사업보고서(11011)
    """
    corp_code = str(dart_corp_code).strip()
    if not corp_code:
        raise ValueError("invalid_dart_corp_code")

    reprt_code = DART_REPORT_CODES.get(report_type, "11011")

    params = {
        "corp_code": corp_code,
        "bsns_year": str(int(year)),
        "reprt_code": reprt_code,
        "fs_div": "CFS",  # 연결 재무제표 우선
    }
    payload = _request_dart_json("fnlttSinglAcntAll.json", params=params)
    rows = payload.get("list") if isinstance(payload, dict) else None

    if not isinstance(rows, list) or not rows:
        # 연결 없으면 별도(OFS) 시도
        payload = _request_dart_json(
            "fnlttSinglAcntAll.json",
            params={**params, "fs_div": "OFS"},
        )
        rows = payload.get("list") if isinstance(payload, dict) else None

    if not isinstance(rows, list):
        return []

    period_label = DART_PERIOD_LABELS.get(reprt_code, "annual")
    normalized: list[dict[str, Any]] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        normalized.append(
            {
                "business_year": _clean_text(row.get("bsns_year")) or str(int(year)),
                "report_code": _clean_text(row.get("reprt_code")) or reprt_code,
                "period_type": period_label,
                "account_name": _clean_text(row.get("account_nm")),
                "amount": _num_or_none(row.get("thstrm_amount")),
            }
        )

    return normalized


def fetch_financials_all_periods(
    dart_corp_code: str,
    year: int,
    periods: list[str] | None = None,
) -> list[dict[str, Any]]:
    """Fetch financials for multiple periods in a single year.

    Parameters
    ----------
    periods : list of 'annual' | 'q1' | 'half' | 'q3'
        Defaults to all four periods.
    """
    if periods is None:
        periods = ["annual", "q3", "half", "q1"]

    all_rows: list[dict[str, Any]] = []
    for period in periods:
        try:
            rows = fetch_financials(dart_corp_code, year, report_type=period)
            all_rows.extend(rows)
        except ValueError as exc:
            # status 013 = no data for this period → skip silently
            if "013" in str(exc) or "no_data" in str(exc):
                continue
            raise
    return all_rows
