from __future__ import annotations

# HTTP-based provider that attempts to fetch public data.
# Data sources: Yahoo Finance (indices), multi-source for USD/KRW.
# Failure handling: try/except around each fetch; on failure return (None, reason)
# so snapshot builder can use fallback 0.0 and record reason in status.

from datetime import date, timedelta
import json
import os
from pathlib import Path
from typing import Dict, List, Tuple
import requests

from committee.tools.news_digest import build_news_digest
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
            return _yahoo_daily_pct_chart("%5EKS11")
        except Exception as exc:
            return None, str(exc)

    # --- Global markets: KOSDAQ, US indices, USD/KRW pct (same fallback policy). ---
    # Data source: Yahoo Finance chart API (interval=1d, range=2d) for daily pct.
    # If fetch fails we return (None, reason); snapshot builder uses 0.0 and notes reason.

    def get_kosdaq_change_pct(self) -> Tuple[float | None, str | None]:
        """Fetch KOSDAQ daily change % from Yahoo Finance (^KQ11)."""
        try:
            return _yahoo_daily_pct_chart("%5EKQ11")
        except Exception as exc:
            return None, str(exc)

    def get_sp500_change_pct(self) -> Tuple[float | None, str | None]:
        """Fetch S&P 500 daily change % from Yahoo Finance (^GSPC)."""
        try:
            return _yahoo_daily_pct_chart("%5EGSPC")
        except Exception as exc:
            return None, str(exc)

    def get_nasdaq_change_pct(self) -> Tuple[float | None, str | None]:
        """Fetch NASDAQ daily change % from Yahoo Finance (^IXIC)."""
        try:
            return _yahoo_daily_pct_chart("%5EIXIC")
        except Exception as exc:
            return None, str(exc)

    def get_dow_change_pct(self) -> Tuple[float | None, str | None]:
        """Fetch DOW daily change % from Yahoo Finance (^DJI)."""
        try:
            return _yahoo_daily_pct_chart("%5EDJI")
        except Exception as exc:
            return None, str(exc)

    def get_usdkrw_pct(self) -> Tuple[float | None, str | None]:
        """USD/KRW daily percentage change: (today - yesterday) / yesterday * 100.
        Data source priority:
        1) Yahoo Finance FX chart (`KRW=X`) over recent 7d
        2) fawazahmed0 dated JSON path backtracking up to 7 days
        """
        try:
            try:
                yahoo_pct, _ = _yahoo_daily_pct_chart("KRW=X")
                return yahoo_pct, None
            except Exception:
                pass

            today_rate, _ = self.get_usdkrw()
            if today_rate is None:
                return None, "usdkrw_current_unavailable"
            prev_f = None
            last_reason = "usdkrw_prev_unavailable"
            for days_back in range(1, 8):
                day = (date.today() - timedelta(days=days_back)).isoformat()
                url = (
                    "https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@1/"
                    f"{day}/currencies/usd/krw.json"
                )
                resp = requests.get(url, timeout=7, headers=_default_headers())
                if resp.status_code != 200:
                    last_reason = f"usdkrw_prev_http_{resp.status_code}"
                    continue
                payload = resp.json()
                prev = _extract_json_value(payload, ("krw",))
                if prev is None:
                    last_reason = "usdkrw_prev_key_missing"
                    continue
                prev_f = float(prev)
                break
            if prev_f is None:
                return None, last_reason
            if prev_f <= 0:
                return None, "usdkrw_prev_invalid"
            return ((float(today_rate) - prev_f) / prev_f) * 100.0, None
        except Exception as exc:
            return None, str(exc)

    def get_flows(self) -> Tuple[Dict | None, str | None]:
        """Fetch Korean market flows (investor net buying).

        Architecture note:
        - This project supports swapping flow sources without changing the pipeline.
        - Default behavior is **disabled** (return unavailable) because KRX scraping endpoints
          are not stable and can slow down runs.
        - Enable a specific source via env:
            KOREAN_FLOW_SOURCE=KRX   -> use KRX (data.krx.co.kr) best-effort scraping
            KOREAN_FLOW_SOURCE=NONE  -> disabled (default)

        Returns:
        - On success: a dict with numeric totals in "억원" (consistent with report label),
          plus a structured breakdown under `korean_market_flow` for report rendering.
        - On failure: (None, reason) so snapshot builder can use fallback and record status.
        """
        try:
            source = os.getenv("KOREAN_FLOW_SOURCE", "NONE").strip().upper()
            if source in ("", "NONE", "OFF", "DISABLED"):
                return None, "unavailable"
            if source != "KRX":
                return None, f"unavailable(source={source})"

            from committee.tools.krx_market_flow_provider import get_korean_market_flow_krx

            flow = get_korean_market_flow_krx()
            markets = (flow or {}).get("market", {})
            kospi = markets.get("KOSPI", {})
            kosdaq = markets.get("KOSDAQ", {})

            # Totals across KOSPI + KOSDAQ (억원, 순매수)
            foreign_total = int(kospi.get("foreign", 0)) + int(kosdaq.get("foreign", 0))
            institution_total = int(kospi.get("institution", 0)) + int(kosdaq.get("institution", 0))
            retail_total = int(kospi.get("individual", 0)) + int(kosdaq.get("individual", 0))

            return {
                "foreign_net": float(foreign_total),
                "institution_net": float(institution_total),
                "retail_net": float(retail_total),
                "korean_market_flow": flow,
            }, None
        except Exception as exc:
            return None, f"krx_flow_unavailable: {exc}"

    def get_headlines(self, limit: int) -> Tuple[List[str] | None, str | None]:
        """Fetch headlines for agents.

        Priority:
        1) Latest hourly topic digest (`runs/news/latest_news_digest.json`) if available
        2) Fallback to live RSS (`build_news_digest`)
        """
        digest_headlines = _load_latest_topic_digest_headlines(limit=limit)
        if digest_headlines:
            return digest_headlines, None

        titles, _digest, reason = build_news_digest(query="KOSPI", limit=limit)
        if not titles:
            return None, reason or "no_titles"
        return titles[:limit], None


