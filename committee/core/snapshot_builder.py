from __future__ import annotations

# Snapshot builder for real-data v1 with fallback safety.
# Failure handling: each provider fetch is wrapped in _safe_value (or _safe_flows/_safe_headlines).
# On fetch failure we use fallback (0.0 or empty) so the pipeline never breaks; the failure reason
# is recorded in status and notes so the report can show which source failed.
# Fallback values (0.0) are used because downstream (report, agents) expect numeric fields;
# missing data is indicated via notes/status rather than omitting the key.
from datetime import date
import os
import re

from committee.schemas.snapshot import Snapshot
from committee.tools.fallback_provider import FallbackProvider
from committee.tools.http_provider import HttpProvider
from committee.tools.providers import IDataProvider
from committee.tools.macro_daily_provider import fetch_dxy, fetch_us10y, fetch_us2y, fetch_usdkrw, fetch_vix
from committee.tools.fred_monthly_provider import (
    fetch_cpi_yoy,
    fetch_core_cpi_yoy,
    fetch_pce_yoy,
    fetch_pmi,
    fetch_unemployment_rate,
    fetch_wage_growth,
    fetch_wage_level,
    fetch_wage_yoy,
    pmi_series_ids_tried,
)
from committee.tools.fred_quarterly_provider import fetch_gdp_growth, fetch_real_gdp
from committee.tools.fred_structural_provider import fetch_breakeven_10y, fetch_fed_funds_rate


def build_snapshot(market_date: date) -> Snapshot:
    """Create a snapshot using the default real builder."""
    return build_snapshot_real(market_date)


