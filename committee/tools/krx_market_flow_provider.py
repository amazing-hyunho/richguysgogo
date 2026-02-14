from __future__ import annotations

"""
KRX market flow provider (no PyKRX / no pandas / no numpy)
----------------------------------------------------------
Goal:
- Fetch Korean market investor net buying (순매수) for:
  - KOSPI (시장 전체)
  - KOSDAQ (시장 전체)
- Return values for 개인/외국인/기관합계 in "억원" (integer)

Why:
- PyKRX depends on pandas/numpy (numpy<2.0). On Python 3.13 this often forces
  a source build of numpy and fails without MSVC (common on Windows).
- This module avoids that by calling KRX Data (data.krx.co.kr) directly with
  lightweight HTTP requests and parsing JSON.

Important:
- KRX endpoints and payload keys are not officially stable APIs.
- Failure handling is done by raising exceptions; caller (HttpProvider) must
  catch and degrade gracefully so the nightly pipeline never breaks.
"""

from dataclasses import dataclass
from datetime import date, timedelta
from typing import Any, Dict, Iterable, Tuple
import re

import requests


EOK = 100_000_000  # 1억원 = 100,000,000 KRW

# Cache parsed page defaults to keep KRX calls fast.
_PAGE_DEFAULTS_CACHE: dict[str, dict[str, str]] = {}


@dataclass(frozen=True)
class KRXFlow:
    trading_date: str  # YYYY-MM-DD
    market: Dict[str, Dict[str, int]]  # {"KOSPI": {...}, "KOSDAQ": {...}}


def get_korean_market_flow_krx(asof: date | None = None) -> Dict[str, Any]:
    """
    Best-effort KRX flow fetcher with automatic holiday/weekend fallback.

    Output shape (stable for snapshot/report):
    {
        "date": "YYYY-MM-DD",
        "market": {
            "KOSPI": {"individual": int, "foreign": int, "institution": int},
            "KOSDAQ": {"individual": int, "foreign": int, "institution": int},
        }
    }
    """
    d = asof or date.today()
    # Try recent dates until KRX returns valid data (handles weekends/holidays).
    last_error: str | None = None
    for _ in range(10):
        ymd = d.strftime("%Y%m%d")
        try:
            # Reuse a session across calls for speed.
            session = requests.Session()
            kospi = _fetch_market_flow_eok(ymd, market_code="STK", session=session)  # KOSPI
            kosdaq = _fetch_market_flow_eok(ymd, market_code="KSQ", session=session)  # KOSDAQ
            return {"date": _ymd_to_iso(ymd), "market": {"KOSPI": kospi, "KOSDAQ": kosdaq}}
        except Exception as exc:
            last_error = f"{ymd}: {exc}"
            d = d - timedelta(days=1)
            continue
    raise RuntimeError(f"krx_flow_unavailable: {last_error or 'unknown'}")


def _fetch_market_flow_eok(trading_ymd: str, market_code: str, session: requests.Session) -> Dict[str, int]:
    """
    Fetch investor net buying amounts for one market on one trading day.

    market_code:
    - STK: KOSPI
    - KSQ: KOSDAQ
    """
    payload_candidates = _krx_payload_candidates(trading_ymd, market_code, session=session)
    last_error: str | None = None

    for bld, payload, referer in payload_candidates:
        try:
            data = _krx_get_json(session, bld=bld, payload=payload, referer=referer)
            inv_map = _extract_investor_net_krw(data)
            individual = _pick_first(inv_map, ["개인"])
            foreign = _pick_first(inv_map, ["외국인", "외국인합계"])
            institution = _pick_first(inv_map, ["기관합계", "기관"])
            return {
                "individual": _to_eok_int(individual),
                "foreign": _to_eok_int(foreign),
                "institution": _to_eok_int(institution),
            }
        except Exception as exc:
            last_error = f"{bld}: {exc}"
            continue

    # Use lowercase market code in error string to avoid ticker-guard false positives.
    raise RuntimeError(f"krx_fetch_failed[{market_code.lower()},{trading_ymd}]: {last_error or 'no_candidates'}")


