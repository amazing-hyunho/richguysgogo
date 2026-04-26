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


def fetch_financials(dart_corp_code: str, year: int) -> list[dict[str, Any]]:
    """Fetch DART account-level financials for one company/year."""
    corp_code = str(dart_corp_code).strip()
    if not corp_code:
        raise ValueError("invalid_dart_corp_code")

    params = {
        "corp_code": corp_code,
        "bsns_year": str(int(year)),
        "reprt_code": "11011",  # annual report
        "fs_div": "CFS",  # consolidated first
    }
    payload = _request_dart_json("fnlttSinglAcntAll.json", params=params)
    rows = payload.get("list") if isinstance(payload, dict) else None

    if not isinstance(rows, list) or not rows:
        payload = _request_dart_json(
            "fnlttSinglAcntAll.json",
            params={**params, "fs_div": "OFS"},
        )
        rows = payload.get("list") if isinstance(payload, dict) else None

    if not isinstance(rows, list):
        return []

    normalized: list[dict[str, Any]] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        normalized.append(
            {
                "business_year": _clean_text(row.get("bsns_year")) or str(int(year)),
                "report_code": _clean_text(row.get("reprt_code")) or "11011",
                "account_name": _clean_text(row.get("account_nm")),
                "amount": _num_or_none(row.get("thstrm_amount")),
            }
        )

    return normalized