def build_snapshot_real(
    market_date: date,
    provider: IDataProvider | None = None,
) -> Snapshot:
    """Build a snapshot using a data provider with fallback."""
    provider = provider or HttpProvider()
    fallback = FallbackProvider()

    notes: list[str] = []
    status: dict[str, str] = {
        "usdkrw": "FAIL", "kospi": "FAIL", "flows": "FAIL", "headlines": "FAIL",
        "kosdaq": "FAIL", "sp500": "FAIL", "nasdaq": "FAIL", "dow": "FAIL", "usdkrw_pct": "FAIL",
        # Phase 1: daily macro (yfinance only; missing values stored as NULL in DB).
        "us10y": "FAIL",
        "us2y": "FAIL",
        "spread_2_10": "FAIL",
        "vix": "FAIL",
        "dxy": "FAIL",
        "usdkrw_macro": "FAIL",
        # Phase 2: monthly macro (FRED).
        "unemployment_rate": "FAIL",
        "cpi_yoy": "FAIL",
        "core_cpi_yoy": "FAIL",
        "pce_yoy": "FAIL",
        "pmi": "FAIL",
        "wage_growth": "FAIL",
        # Phase 3 quarterly macro.
        "real_gdp": "FAIL",
        "gdp_qoq_annualized": "FAIL",
        # Phase 4 structural.
        "fed_funds_rate": "FAIL",
        "breakeven_10y": "FAIL",
        "real_rate": "FAIL",
    }

    usdkrw, usdkrw_reason = _safe_value(provider.get_usdkrw, fallback.get_usdkrw)
    kospi_change_pct, kospi_reason = _safe_value(provider.get_kospi_change_pct, fallback.get_kospi_change_pct)
    flows, flows_reason = _safe_flows(provider, fallback)
    headlines, headlines_reason = _safe_headlines(provider)

    # Global markets: fetch with fallback; on failure use 0.0 and record reason in notes.
    kosdaq_pct, kosdaq_reason = _safe_value(provider.get_kosdaq_change_pct, fallback.get_kosdaq_change_pct)
    sp500_pct, sp500_reason = _safe_value(provider.get_sp500_change_pct, fallback.get_sp500_change_pct)
    nasdaq_pct, nasdaq_reason = _safe_value(provider.get_nasdaq_change_pct, fallback.get_nasdaq_change_pct)
    dow_pct, dow_reason = _safe_value(provider.get_dow_change_pct, fallback.get_dow_change_pct)
    usdkrw_pct, usdkrw_pct_reason = _safe_value(provider.get_usdkrw_pct, fallback.get_usdkrw_pct)

    # Phase 1: daily macro (yfinance only). Missing values are None -> DB NULL.
    us10y = fetch_us10y()
    us2y = fetch_us2y()
    vix_value = fetch_vix()
    dxy = fetch_dxy()
    usdkrw_macro = fetch_usdkrw()

    # Spread calculation: only when both yields are available.
    spread_2_10 = (us10y - us2y) if (us10y is not None and us2y is not None) else None

    # Phase 2: monthly macro (FRED). Missing FRED key -> None for all values.
    unemployment_rate = fetch_unemployment_rate()
    cpi_yoy = fetch_cpi_yoy()
    core_cpi_yoy = fetch_core_cpi_yoy()
    pce_yoy = fetch_pce_yoy()
    pmi = fetch_pmi()
    wage_level = fetch_wage_level()
    wage_yoy = fetch_wage_yoy()
    # Backward compatibility: keep wage_growth populated with the level series.
    wage_growth = wage_level

    # Phase 3 quarterly macro (FRED).
    real_gdp = fetch_real_gdp()
    gdp_qoq_annualized = fetch_gdp_growth()

    # Phase 4 structural (FRED) + derived real rate.
    fed_funds_rate = fetch_fed_funds_rate()
    breakeven_10y = fetch_breakeven_10y()
    real_rate = (us10y - breakeven_10y) if (us10y is not None and breakeven_10y is not None) else None

    if usdkrw_reason is None:
        status["usdkrw"] = "OK"
    else:
        notes.append(f"usdkrw_fetch_failed: {usdkrw_reason}")
    if kospi_reason is None:
        status["kospi"] = "OK"
    else:
        notes.append(f"kospi_change_pct_fetch_failed: {kospi_reason}")
    if flows_reason is None:
        status["flows"] = "OK"
    else:
        # IMPORTANT: Avoid leaking KRX internal identifiers (e.g., "MDC", "STK", "KSQ")
        # into notes because the ticker-guard validator treats ALLCAPS tokens as tickers.
        notes.append(f"flows_fetch_failed: {_sanitize_ticker_like_tokens(flows_reason)}")
    if headlines_reason is None:
        status["headlines"] = "OK"
    else:
        notes.append(f"headlines_fetch_failed: {headlines_reason}")
    # Status for new markets keys; failure reasons go to notes so report can show them.
    if kosdaq_reason is None:
        status["kosdaq"] = "OK"
    else:
        notes.append(f"kosdaq_fetch_failed: {kosdaq_reason}")
    if sp500_reason is None:
        status["sp500"] = "OK"
    else:
        notes.append(f"sp500_fetch_failed: {sp500_reason}")
    if nasdaq_reason is None:
        status["nasdaq"] = "OK"
    else:
        notes.append(f"nasdaq_fetch_failed: {nasdaq_reason}")
    if dow_reason is None:
        status["dow"] = "OK"
    else:
        notes.append(f"dow_fetch_failed: {dow_reason}")
    if usdkrw_pct_reason is None:
        status["usdkrw_pct"] = "OK"
    else:
        notes.append(f"usdkrw_pct_fetch_failed: {usdkrw_pct_reason}")

    if vix_value is not None:
        status["vix"] = "OK"
        vix = float(vix_value)
    else:
        # Keep snapshot stable with a numeric value, but DB will store NULL when status != OK.
        notes.append("vix_fetch_failed: unavailable")
        vix = 0.0

    # Phase 1 macro status updates (daily only).
    status["us10y"] = "OK" if us10y is not None else "FAIL"
    status["us2y"] = "OK" if us2y is not None else "FAIL"
    status["dxy"] = "OK" if dxy is not None else "FAIL"
    status["usdkrw_macro"] = "OK" if usdkrw_macro is not None else "FAIL"
    status["spread_2_10"] = "OK" if spread_2_10 is not None else "FAIL"

    # Phase 2 monthly status tracking (FAIL when missing/unavailable).
    status["unemployment_rate"] = "OK" if unemployment_rate is not None else "FAIL"
    status["cpi_yoy"] = "OK" if cpi_yoy is not None else "FAIL"
    status["core_cpi_yoy"] = "OK" if core_cpi_yoy is not None else "FAIL"
    status["pce_yoy"] = "OK" if pce_yoy is not None else "FAIL"
    status["pmi"] = "OK" if pmi is not None else "FAIL"
    status["wage_growth"] = "OK" if wage_growth is not None else "FAIL"
    status["wage_level"] = "OK" if wage_level is not None else "FAIL"
    status["wage_yoy"] = "OK" if wage_yoy is not None else "FAIL"
    if pmi is None:
        # Document which sources were attempted so failures are traceable.
        notes.append(f"pmi_fetch_failed: tried={','.join(pmi_series_ids_tried())}")

    # Phase 3 quarterly status.
    status["real_gdp"] = "OK" if real_gdp is not None else "FAIL"
    status["gdp_qoq_annualized"] = "OK" if gdp_qoq_annualized is not None else "FAIL"

    # Phase 4 structural status.
    status["fed_funds_rate"] = "OK" if fed_funds_rate is not None else "FAIL"
    status["breakeven_10y"] = "OK" if breakeven_10y is not None else "FAIL"
    status["real_rate"] = "OK" if real_rate is not None else "FAIL"
    _set_last_status(status)

    if usdkrw != 0.0 or kospi_change_pct != 0.0:
        headlines_state = "Headlines loaded." if headlines_reason is None else "Headlines unavailable."
        flows_state = "Flows loaded." if flows_reason is None else "Flows unavailable."
        market_note = (
            f"KOSPI {kospi_change_pct:.2f}%, USD/KRW {usdkrw:.2f}. "
            f"{headlines_state} {flows_state}"
        )
    else:
        market_note = "; ".join(
            [note for note in notes if note.startswith("usdkrw") or note.startswith("kospi")]
        )
    korean_market_flow = flows.get("korean_market_flow") if isinstance(flows, dict) else None

    flow_error = "; ".join([n for n in notes if n.startswith("flows")])
    if flow_error:
        flow_note = f"{flow_error} (외국인/기관/개인 순매수는 데이터 없음)"
    else:
        f_net, i_net, r_net = flows["foreign_net"], flows["institution_net"], flows["retail_net"]
        flow_note = f"외국인 {f_net:+.0f}억, 기관 {i_net:+.0f}억, 개인 {r_net:+.0f}억"
        # If PyKRX breakdown exists, append a compact per-market note (keep within 500 chars).
        try:
            if korean_market_flow and isinstance(korean_market_flow, dict):
                mk = korean_market_flow.get("market", {}) or {}
                k1 = mk.get("KOSPI", {}) or {}
                k2 = mk.get("KOSDAQ", {}) or {}
                flow_note += (
                    f" | KOSPI(외 {int(k1.get('foreign', 0)):+d},"
                    f" 기관 {int(k1.get('institution', 0)):+d},"
                    f" 개인 {int(k1.get('individual', 0)):+d})"
                    f" KOSDAQ(외 {int(k2.get('foreign', 0)):+d},"
                    f" 기관 {int(k2.get('institution', 0)):+d},"
                    f" 개인 {int(k2.get('individual', 0)):+d})"
                )
        except Exception:
            pass

    # Build top-level "markets" (KR/US indices + FX); failed fetches already 0.0 via fallback.
    markets = {
        "kr": {"kospi_pct": kospi_change_pct, "kosdaq_pct": kosdaq_pct},
        "us": {"sp500_pct": sp500_pct, "nasdaq_pct": nasdaq_pct, "dow_pct": dow_pct},
        "fx": {"usdkrw": usdkrw, "usdkrw_pct": usdkrw_pct},
        "volatility": {"vix": vix},
    }

    phase_two_signals = _compute_phase_two_signals(
        headlines=headlines,
        markets=markets,
        macro_daily={
            "dxy": dxy,
            "spread_2_10": spread_2_10,
        },
        macro_structural={"real_rate": real_rate},
    )

    return Snapshot(
        market_summary={
            "note": market_note or "market_summary_note_unavailable",
            "kospi_change_pct": kospi_change_pct,
            "usdkrw": usdkrw,
        },
        flow_summary={
            "note": flow_note[:500],  # MediumText max 500
            "foreign_net": flows["foreign_net"],
            "institution_net": flows["institution_net"],
            "retail_net": flows["retail_net"],
        },
        korean_market_flow=korean_market_flow,
        sector_moves=["n/a", "n/a", "n/a"],
        news_headlines=headlines,
        watchlist=["SPY", "QQQ", "XLK"],
        markets=markets,
        phase_two_signals=phase_two_signals,
        macro={
            "daily": {
                "us10y": us10y,
                "us2y": us2y,
                "spread_2_10": spread_2_10,
                "vix": float(vix_value) if vix_value is not None else None,
                "dxy": dxy,
                "usdkrw": usdkrw_macro,
            },
            "monthly": {
                "unemployment_rate": unemployment_rate,
                "cpi_yoy": cpi_yoy,
                "core_cpi_yoy": core_cpi_yoy,
                "pce_yoy": pce_yoy,
                "pmi": pmi,
                "wage_growth": wage_growth,
                "wage_level": wage_level,
                "wage_yoy": wage_yoy,
            },
            "quarterly": {
                "real_gdp": real_gdp,
                "gdp_qoq_annualized": gdp_qoq_annualized,
            },
            "structural": {
                "fed_funds_rate": fed_funds_rate,
                "real_rate": real_rate,
            },
        },
    )


