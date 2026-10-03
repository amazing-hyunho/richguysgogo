from __future__ import annotations

"""
Naver market flow provider (JSON API, no pandas dependency)
-------------------------------------------------------------
Fetch investor net buying (순매수, 억원) for:
- KOSPI (sosok=01)
- KOSDAQ (sosok=02)

Data source:
- https://stock.naver.com/api/domestic/market/trend/daily
- Legacy HTML parser retained for regression checks only.
"""

from datetime import date, timedelta
import re
from typing import Any, Dict

import requests


FLOW_API = "https://stock.naver.com/api/domestic/market/trend/daily"
_INSTITUTIONS = ("1000", "2000", "3000", "3100", "4000", "5000", "6000", "7000")


def _parse_api_investors(row: dict) -> Dict[str, int]:
    from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
    values = {}
    for item in row.get("netAmounts", []):
        code = str(item.get("investorGubun", ""))
        if code in values:
            raise ValueError("duplicate_investor_code")
        try:
            value = Decimal(str(item.get("diffValue")))
        except InvalidOperation as exc:
            raise ValueError("invalid_flow_value") from exc
        if not value.is_finite():
            raise ValueError("nonfinite_flow_value")
        values[code] = value
    required = ("8000", "9000", "9001", *_INSTITUTIONS)
    if any(code not in values for code in required):
        raise ValueError("incomplete_market_flow")
    def eok(value):
        return int((value / Decimal(100_000_000)).quantize(Decimal(1), rounding=ROUND_HALF_UP))
    # Match the Naver KRX display: foreigners include 기타외국인 (9001).
    return {"individual": eok(values["8000"]),
            "foreign": eok(values["9000"] + values["9001"]),
            "institution": eok(sum(values[k] for k in _INSTITUTIONS))}


def fetch_korean_market_flow_history(asof: date, rows: int = 80) -> list[dict]:
    """Read dated KRX daily observations from Naver's current public JSON endpoint.

    Values are KRW in the API and integer 억원 in the existing snapshot contract.
    Both markets must cover the same dates; partial/malformed responses fail closed.
    """
    if not 1 <= rows <= 100:
        raise ValueError("rows must be between 1 and 100")
    markets = {}
    for market in ("KOSPI", "KOSDAQ"):
        response = requests.get(FLOW_API,
            params={"tradeType": "KRX", "marketType": market,
                    "bizdate": asof.strftime("%Y%m%d"), "startIdx": 0, "pageSize": rows},
            timeout=15, headers={"User-Agent": "Mozilla/5.0", "Referer": "https://stock.naver.com/market/stock/kr/trend/trader"})
        response.raise_for_status()
        payload = response.json()
        content = payload.get("content") if isinstance(payload, dict) else None
        if not isinstance(content, list) or not content:
            raise RuntimeError(f"empty_flow_history[{market}]")
        parsed = {}
        for row in content:
            raw = str(row.get("bizdate", ""))
            if not re.fullmatch(r"[0-9]{8}", raw):
                raise ValueError("invalid_flow_date")
            d = date(int(raw[:4]), int(raw[4:6]), int(raw[6:]))
            if d > asof or d.weekday() >= 5 or d.isoformat() in parsed:
                raise ValueError("unexpected_flow_date")
            parsed[d.isoformat()] = _parse_api_investors(row)
        markets[market] = parsed
    if set(markets["KOSPI"]) != set(markets["KOSDAQ"]):
        raise RuntimeError("market_flow_dates_mismatch")
    return [{"date": d, "market": {m: markets[m][d] for m in markets}}
            for d in sorted(markets["KOSPI"])]


def get_korean_market_flow_naver(asof: date | None = None) -> Dict[str, Any]:
    """Return the latest common observation, keeping its actual trading date."""
    target = asof or date.today()
    history = fetch_korean_market_flow_history(target, rows=10)
    latest = history[-1]
    if (target - date.fromisoformat(latest["date"])).days > 10:
        raise RuntimeError("stale_flow_history")
    return latest


def _fetch_market_flow_eok(ymd: str, sosok: str) -> Dict[str, int]:
    """Parse one market's investor net row from Naver daily trend table."""
    url = (
        "https://finance.naver.com/sise/investorDealTrendDay.naver"
        f"?bizdate={ymd}&sosok={sosok}&page=1"
    )
    response = requests.get(
        url,
        timeout=10,
        headers={"User-Agent": "Mozilla/5.0", "Referer": "https://finance.naver.com/"},
    )
    if response.status_code != 200:
        raise RuntimeError(f"http_status_{response.status_code}")

    html = response.text or ""
    if not html:
        raise RuntimeError("empty_html")

    tr_blocks = re.findall(r"<tr[^>]*>(.*?)</tr>", html, flags=re.IGNORECASE | re.DOTALL)
    if not tr_blocks:
        raise RuntimeError("no_rows")

    target_cells: list[str] | None = None
    for tr in tr_blocks:
        cells = re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", tr, flags=re.IGNORECASE | re.DOTALL)
        cleaned = [_clean_html_text(c) for c in cells]
        if len(cleaned) < 4:
            continue
        row_ymd = _normalize_ymd(cleaned[0])
        if not row_ymd:
            continue
        if row_ymd == ymd:
            target_cells = cleaned
            break

    if not target_cells:
        raise RuntimeError(f"row_not_found[{ymd}]")

    individual = _parse_eok_cell(target_cells[1])
    foreign = _parse_eok_cell(target_cells[2])
    institution = _parse_eok_cell(target_cells[3])
    return {
        "individual": individual,
        "foreign": foreign,
        "institution": institution,
    }


def _clean_html_text(raw: str) -> str:
    """Strip tags/entities and normalize numeric text."""
    text = re.sub(r"<[^>]+>", "", raw)
    text = (
        text.replace("&nbsp;", " ")
        .replace("&#160;", " ")
        .replace("&minus;", "-")
        .replace("−", "-")
    )
    return text.strip()


def _parse_eok_cell(raw: str) -> int:
    """Parse integer 억원 values like '+1,234' / '-56' / '0'."""
    s = (raw or "").strip()
    if not s:
        raise ValueError("missing_flow_value")

    sign = -1 if s.startswith("-") else 1
    digits = re.sub(r"[^0-9]", "", s)
    if not digits:
        raise ValueError("invalid_flow_value")
    return sign * int(digits)


def _normalize_ymd(raw: str) -> str:
    """Normalize date labels like 2026.03.13 / 2026-03-13 / 20260313."""
    s = (raw or "").strip()
    digits = re.sub(r"[^0-9]", "", s)
    if len(digits) >= 8:
        return digits[:8]
    if len(digits) == 6:
        # Naver often returns yy.mm.dd (e.g., 26.03.04).
        return f"20{digits}"
    return ""