def _default_headers() -> dict:
    """Return common headers for HTTP requests."""
    return {"User-Agent": "DailyAIInvestmentCommittee/1.0"}


def _yahoo_daily_pct_chart(symbol: str) -> Tuple[float, None]:
    """Compute daily pct change from Yahoo Finance chart (2d range).
    Data source: query1.finance.yahoo.com v8/finance/chart. Raises on failure
    so caller can catch and return (None, reason); fallback 0.0 is applied by snapshot builder.
    """
    intraday = requests.get(
        f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1m&range=1d",
        timeout=7,
        headers=_default_headers(),
    )
    if intraday.status_code == 200:
        payload = intraday.json()
        result = payload.get("chart", {}).get("result", [])
        if result:
            meta = result[0].get("meta", {}) or {}
            regular = meta.get("regularMarketPrice")
            prev_close = meta.get("chartPreviousClose")
            if regular is not None and prev_close is not None:
                regular_f = float(regular)
                prev_f = float(prev_close)
                if prev_f > 0:
                    pct = ((regular_f - prev_f) / prev_f) * 100.0
                    return (pct, None)

    response = requests.get(
        f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1d&range=7d",
        timeout=7,
        headers=_default_headers(),
    )
    if response.status_code != 200:
        raise RuntimeError(f"http_status_{response.status_code}")
    payload = response.json()
    result = payload.get("chart", {}).get("result", [])
    if not result:
        raise RuntimeError("no_result")
    closes = result[0].get("indicators", {}).get("quote", [])[0].get("close", [])
    closes = [v for v in closes if v is not None]
    if len(closes) < 2:
        raise RuntimeError("insufficient_closes")
    prev_close, latest_close = closes[-2], closes[-1]
    pct = ((latest_close - prev_close) / prev_close) * 100.0
    return (pct, None)


def _extract_json_value(payload: dict, path: tuple) -> float | None:
    """Extract nested value by path from JSON payload."""
    current = payload
    for key in path:
        if not isinstance(current, dict) or key not in current:
            return None
        current = current[key]
    return current


def _load_latest_topic_digest_headlines(limit: int) -> List[str]:
    """Load top article titles from hourly topic digest if present."""
    try:
        root = Path(__file__).resolve().parents[2]
        digest_path = root / "runs" / "news" / "latest_news_digest.json"
        if not digest_path.exists():
            return []
        payload = json.loads(digest_path.read_text(encoding="utf-8"))
        top_articles = payload.get("top_articles", [])
        if not isinstance(top_articles, list):
            return []

        headlines: List[str] = []
        for article in top_articles:
            if not isinstance(article, dict):
                continue
            topic = str(article.get("topic", "")).strip()
            title = str(article.get("title", "")).strip()
            if not title:
                continue
            if topic:
                headlines.append(f"[{topic}] {title}"[:200])
            else:
                headlines.append(title[:200])
            if len(headlines) >= max(limit, 1):
                break
        return headlines
    except Exception:
        return []