def _compute_phase_two_signals(
    headlines: list[str],
    markets: dict,
    macro_daily: dict,
    macro_structural: dict,
) -> dict:
    """Build derived earnings/breadth/liquidity signals from existing inputs only."""
    headline_text = " ".join(headlines).lower()
    positive = sum(token in headline_text for token in ["earnings beat", "guidance up", "estimate up", "eps beat", "upgrade"])
    negative = sum(token in headline_text for token in ["earnings miss", "guidance cut", "estimate down", "eps miss", "downgrade"])
    earnings_score = float(positive - negative)

    kr = (markets.get("kr") or {}) if isinstance(markets, dict) else {}
    us = (markets.get("us") or {}) if isinstance(markets, dict) else {}
    kr_avg = (float(kr.get("kospi_pct", 0.0)) + float(kr.get("kosdaq_pct", 0.0))) / 2.0
    us_avg = (
        float(us.get("sp500_pct", 0.0))
        + float(us.get("nasdaq_pct", 0.0))
        + float(us.get("dow_pct", 0.0))
    ) / 3.0
    breadth_score = float(kr_avg - us_avg)

    dxy = macro_daily.get("dxy")
    spread_2_10 = macro_daily.get("spread_2_10")
    real_rate = macro_structural.get("real_rate")

    liquidity_score = 0.0
    if dxy is not None:
        liquidity_score += (100.0 - float(dxy)) / 5.0
    if real_rate is not None:
        liquidity_score += (1.5 - float(real_rate))
    if spread_2_10 is not None:
        liquidity_score += float(spread_2_10) * 2.0

    return {
        "earnings_signal_score": round(earnings_score, 3),
        "breadth_signal_score": round(breadth_score, 3),
        "liquidity_signal_score": round(liquidity_score, 3),
        "note": "derived from headlines + markets + macro.daily + macro.structural",
    }


