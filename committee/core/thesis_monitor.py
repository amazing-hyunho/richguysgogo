from __future__ import annotations

"""Rules-based Investment Thesis Monitor.

The LLM may help classify notes/news, but final scores and recommended actions
are deterministic here so the dashboard remains usable when AI calls fail.
"""

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import json
import sqlite3

from committee.core.database import connect, get_db_path, init_db
from committee.core.stock_watchlist import get_stocks


ACTION_LABELS = {
    "strong_buy_candidate": "매수 후보",
    "buy_on_pullback": "조정 시 분할매수",
    "watch": "관망",
    "no_new_buy": "신규매수 보류",
    "reduce": "비중 축소",
    "sell_or_hedge": "매도 / 헤지 검토",
}


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def clamp(value: float, low: float = -100.0, high: float = 100.0) -> float:
    return max(low, min(high, float(value)))


def _num(value: Any) -> float | None:
    if value is None:
        return None
    try:
        f = float(value)
    except (TypeError, ValueError):
        return None
    return f if f == f else None


def _last(rows: list[dict[str, Any]]) -> dict[str, Any]:
    return rows[-1] if rows else {}


def _change(rows: list[dict[str, Any]], key: str, lookback: int) -> float | None:
    vals = [(_num(r.get(key)), r) for r in rows if _num(r.get(key)) is not None]
    if len(vals) <= lookback:
        return None
    latest = vals[-1][0]
    prev = vals[-1 - lookback][0]
    if latest is None or prev is None:
        return None
    return latest - prev


def _pct_change(rows: list[dict[str, Any]], key: str, lookback: int) -> float | None:
    vals = [(_num(r.get(key)), r) for r in rows if _num(r.get(key)) is not None]
    if len(vals) <= lookback:
        return None
    latest = vals[-1][0]
    prev = vals[-1 - lookback][0]
    if latest is None or prev in (None, 0):
        return None
    return (latest / prev - 1.0) * 100.0


def score_market_regime(
    *,
    daily_macro: list[dict[str, Any]],
    market_daily: list[dict[str, Any]],
    market_flow_daily: list[dict[str, Any]],
) -> dict[str, Any]:
    """Calculate risk appetite from already-collected indicators."""
    dm = _last(daily_macro)
    flow = _last(market_flow_daily)
    score = 0.0
    reasons: list[str] = []

    vix = _num(dm.get("vix"))
    if vix is not None:
        if vix < 16:
            score += 18
            reasons.append("VIX 안정")
        elif vix < 22:
            score += 4
        elif vix < 30:
            score -= 18
            reasons.append("VIX 경계")
        else:
            score -= 34
            reasons.append("VIX stress")

    vix_term = _num(dm.get("vix_term_spread"))
    if vix_term is not None:
        score += clamp(vix_term * 3.0, -12, 12)

    for key, label, scale in [
        ("dxy", "DXY 상승", -0.8),
        ("usdkrw", "USD/KRW 상승", -0.05),
        ("hy_oas", "HY OAS 확대", -7.0),
        ("ig_oas", "IG OAS 확대", -10.0),
        ("real_rate", "실질금리 상승", -8.0),
    ]:
        chg = _change(daily_macro, key, 5)
        if chg is None:
            continue
        adj = clamp(chg * scale, -15, 15)
        score += adj
        if adj < -6:
            reasons.append(label)

    foreign20 = _num(flow.get("foreign_20d")) or _num(flow.get("kospi_foreign_net"))
    if foreign20 is not None:
        score += clamp(foreign20 / 2500.0, -18, 18)
        if foreign20 > 0:
            reasons.append("외국인 수급 우호")

    kospi20 = _pct_change(market_daily, "kospi", 20)
    kosdaq20 = _pct_change(market_daily, "kosdaq", 20)
    nasdaq20 = _pct_change(market_daily, "nasdaq", 20)
    rut20 = _pct_change(daily_macro, "russell2000", 20)
    if kospi20 is not None and kosdaq20 is not None:
        score += clamp((kosdaq20 - kospi20) * 1.5, -10, 10)
    if nasdaq20 is not None:
        score += clamp(nasdaq20 * 1.2, -12, 12)
    if rut20 is not None:
        score += clamp(rut20 * 1.0, -10, 10)

    score = clamp(score)
    if score >= 60:
        regime = "strong_risk_on"
    elif score >= 25:
        regime = "risk_on"
    elif score <= -60:
        regime = "stress"
    elif score <= -25:
        regime = "risk_off"
    else:
        regime = "neutral"
    return {"regime": regime, "risk_appetite_score": round(score, 1), "reasons": reasons[:5]}


