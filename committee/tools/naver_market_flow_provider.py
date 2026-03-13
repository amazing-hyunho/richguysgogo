from __future__ import annotations

"""
Naver market flow provider (HTML crawl, no pandas dependency)
-------------------------------------------------------------
Fetch investor net buying (순매수, 억원) for:
- KOSPI (sosok=01)
- KOSDAQ (sosok=02)

Data source:
- https://finance.naver.com/sise/investorDealTrendDay.naver
"""

from datetime import date, timedelta
import re
from typing import Any, Dict

import requests


def get_korean_market_flow_naver(asof: date | None = None) -> Dict[str, Any]:
    """Best-effort Naver flow fetch with weekend/holiday backoff."""
    d = asof or date.today()
    last_error: str | None = None
    for _ in range(10):
        ymd = d.strftime("%Y%m%d")
        try:
            kospi = _fetch_market_flow_eok(ymd=ymd, sosok="01")
            kosdaq = _fetch_market_flow_eok(ymd=ymd, sosok="02")
            return {
                "date": f"{ymd[0:4]}-{ymd[4:6]}-{ymd[6:8]}",
                "market": {"KOSPI": kospi, "KOSDAQ": kosdaq},
            }
        except Exception as exc:
            last_error = f"{ymd}: {exc}"
            d = d - timedelta(days=1)
    raise RuntimeError(f"naver_flow_unavailable: {last_error or 'unknown'}")


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
    fallback_cells: list[str] | None = None
    for tr in tr_blocks:
        cells = re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", tr, flags=re.IGNORECASE | re.DOTALL)
        cleaned = [_clean_html_text(c) for c in cells]
        if len(cleaned) < 4:
            continue
        row_ymd = _normalize_ymd(cleaned[0])
        if not row_ymd:
            continue
        if fallback_cells is None:
            fallback_cells = cleaned
        if row_ymd == ymd:
            target_cells = cleaned
            break

    if not target_cells:
        if fallback_cells is not None:
            target_cells = fallback_cells
        else:
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
        return 0

    sign = -1 if s.startswith("-") else 1
    digits = re.sub(r"[^0-9]", "", s)
    if not digits:
        return 0
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