def build_dummy_snapshot(market_date: date) -> Snapshot:
    """Return a deterministic snapshot without external dependencies."""
    fallback = FallbackProvider()
    usdkrw, _ = fallback.get_usdkrw()
    kospi_change_pct, _ = fallback.get_kospi_change_pct()
    # Dummy markets: all 0.0 to keep pipeline and JSON structure intact.
    markets = {
        "kr": {"kospi_pct": kospi_change_pct or 0.0, "kosdaq_pct": 0.0},
        "us": {"sp500_pct": 0.0, "nasdaq_pct": 0.0, "dow_pct": 0.0},
        "fx": {"usdkrw": usdkrw or 0.0, "usdkrw_pct": 0.0},
        "volatility": {"vix": 0.0},
    }
    return Snapshot(
        market_summary={
            "note": f"{market_date.isoformat()} dummy snapshot",
            "kospi_change_pct": kospi_change_pct or 0.0,
            "usdkrw": usdkrw or 0.0,
        },
        flow_summary={
            "note": "dummy flow summary",
            "foreign_net": 0.0,
            "institution_net": 0.0,
            "retail_net": 0.0,
        },
        sector_moves=["n/a", "n/a", "n/a"],
        news_headlines=[],
        watchlist=["SPY", "QQQ", "XLK"],
        markets=markets,
        phase_two_signals={
            "earnings_signal_score": 0.0,
            "breadth_signal_score": 0.0,
            "liquidity_signal_score": 0.0,
            "note": "dummy derived signals",
        },
    )