def recommended_action_from_score(score: float, *, regime: str, has_price_flow_confirmation: bool = True) -> str:
    if score >= 70:
        action = "strong_buy_candidate"
    elif score >= 35:
        action = "buy_on_pullback"
    elif score >= -34:
        action = "watch"
    elif score >= -69:
        action = "reduce" if score < -50 else "no_new_buy"
    else:
        action = "sell_or_hedge"

    if action == "strong_buy_candidate" and regime in {"risk_off", "stress"}:
        return "buy_on_pullback" if regime == "risk_off" else "watch"
    if action in {"strong_buy_candidate", "buy_on_pullback"} and not has_price_flow_confirmation:
        return "watch"
    return action


def calculate_thesis_score(
    *,
    evidence_support_score: float = 0.0,
    evidence_contradiction_score: float = 0.0,
    macro_confirmation_score: float = 0.0,
    flow_confirmation_score: float = 0.0,
    price_confirmation_score: float = 0.0,
    risk_score: float = 0.0,
    recent_5d_delta: float = 0.0,
    recent_20d_delta: float = 0.0,
    invalidation_hit: bool = False,
    market_regime: str = "neutral",
) -> dict[str, Any]:
    raw = (
        evidence_support_score
        - evidence_contradiction_score
        + macro_confirmation_score
        + flow_confirmation_score
        + price_confirmation_score
        - risk_score
    )
    if recent_5d_delta < -20:
        raw -= 12
    if recent_20d_delta < -30:
        raw -= 10
    if invalidation_hit:
        raw -= 55

    score = clamp(raw)
    if invalidation_hit and score <= -35:
        trend = "invalidated"
    elif recent_5d_delta > 8:
        trend = "strengthening"
    elif recent_5d_delta < -8:
        trend = "weakening"
    else:
        trend = "stable"

    has_confirmation = (flow_confirmation_score + price_confirmation_score) >= 8
    action = recommended_action_from_score(score, regime=market_regime, has_price_flow_confirmation=has_confirmation)
    position_multiplier = 0.0
    if action == "strong_buy_candidate":
        position_multiplier = 1.0
    elif action == "buy_on_pullback":
        position_multiplier = 0.6
    elif action == "watch":
        position_multiplier = 0.25
    elif action == "no_new_buy":
        position_multiplier = 0.0
    elif action == "reduce":
        position_multiplier = -0.3
    else:
        position_multiplier = -0.7

    return {
        "thesis_score": round(score, 1),
        "thesis_trend": trend,
        "recommended_action": action,
        "position_multiplier": position_multiplier,
    }


def filter_point_in_time_rows(rows: list[dict[str, Any]], asof: str) -> list[dict[str, Any]]:
    """Keep only rows observable at `asof` to avoid future leakage."""
    out: list[dict[str, Any]] = []
    for row in rows:
        observed = row.get("observed_at") or row.get("published_at") or row.get("date")
        if observed is None or str(observed) <= asof:
            out.append(row)
    return out


def parse_news_evidence_json(payload: str | dict[str, Any]) -> dict[str, Any]:
    data = json.loads(payload) if isinstance(payload, str) else dict(payload)
    direction = data.get("direction", "neutral")
    if direction not in {"support", "contradict", "neutral"}:
        direction = "neutral"
    return {
        "thesis_id": int(data.get("thesis_id") or 0),
        "relevance": clamp(float(data.get("relevance", 0.0)), 0.0, 1.0),
        "direction": direction,
        "strength": clamp(float(data.get("strength", 0.0)), 0.0, 1.0),
        "novelty": clamp(float(data.get("novelty", 0.0)), 0.0, 1.0),
        "reliability": clamp(float(data.get("reliability", 0.0)), 0.0, 1.0),
        "summary": str(data.get("summary") or "").strip(),
        "reasoning": str(data.get("reasoning") or "").strip(),
        "new_variables": data.get("new_variables") if isinstance(data.get("new_variables"), list) else [],
    }