def _krx_payload_candidates(
    trading_ymd: str, market_code: str, session: requests.Session
) -> Iterable[Tuple[str, Dict[str, str], str]]:
    """
    KRX pages can change their internal `bld` identifiers. We try a small set of
    known candidates used by common KRX investor-stat pages.

    Notes:
    - `getJsonData.cmd` expects form-encoded params including `bld`.
    - Most pages accept `trdDd` (YYYYMMDD), `mktId` (STK/KSQ), and unit toggles.
    """
    candidate_pages = [
        "https://data.krx.co.kr/contents/MDC/STAT/standard/MDCSTAT02301.jspx",
        "https://data.krx.co.kr/contents/MDC/STAT/standard/MDCSTAT02201.jspx",
        "https://data.krx.co.kr/contents/MDC/STAT/standard/MDCSTAT02401.jspx",
    ]

    # 1) Discover bld(s) from HTML (best resilience).
    discovered: list[tuple[str, str]] = []
    # 1) Static fallbacks first (fast path).
    static_blds_with_pages = [
        ("dbms/MDC/STAT/standard/MDCSTAT02301", candidate_pages[0]),
        ("dbms/MDC/STAT/standard/MDCSTAT02201", candidate_pages[1]),
        ("dbms/MDC/STAT/standard/MDCSTAT02401", candidate_pages[2]),
    ]
    for bld, page in static_blds_with_pages:
        defaults = _get_page_defaults(page, session=session)
        for payload in _payload_variants(trading_ymd, market_code, defaults):
            # NOTE: KRX can reject requests when Referer page doesn't match the bld.
            yield bld, payload, page

    # 2) Discover bld(s) from HTML only if needed (slower, but more resilient).
    for page in candidate_pages:
        try:
            for bld in _discover_blds_from_page(page, session=session):
                discovered.append((bld, page))
        except Exception:
            continue

    # Deduplicate while preserving order.
    seen: set[str] = set()
    for bld, page in discovered:
        if bld in seen:
            continue
        seen.add(bld)
        defaults = _get_page_defaults(page, session=session)
        for payload in _payload_variants(trading_ymd, market_code, defaults):
            yield bld, payload, page


def _payload_variants(trading_ymd: str, market_code: str, defaults: dict[str, str]) -> list[dict[str, str]]:
    """Return a few likely payload shapes for KRX JSON endpoints."""
    base = dict(defaults or {})
    base.setdefault("money", "1")
    base.setdefault("csvxls_isNo", "false")

    def _compact(p: dict[str, str]) -> dict[str, str]:
        return {k: str(v) for k, v in p.items() if v is not None and str(v).strip() != ""}

    # Variant A: single day with trdDd
    v1 = dict(base)
    v1["trdDd"] = trading_ymd
    v1["mktId"] = market_code

    # Variant B: date range with strtDd/endDd
    v2 = dict(base)
    v2["strtDd"] = trading_ymd
    v2["endDd"] = trading_ymd
    v2["mktId"] = market_code

    # Variant C: both (extra keys often ignored)
    v3 = dict(v2)
    v3["trdDd"] = trading_ymd

    return [_compact(v1), _compact(v2), _compact(v3)]

def _discover_blds_from_page(page_url: str, session: requests.Session) -> list[str]:
    """
    Try to extract one or more `bld` identifiers from a KRX page HTML.

    KRX pages typically embed AJAX params like:
      bld: 'dbms/MDC/STAT/standard/MDCSTAT02301'
    or JSON fragments like:
      "bld":"dbms/MDC/STAT/standard/MDCSTAT02301"
    """
    headers = {
        "User-Agent": "DailyAIInvestmentCommittee/1.0",
        "Referer": "https://data.krx.co.kr/",
    }
    resp = session.get(page_url, headers=headers, timeout=10)
    if resp.status_code != 200:
        raise RuntimeError(f"page_http_status_{resp.status_code}")
    html = resp.text or ""
    if not html:
        return []

    # Find all bld occurrences.
    patterns = [
        r"""["']bld["']\s*:\s*["']([^"']+)["']""",
        r"""["']bld["']\s*=\s*["']([^"']+)["']""",
        # fallback: any dbms/... token in the HTML
        r"""(dbms/[A-Za-z0-9_/]+)""",
    ]
    blds: list[str] = []
    for pat in patterns:
        for m in re.finditer(pat, html):
            # Some patterns have group(1), some match the full token as group(0).
            bld = (m.group(1) if m.groups() else m.group(0)) or ""
            bld = bld.strip()
            if bld.startswith("dbms/"):
                blds.append(bld)

    # If none found, the page is likely server-rendered without inline params.
    return blds


def _get_page_defaults(page_url: str, session: requests.Session) -> dict[str, str]:
    """Extract hidden/default form parameters from a KRX page HTML.

    KRX often requires additional parameters beyond trdDd/mktId. By merging
    default hidden inputs from the page, we reduce HTTP 400 rejections.
    """
    cached = _PAGE_DEFAULTS_CACHE.get(page_url)
    if cached is not None:
        return dict(cached)

    headers = {
        "User-Agent": "DailyAIInvestmentCommittee/1.0",
        "Referer": "https://data.krx.co.kr/",
    }
    try:
        resp = session.get(page_url, headers=headers, timeout=10)
    except Exception:
        _PAGE_DEFAULTS_CACHE[page_url] = {}
        return {}
    if resp.status_code != 200:
        _PAGE_DEFAULTS_CACHE[page_url] = {}
        return {}
    defaults = _extract_input_defaults(resp.text or "")
    _PAGE_DEFAULTS_CACHE[page_url] = dict(defaults)
    return dict(defaults)