def get_last_snapshot_status() -> dict[str, str]:
    """Return the most recent snapshot source status."""
    return dict(_LAST_STATUS)


def _safe_value(fetcher, fallback_fetcher) -> tuple[float, str | None]:
    """Fetch a numeric value with fallback and a reason.
    On success returns (value, None). On failure uses fallback (0.0) and returns (0.0, reason)
    so caller can append reason to snapshot status/notes.
    """
    try:
        value, reason = fetcher()
        if value is None:
            raise ValueError(reason or "unavailable")
        return float(value), None
    except Exception as exc:  # noqa: BLE001 - guardrail
        fallback_value, fallback_reason = fallback_fetcher()
        return float(fallback_value or 0.0), str(exc) if str(exc) else (fallback_reason or "unavailable")


def _safe_flows(provider: IDataProvider, fallback: IDataProvider) -> tuple[dict, str | None]:
    """Fetch flows with fallback and a reason."""
    try:
        data, reason = provider.get_flows()
        data = data or {}
        foreign_net = float(data.get("foreign_net", 0.0))
        institution_net = float(data.get("institution_net", 0.0))
        retail_net = float(data.get("retail_net", 0.0))
        if data:
            out: dict = {
                "foreign_net": foreign_net,
                "institution_net": institution_net,
                "retail_net": retail_net,
            }
            if "korean_market_flow" in data:
                out["korean_market_flow"] = data["korean_market_flow"]
            return out, None
        raise ValueError(reason or "unavailable")
    except Exception as exc:  # noqa: BLE001 - guardrail
        fallback_data, fallback_reason = fallback.get_flows()
        fallback_data = fallback_data or {}
        return {
            "foreign_net": float(fallback_data.get("foreign_net", 0.0)),
            "institution_net": float(fallback_data.get("institution_net", 0.0)),
            "retail_net": float(fallback_data.get("retail_net", 0.0)),
        }, str(exc) if str(exc) else (fallback_reason or "unavailable")


def _sanitize_ticker_like_tokens(text: str | None) -> str:
    """Lowercase ticker-like ALLCAPS tokens to avoid validator false positives."""
    if not text:
        return "unavailable"
    # Matches the same pattern as validators.TICKER_PATTERN, so we neutralize those tokens.
    return re.sub(r"\b[A-Z][A-Z0-9]{1,11}\b", lambda m: m.group(0).lower(), str(text))


def _safe_headlines(provider: IDataProvider) -> tuple[list[str], str | None]:
    """Fetch headlines with fallback and a reason."""
    try:
        headlines, reason = provider.get_headlines(limit=50)
        headlines = headlines or []
        if len(headlines) < 5:
            raise ValueError(reason or "insufficient headlines")
        return headlines[:50], None
    except Exception as exc:  # noqa: BLE001 - guardrail
        return [], str(exc) if str(exc) else "unavailable"


_LAST_STATUS: dict[str, str] = {}


def _set_last_status(status: dict[str, str]) -> None:
    """Store the latest snapshot source status."""
    _LAST_STATUS.clear()
    _LAST_STATUS.update(status)
