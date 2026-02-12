from __future__ import annotations

# HTTP-based provider that attempts to fetch public data.

from typing import Dict, List, Tuple
import xml.etree.ElementTree as ET

import requests

from committee.tools.providers import IDataProvider


class HttpProvider(IDataProvider):
    """Best-effort public data provider with internal error handling."""

    def get_usdkrw(self) -> Tuple[float | None, str | None]:
        """Fetch USD/KRW using multiple public JSON endpoints."""
        sources = [
            ("er_api", "https://open.er-api.com/v6/latest/USD", ("rates", "KRW")),
            ("exchangerate_host", "https://api.exchangerate.host/latest?base=USD&symbols=KRW", ("rates", "KRW")),
            ("fawaz_api", "https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@1/latest/currencies/usd/krw.json", ("krw",)),
        ]

        last_reason = "unavailable"
        for name, url, path in sources:
            try:
                response = requests.get(url, timeout=7, headers=_default_headers())
                if response.status_code != 200:
                    last_reason = f"{name}:http_status_{response.status_code}"
                    continue
                try:
                    payload = response.json()
                except Exception:
                    last_reason = f"{name}:json_parse_error"
                    continue

                value = _extract_json_value(payload, path)
                if value is None:
                    last_reason = f"{name}:key_missing"
                    continue
                try:
                    return float(value), None
                except Exception:
                    last_reason = f"{name}:value_not_float"
                    continue
            except Exception as exc:
                last_reason = f"{name}:{exc}"
                continue

        return None, last_reason

    def get_kospi_change_pct(self) -> Tuple[float | None, str | None]:
        """Fetch KOSPI change percent using a public chart endpoint."""
        try:
            response = requests.get(
                "https://query1.finance.yahoo.com/v8/finance/chart/%5EKS11?interval=1d&range=2d",
                timeout=7,
                headers=_default_headers(),
            )
            if response.status_code != 200:
                return None, f"http_status_{response.status_code}"
            payload = response.json()
            result = payload.get("chart", {}).get("result", [])
            if not result:
                return None, "no_result"
            closes = result[0].get("indicators", {}).get("quote", [])[0].get("close", [])
            closes = [value for value in closes if value is not None]
            if len(closes) < 2:
                return None, "insufficient_closes"
            prev_close, latest_close = closes[-2], closes[-1]
            return ((latest_close - prev_close) / prev_close) * 100.0, None
        except Exception as exc:
            return None, str(exc)

    def get_flows(self) -> Tuple[Dict | None, str | None]:
        """Flow data not available without paid sources; return None."""
        return None, "unavailable"

    def get_headlines(self, limit: int) -> Tuple[List[str] | None, str | None]:
        """Fetch headlines from a public RSS feed."""
        try:
            response = requests.get(
                "https://news.google.com/rss/search?q=KOSPI",
                timeout=7,
                headers=_default_headers(),
            )
            if response.status_code != 200:
                return None, f"http_status_{response.status_code}"
            root = ET.fromstring(response.text)
            titles: List[str] = []
            for item in root.findall(".//item/title"):
                if item.text:
                    titles.append(item.text.strip())
            if not titles:
                return None, "no_titles"
            return titles[:limit], None
        except Exception as exc:
            return None, str(exc)


def _default_headers() -> dict:
    """Return common headers for HTTP requests."""
    return {"User-Agent": "DailyAIInvestmentCommittee/1.0"}


def _extract_json_value(payload: dict, path: tuple) -> float | None:
    """Extract nested value by path from JSON payload."""
    current = payload
    for key in path:
        if not isinstance(current, dict) or key not in current:
            return None
        current = current[key]
    return current
