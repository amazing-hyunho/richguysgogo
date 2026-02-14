from __future__ import annotations

# Snapshot builder for real-data v1 with fallback safety.
# Failure handling: each provider fetch is wrapped in _safe_value (or _safe_flows/_safe_headlines).
# On fetch failure we use fallback (0.0 or empty) so the pipeline never breaks; the failure reason
# is recorded in status and notes so the report can show which source failed.
# Fallback values (0.0) are used because downstream (report, agents) expect numeric fields;
# missing data is indicated via notes/status rather than omitting the key.
from datetime import date

from committee.schemas.snapshot import Snapshot
from committee.tools.fallback_provider import FallbackProvider
from committee.tools.http_provider import HttpProvider
from committee.tools.providers import IDataProvider


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
        notes.append(f"flows_fetch_failed: {flows_reason}")
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
    flow_error = "; ".join([n for n in notes if n.startswith("flows")])
    if flow_error:
        flow_note = f"{flow_error} (외국인/기관/개인 순매수는 데이터 없음)"
    else:
        f_net, i_net, r_net = flows["foreign_net"], flows["institution_net"], flows["retail_net"]
        flow_note = f"외국인 {f_net:+.0f}억, 기관 {i_net:+.0f}억, 개인 {r_net:+.0f}억"

    # Build top-level "markets" (KR/US indices + FX); failed fetches already 0.0 via fallback.
    markets = {
        "kr": {"kospi_pct": kospi_change_pct, "kosdaq_pct": kosdaq_pct},
        "us": {"sp500_pct": sp500_pct, "nasdaq_pct": nasdaq_pct, "dow_pct": dow_pct},
        "fx": {"usdkrw": usdkrw, "usdkrw_pct": usdkrw_pct},
    }

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
        sector_moves=["n/a", "n/a", "n/a"],
        news_headlines=headlines,
        watchlist=["SPY", "QQQ", "XLK"],
        markets=markets,
    )


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


def _safe_flows(provider: IDataProvider, fallback: IDataProvider) -> tuple[dict[str, float], str | None]:
    """Fetch flows with fallback and a reason."""
    try:
        data, reason = provider.get_flows()
        data = data or {}
        foreign_net = float(data.get("foreign_net", 0.0))
        institution_net = float(data.get("institution_net", 0.0))
        retail_net = float(data.get("retail_net", 0.0))
        if data:
            return {
                "foreign_net": foreign_net,
                "institution_net": institution_net,
                "retail_net": retail_net,
            }, None
        raise ValueError(reason or "unavailable")
    except Exception as exc:  # noqa: BLE001 - guardrail
        fallback_data, fallback_reason = fallback.get_flows()
        fallback_data = fallback_data or {}
        return {
            "foreign_net": float(fallback_data.get("foreign_net", 0.0)),
            "institution_net": float(fallback_data.get("institution_net", 0.0)),
            "retail_net": float(fallback_data.get("retail_net", 0.0)),
        }, str(exc) if str(exc) else (fallback_reason or "unavailable")


def _safe_headlines(provider: IDataProvider) -> tuple[list[str], str | None]:
    """Fetch headlines with fallback and a reason."""
    try:
        headlines, reason = provider.get_headlines(limit=8)
        headlines = headlines or []
        if len(headlines) < 5:
            raise ValueError(reason or "insufficient headlines")
        return headlines[:10], None
    except Exception as exc:  # noqa: BLE001 - guardrail
        return [], str(exc) if str(exc) else "unavailable"


_LAST_STATUS: dict[str, str] = {}


def _set_last_status(status: dict[str, str]) -> None:
    """Store the latest snapshot source status."""
    _LAST_STATUS.clear()
    _LAST_STATUS.update(status)