def _extract_input_defaults(html: str) -> dict[str, str]:
    """Very lightweight extraction of <input name=... value=...> pairs."""
    out: dict[str, str] = {}
    for m in re.finditer(r"""<input[^>]+name=["']([^"']+)["'][^>]*>""", html, flags=re.IGNORECASE):
        tag = m.group(0)
        name = (m.group(1) or "").strip()
        if not name:
            continue
        vm = re.search(r"""value=["']([^"']*)["']""", tag, flags=re.IGNORECASE)
        value = (vm.group(1) if vm else "").strip()
        if value:
            out[name] = value
    return out


def _krx_get_json(session: requests.Session, bld: str, payload: Dict[str, str], referer: str) -> dict:
    url = "https://data.krx.co.kr/comm/bldAttendant/getJsonData.cmd"
    headers = {
        "User-Agent": "DailyAIInvestmentCommittee/1.0",
        "Origin": "https://data.krx.co.kr",
        "Referer": referer,
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    }
    data = {"bld": bld, **payload}
    resp = session.post(url, data=data, headers=headers, timeout=10)
    if resp.status_code != 200:
        raise RuntimeError(f"http_status_{resp.status_code}")
    try:
        js = resp.json()
    except Exception as exc:
        raise RuntimeError(f"json_parse_error: {exc}") from exc
    if not isinstance(js, dict) or not js:
        raise RuntimeError("empty_json")
    return js


def _extract_investor_net_krw(js: dict) -> Dict[str, int]:
    """
    Convert KRX JSON payload into investor -> net_krw mapping.

    We support multiple possible key names because KRX output keys can change.
    """
    rows = _pick_first_existing_list(js, ["output", "output1", "OutBlock_1", "block1", "result"])
    if not rows:
        raise RuntimeError("no_output_rows")

    out: Dict[str, int] = {}
    for row in rows:
        if not isinstance(row, dict):
            continue
        investor = _pick_first_existing_str(row, ["INVST_TP_NM", "invstTpNm", "투자자구분", "투자자구분명", "투자자", "INVESTOR"])
        net = _pick_first_existing_str(row, ["NET_TRDVOL", "NET_TRDVAL", "netTrdVal", "순매수", "순매수거래대금", "순매수대금", "NET"])
        if not investor or net is None:
            continue
        out[investor] = _parse_int_loose(net)

    if not out:
        # Sometimes the table is returned as a single row with many columns.
        # Try to interpret the first row as wide-format: {개인: ..., 외국인: ..., 기관합계: ...}
        first = rows[0] if isinstance(rows[0], dict) else None
        if first:
            for inv_key in ["개인", "외국인", "기관합계", "기관"]:
                if inv_key in first:
                    out[inv_key] = _parse_int_loose(first[inv_key])

    if not out:
        raise RuntimeError(f"unrecognized_output_keys: sample={list(rows[0].keys()) if isinstance(rows[0], dict) else type(rows[0])}")
    return out


def _pick_first(values: Dict[str, int], keys: list[str]) -> int:
    for k in keys:
        if k in values:
            return int(values[k])
    raise KeyError(f"missing_keys: tried={keys}, available={list(values.keys())[:30]}")


def _pick_first_existing_list(js: dict, keys: list[str]) -> list:
    for k in keys:
        v = js.get(k)
        if isinstance(v, list):
            return v
    return []


def _pick_first_existing_str(row: dict, keys: list[str]) -> str | None:
    for k in keys:
        if k in row and row[k] is not None:
            return str(row[k]).strip()
    return None


def _parse_int_loose(v: Any) -> int:
    """
    Parse ints from typical KRX strings:
    - may contain commas
    - may be empty
    - may be already numeric
    """
    if v is None:
        raise ValueError("value_is_none")
    if isinstance(v, (int, float)):
        return int(v)
    s = str(v).strip()
    if not s:
        raise ValueError("value_is_empty")
    s = s.replace(",", "")
    # Some KRX values can include trailing decimals ".0"
    try:
        return int(float(s))
    except Exception as exc:
        raise ValueError(f"value_not_numeric[{s}]") from exc


def _to_eok_int(krw_value: int) -> int:
    return int(round(float(krw_value) / EOK))


def _ymd_to_iso(ymd: str) -> str:
    if len(ymd) != 8:
        return ymd
    return f"{ymd[0:4]}-{ymd[4:6]}-{ymd[6:8]}"


if __name__ == "__main__":
    # Manual test:
    #   python -m committee.tools.krx_market_flow_provider
    try:
        print(get_korean_market_flow_krx())
    except Exception as e:
        print(f"ERROR: {e}")