def insert_thesis_evidence(
    evidence: dict[str, Any],
    *,
    date: str,
    evidence_type: str = "news",
    source_id: str | None = None,
    db_path: Path | None = None,
) -> int:
    init_db(db_path)
    item = parse_news_evidence_json(evidence)
    impact_score = item["relevance"] * item["strength"] * item["reliability"] * 100.0
    with connect(db_path) as conn:
        cur = conn.execute(
            """
            INSERT INTO thesis_evidence_daily (
                date, thesis_id, evidence_type, source_id, direction,
                strength, novelty, reliability, impact_score, summary, reasoning, created_at
            ) VALUES (
                :date, :thesis_id, :evidence_type, :source_id, :direction,
                :strength, :novelty, :reliability, :impact_score, :summary, :reasoning, :created_at
            );
            """,
            {
                "date": date,
                "thesis_id": item["thesis_id"],
                "evidence_type": evidence_type,
                "source_id": source_id,
                "direction": item["direction"],
                "strength": item["strength"],
                "novelty": item["novelty"],
                "reliability": item["reliability"],
                "impact_score": impact_score,
                "summary": item["summary"],
                "reasoning": item["reasoning"],
                "created_at": _utc_now_iso(),
            },
        )
        return int(cur.lastrowid)


def _fetch_rows(conn: sqlite3.Connection, query: str, params: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    rows = conn.execute(query, params or {}).fetchall()
    return [dict(r) for r in rows]


def _list_from_json(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(v).strip() for v in value if str(v).strip()]
    if not value:
        return []
    try:
        parsed = json.loads(str(value))
        if isinstance(parsed, list):
            return [str(v).strip() for v in parsed if str(v).strip()]
    except Exception:
        pass
    return [v.strip() for v in str(value).split(",") if v.strip()]


def _text_tokens(*parts: Any) -> set[str]:
    text = " ".join(str(p or "") for p in parts).lower()
    tokens: set[str] = set()
    for raw in text.replace("/", " ").replace(",", " ").split():
        token = raw.strip().strip("()[]{}'\"")
        if len(token) >= 2:
            tokens.add(token)
    return tokens


def _related_watchlist_stocks(
    thesis: dict[str, Any],
    asset_rows: list[dict[str, Any]],
    watchlist: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    explicit = {
        str(row.get("ticker") or row.get("asset_id") or "").strip().upper()
        for row in asset_rows
        if int(row.get("thesis_id") or 0) == int(thesis.get("id") or 0)
    }
    thesis_tokens = _text_tokens(
        thesis.get("title"),
        thesis.get("summary"),
        thesis.get("core_claim"),
        thesis.get("raw_study_text"),
        thesis.get("thesis_type"),
        *_list_from_json(thesis.get("news_keywords_json")),
        *_list_from_json(thesis.get("beneficiaries_json")),
    )
    out: list[dict[str, Any]] = []
    for stock in watchlist:
        ticker = str(stock.get("ticker") or "").strip().upper()
        sector = str(stock.get("sector") or "").strip()
        name = str(stock.get("name") or "").strip()
        stock_tokens = _text_tokens(ticker, name, sector)
        if ticker in explicit or (sector and thesis_tokens.intersection(stock_tokens)):
            out.append(dict(stock))
    return out


def _stock_context_for_thesis(
    thesis: dict[str, Any],
    *,
    asset_rows: list[dict[str, Any]],
    watchlist: list[dict[str, Any]],
    stock_news: list[dict[str, Any]],
    stock_consensus: list[dict[str, Any]],
) -> dict[str, Any]:
    related = _related_watchlist_stocks(thesis, asset_rows, watchlist)
    tickers = {str(s.get("ticker") or "").strip().upper() for s in related}
    news = [n for n in stock_news if str(n.get("ticker") or "").strip().upper() in tickers]
    latest_consensus = {
        str(c.get("ticker") or "").strip().upper(): c
        for c in stock_consensus
        if str(c.get("ticker") or "").strip().upper() in tickers
    }
    score = 0.0
    reasons: list[str] = []
    for stock in related:
        ticker = str(stock.get("ticker") or "").strip().upper()
        c = latest_consensus.get(ticker)
        if not c:
            continue
        rec = str(c.get("recommendation_key") or "").lower()
        mean = _num(c.get("recommendation_mean"))
        current = _num(c.get("current_price"))
        target = _num(c.get("target_mean_price"))
        if rec in {"strong buy", "buy"} or (mean is not None and mean <= 2.2):
            score += 4
            reasons.append(f"{ticker} 컨센서스 우호")
        if current not in (None, 0) and target is not None:
            upside = (target / current - 1.0) * 100.0
            if upside >= 10:
                score += 3
                reasons.append(f"{ticker} 목표가 괴리율 +{upside:.0f}%")
            elif upside <= -10:
                score -= 3
                reasons.append(f"{ticker} 목표가 부담")
    if news:
        score += min(6.0, len(news) * 0.5)
        reasons.append(f"연결 종목 뉴스 {len(news)}건 갱신")
    return {
        "related_stocks": related,
        "recent_news_count": len(news),
        "stock_context_score": clamp(score, -15, 15),
        "reasons": reasons[:6],
    }


def load_thesis_monitor_data(db_path: Path | None = None) -> dict[str, Any]:
    """Load dashboard-ready Thesis Monitor data from SQLite."""
    init_db(db_path)
    with connect(db_path or get_db_path()) as conn:
        theses = _fetch_rows(conn, "SELECT * FROM investment_thesis ORDER BY updated_at DESC, id DESC")
        indicators = _fetch_rows(conn, "SELECT * FROM thesis_indicator_map ORDER BY thesis_id, weight DESC")
        assets = _fetch_rows(conn, "SELECT * FROM thesis_asset_map ORDER BY thesis_id, relation_type, asset_id")
        evidence = _fetch_rows(conn, "SELECT * FROM thesis_evidence_daily ORDER BY date DESC, id DESC LIMIT 200")
        signals = _fetch_rows(conn, "SELECT * FROM thesis_signal_daily ORDER BY date DESC, thesis_id")
        stock_news = _fetch_rows(conn, "SELECT ticker, title, published_at, source, link FROM stock_news ORDER BY COALESCE(published_at, collected_at) DESC LIMIT 500")
        stock_consensus = _fetch_rows(
            conn,
            """
            SELECT s.*
            FROM stock_consensus s
            INNER JOIN (
                SELECT ticker, MAX(date) AS max_date
                FROM stock_consensus
                GROUP BY ticker
            ) latest ON s.ticker = latest.ticker AND s.date = latest.max_date
            """,
        )
        daily_macro = _fetch_rows(conn, "SELECT * FROM daily_macro ORDER BY date")
        market_daily = _fetch_rows(conn, "SELECT * FROM market_daily ORDER BY date")
        market_flow = _fetch_rows(conn, "SELECT * FROM market_flow_daily ORDER BY date")
        regime = score_market_regime(
            daily_macro=daily_macro,
            market_daily=market_daily,
            market_flow_daily=market_flow,
        )
        watchlist = get_stocks()
        stock_context = {
            str(t.get("id")): _stock_context_for_thesis(
                t,
                asset_rows=assets,
                watchlist=watchlist,
                stock_news=stock_news,
                stock_consensus=stock_consensus,
            )
            for t in theses
        }
    return {
        "market_regime": regime,
        "theses": theses,
        "indicator_map": indicators,
        "asset_map": assets,
        "watchlist_stocks": watchlist,
        "stock_context": stock_context,
        "evidence": evidence,
        "signals": signals,
        "action_labels": ACTION_LABELS,
    }


def _series_for_indicator(
    key: str,
    *,
    daily_macro: list[dict[str, Any]],
    monthly_macro: list[dict[str, Any]],
    market_daily: list[dict[str, Any]],
    market_flow: list[dict[str, Any]],
) -> list[tuple[str, float]]:
    mapping = {
        "usdkrw": (daily_macro, "usdkrw"),
        "dxy": (daily_macro, "dxy"),
        "us_10y_yield": (daily_macro, "us_10y_yield"),
        "us_2y_yield": (daily_macro, "us_2y_yield"),
        "us_3m_yield": (daily_macro, "us_3m_yield"),
        "us_real_10y_yield": (daily_macro, "real_rate"),
        "vix": (daily_macro, "vix"),
        "vix_term_spread": (daily_macro, "vix_term_spread"),
        "hy_oas": (daily_macro, "hy_oas"),
        "ig_oas": (daily_macro, "ig_oas"),
        "fed_balance_sheet": (daily_macro, "fed_balance_sheet"),
        "tga_balance": (daily_macro, "tga_balance"),
        "foreign_flow_kospi_20d": (market_flow, "foreign_20d"),
        "foreign_flow_kospi_60d": (market_flow, "foreign_60d"),
        "korea_export_yoy": (monthly_macro, "export_yoy"),
        "cpi_yoy": (monthly_macro, "cpi_yoy"),
        "pce_yoy": (monthly_macro, "pce_yoy"),
        "pmi": (monthly_macro, "pmi"),
    }
    if key in {"kospi_return_20d", "nasdaq_return_20d"}:
        col = "kospi" if key.startswith("kospi") else "nasdaq"
        values: list[tuple[str, float]] = []
        for idx, row in enumerate(market_daily):
            if idx < 20:
                continue
            cur = _num(row.get(col))
            prev = _num(market_daily[idx - 20].get(col))
            if cur is not None and prev not in (None, 0):
                values.append((str(row.get("date")), (cur / prev - 1.0) * 100.0))
        return values
    rows, col = mapping.get(key, ([], ""))
    out: list[tuple[str, float]] = []
    for row in rows:
        value = _num(row.get(col))
        if value is not None:
            out.append((str(row.get("date")), value))
    return out


def score_indicator_map(
    mappings: list[dict[str, Any]],
    *,
    daily_macro: list[dict[str, Any]],
    monthly_macro: list[dict[str, Any]],
    market_daily: list[dict[str, Any]],
    market_flow: list[dict[str, Any]],
) -> dict[str, float]:
    macro = flow = price = risk = 0.0
    for item in mappings:
        key = str(item.get("indicator_key") or "")
        direction = str(item.get("expected_direction") or "neutral")
        weight = float(item.get("weight") or 1.0)
        lookback = max(1, int(item.get("lookback_days") or 20))
        threshold = _num(item.get("threshold"))
        series = _series_for_indicator(
            key,
            daily_macro=daily_macro,
            monthly_macro=monthly_macro,
            market_daily=market_daily,
            market_flow=market_flow,
        )
        if len(series) <= lookback:
            continue
        latest = series[-1][1]
        prev = series[-1 - lookback][1]
        delta = latest - prev
        if threshold is not None and abs(delta) < abs(threshold):
            continue
        if direction == "up":
            raw = delta
        elif direction == "down":
            raw = -delta
        else:
            raw = -abs(delta)
        contribution = clamp(raw * weight, -20, 20)
        if key.startswith("foreign_flow"):
            flow += contribution
        elif key.endswith("_return_20d") or key in {"kospi", "nasdaq"}:
            price += contribution
        elif key in {"vix", "hy_oas", "ig_oas"} and contribution < 0:
            risk += abs(contribution)
        else:
            macro += contribution
    return {
        "macro_confirmation_score": clamp(macro, -40, 40),
        "flow_confirmation_score": clamp(flow, -35, 35),
        "price_confirmation_score": clamp(price, -35, 35),
        "risk_score": clamp(risk, 0, 50),
    }


def update_thesis_signals(date: str, db_path: Path | None = None) -> int:
    """Calculate and upsert one daily signal for every active thesis."""
    init_db(db_path)
    now = _utc_now_iso()
    with connect(db_path or get_db_path()) as conn:
        theses = _fetch_rows(conn, "SELECT * FROM investment_thesis WHERE LOWER(COALESCE(status, '')) = 'active'")
        if not theses:
            return 0
        indicators = _fetch_rows(conn, "SELECT * FROM thesis_indicator_map")
        assets = _fetch_rows(conn, "SELECT * FROM thesis_asset_map")
        evidence = _fetch_rows(conn, "SELECT * FROM thesis_evidence_daily WHERE date <= :date", {"date": date})
        prior_signals = _fetch_rows(conn, "SELECT * FROM thesis_signal_daily WHERE date < :date ORDER BY date", {"date": date})
        stock_news = _fetch_rows(
            conn,
            "SELECT ticker, title, published_at, source, link FROM stock_news "
            "WHERE substr(COALESCE(published_at, collected_at, ''), 1, 10) <= :date "
            "ORDER BY COALESCE(published_at, collected_at) DESC LIMIT 500",
            {"date": date},
        )
        stock_consensus = _fetch_rows(
            conn,
            """
            SELECT s.*
            FROM stock_consensus s
            INNER JOIN (
                SELECT ticker, MAX(date) AS max_date
                FROM stock_consensus
                WHERE date <= :date
                GROUP BY ticker
            ) latest ON s.ticker = latest.ticker AND s.date = latest.max_date
            """,
            {"date": date},
        )
        daily_macro = filter_point_in_time_rows(_fetch_rows(conn, "SELECT * FROM daily_macro ORDER BY date"), date)
        monthly_macro = filter_point_in_time_rows(_fetch_rows(conn, "SELECT * FROM monthly_macro ORDER BY date"), date)
        market_daily = _fetch_rows(conn, "SELECT * FROM market_daily WHERE date <= :date ORDER BY date", {"date": date})
        market_flow = _fetch_rows(conn, "SELECT * FROM market_flow_daily WHERE date <= :date ORDER BY date", {"date": date})
        regime = score_market_regime(daily_macro=daily_macro, market_daily=market_daily, market_flow_daily=market_flow)
        watchlist = get_stocks()

        changed = 0
        for thesis in theses:
            tid = int(thesis["id"])
            thesis_evidence = [e for e in evidence if int(e.get("thesis_id") or 0) == tid][-50:]
            support = sum(float(e.get("impact_score") or 0.0) for e in thesis_evidence if e.get("direction") == "support")
            contradict = sum(float(e.get("impact_score") or 0.0) for e in thesis_evidence if e.get("direction") == "contradict")
            evidence_support_score = clamp(support / 3.0, 0, 35)
            evidence_contradiction_score = clamp(contradict / 3.0, 0, 45)
            imap = [i for i in indicators if int(i.get("thesis_id") or 0) == tid]
            confirmations = score_indicator_map(
                imap,
                daily_macro=daily_macro,
                monthly_macro=monthly_macro,
                market_daily=market_daily,
                market_flow=market_flow,
            )
            stock_context = _stock_context_for_thesis(
                thesis,
                asset_rows=assets,
                watchlist=watchlist,
                stock_news=stock_news,
                stock_consensus=stock_consensus,
            )
            confirmations["price_confirmation_score"] = clamp(
                confirmations["price_confirmation_score"] + float(stock_context["stock_context_score"]),
                -35,
                35,
            )
            priors = [s for s in prior_signals if int(s.get("thesis_id") or 0) == tid]
            recent_5d_delta = 0.0
            recent_20d_delta = 0.0
            if priors:
                last_score = _num(priors[-1].get("thesis_score")) or 0.0
                if len(priors) >= 5:
                    recent_5d_delta = last_score - (_num(priors[-5].get("thesis_score")) or last_score)
                if len(priors) >= 20:
                    recent_20d_delta = last_score - (_num(priors[-20].get("thesis_score")) or last_score)
            invalidation_hit = any(e.get("direction") == "contradict" and float(e.get("impact_score") or 0.0) >= 70 for e in thesis_evidence[-10:])
            result = calculate_thesis_score(
                evidence_support_score=evidence_support_score,
                evidence_contradiction_score=evidence_contradiction_score,
                macro_confirmation_score=confirmations["macro_confirmation_score"],
                flow_confirmation_score=confirmations["flow_confirmation_score"],
                price_confirmation_score=confirmations["price_confirmation_score"],
                risk_score=confirmations["risk_score"],
                recent_5d_delta=recent_5d_delta,
                recent_20d_delta=recent_20d_delta,
                invalidation_hit=invalidation_hit,
                market_regime=str(regime["regime"]),
            )
            reason = (
                f"evidence +{evidence_support_score:.1f}/-{evidence_contradiction_score:.1f}, "
                f"macro {confirmations['macro_confirmation_score']:.1f}, "
                f"flow {confirmations['flow_confirmation_score']:.1f}, "
                f"price {confirmations['price_confirmation_score']:.1f}, "
                f"stock {float(stock_context['stock_context_score']):.1f}, "
                f"risk {confirmations['risk_score']:.1f}, regime {regime['regime']}. "
                + "; ".join(stock_context["reasons"])
            )
            conn.execute(
                """
                INSERT INTO thesis_signal_daily (
                    date, thesis_id, thesis_score, thesis_trend,
                    evidence_support_score, evidence_contradiction_score,
                    macro_confirmation_score, flow_confirmation_score, price_confirmation_score,
                    risk_score, recommended_action, position_multiplier, reason_summary, created_at
                ) VALUES (
                    :date, :thesis_id, :thesis_score, :thesis_trend,
                    :evidence_support_score, :evidence_contradiction_score,
                    :macro_confirmation_score, :flow_confirmation_score, :price_confirmation_score,
                    :risk_score, :recommended_action, :position_multiplier, :reason_summary, :created_at
                )
                ON CONFLICT(date, thesis_id) DO UPDATE SET
                    thesis_score=excluded.thesis_score,
                    thesis_trend=excluded.thesis_trend,
                    evidence_support_score=excluded.evidence_support_score,
                    evidence_contradiction_score=excluded.evidence_contradiction_score,
                    macro_confirmation_score=excluded.macro_confirmation_score,
                    flow_confirmation_score=excluded.flow_confirmation_score,
                    price_confirmation_score=excluded.price_confirmation_score,
                    risk_score=excluded.risk_score,
                    recommended_action=excluded.recommended_action,
                    position_multiplier=excluded.position_multiplier,
                    reason_summary=excluded.reason_summary,
                    created_at=excluded.created_at;
                """,
                {
                    "date": date,
                    "thesis_id": tid,
                    "thesis_score": result["thesis_score"],
                    "thesis_trend": result["thesis_trend"],
                    "evidence_support_score": evidence_support_score,
                    "evidence_contradiction_score": evidence_contradiction_score,
                    "macro_confirmation_score": confirmations["macro_confirmation_score"],
                    "flow_confirmation_score": confirmations["flow_confirmation_score"],
                    "price_confirmation_score": confirmations["price_confirmation_score"],
                    "risk_score": confirmations["risk_score"],
                    "recommended_action": result["recommended_action"],
                    "position_multiplier": result["position_multiplier"],
                    "reason_summary": reason,
                    "created_at": now,
                },
            )
            changed += 1
        return changed


@dataclass(frozen=True)
class StockDecisionInput:
    market_permission_score: float
    thesis_alignment_score: float
    fundamental_score: float
    flow_confirmation_score: float
    price_confirmation_score: float
    valuation_adjustment: float


def calculate_stock_decision(values: StockDecisionInput, *, market_regime: str) -> dict[str, Any]:
    final = clamp(
        values.market_permission_score * 0.20
        + values.thesis_alignment_score * 0.25
        + values.fundamental_score * 0.20
        + values.flow_confirmation_score * 0.15
        + values.price_confirmation_score * 0.10
        + values.valuation_adjustment * 0.10,
        0,
        100,
    )
    action = recommended_action_from_score((final - 50) * 2, regime=market_regime, has_price_flow_confirmation=True)
    return {
        "final_decision_score": round(final, 1),
        "status": ACTION_LABELS[action],
        "recommended_action": action,
    }
