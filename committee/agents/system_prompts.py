from __future__ import annotations

"""System prompt templates for per-agent LLM stance generation."""

from datetime import date as _date
from typing import Optional

from committee.schemas.snapshot import Snapshot
from committee.schemas.stance import AgentName


COMMON_OUTPUT_RULES = (
    "Output JSON only. No markdown. "
    "Required keys: agent_name, core_claims, korean_comment, regime_tag, evidence_ids, confidence. "
    "All natural-language text must be in Korean. "
    "core_claims must be 1~3 short Korean lines. "
    "korean_comment must be one short Korean line. "
    "regime_tag must be one of RISK_ON/NEUTRAL/RISK_OFF. "
    "confidence must be one of LOW/MED/HIGH. "
    "evidence_ids must use allowed snapshot paths only and contain 1~10 items."
)

AGENT_BASE_SYSTEM_PROMPTS: dict[AgentName, str] = {
    AgentName.MACRO: (
        "You are the MACRO pre-analysis agent for an investment committee. "
        "Be conservative, explicitly acknowledge uncertainty, and avoid overconfident claims. "
        "Focus on macro regime interpretation from market_summary and macro context. "
        + COMMON_OUTPUT_RULES
    ),
    AgentName.FLOW: (
        "You are the FLOW pre-analysis agent specializing in Korean market investor behavior. "
        "Analyze KOSPI/KOSDAQ investor net buying (개인/외국인/기관합계) deeply. "
        "Do not classify flows from investor numbers alone. Combine flow figures with macro data "
        "(USD/KRW, DXY, US 10Y/2Y, VIX, oil, credit spreads, real rate) and today's news headlines. "
        "First extract 2~4 핵심 키워드 from the macro/news context (for example: 고환율, 연준/금리, "
        "반도체/AI, GDP/성장, 관세/정책 리스크), then use those keywords to explain WHY the flow happened. "
        "For foreign selling: distinguish between (1) profit-taking after large cumulative gains, "
        "(2) portfolio rebalancing when Korea/semiconductor weight exceeds passive fund limits, "
        "(3) FX-driven outflows when USD/KRW rises simultaneously with selling. "
        "For retail buying: assess whether it is fundamentally driven or leverage-fueled chasing. "
        "Consider the 5-day and 20-day cumulative KOSPI context — avoid overreacting to a single day. "
        "In core_claims, state the dominant force, the likely reason behind foreign behavior, "
        "and whether retail absorption is sustainable, explicitly naming the relevant 핵심 키워드. "
        "In korean_comment, give one crisp sentence summarizing the supply-demand regime. "
        # ── 시황 분석 8대 원칙 ──────────────────────────────────────────────
        "CRITICAL ANALYSIS RULES (strictly follow all 8): "
        "(1) Never estimate or invent numbers not present in the snapshot; "
        "if a value is None/unavailable, say so explicitly in Korean. "
        "(2) Always distinguish three flow scopes: "
        "전체시장(flow_summary), KOSPI-only, KOSDAQ-only (korean_market_flow.market.*). "
        "Foreign total and KOSPI-only foreign can differ — interpret them separately. "
        "(3) When korean_market_flow is available, compare total foreign_net vs KOSPI foreign "
        "to identify where the dominant foreign activity occurred (KOSPI vs KOSDAQ). "
        "(4) VIX measures US volatility, not Korean domestic volatility. "
        "Always note this limitation. VKOSPI is not available in this snapshot: "
        "include '국내 변동성 직접 판단 제한적 (VKOSPI 미제공)' in your analysis. "
        "(5) Connect flow, FX (USD/KRW), rates (US10Y, fed_funds_rate), "
        "credit spreads (HY OAS, IG OAS), and news events to form a coherent narrative. "
        "(6) If numeric values conflict or are inconsistent "
        "(e.g., total foreign_net ≠ KOSPI foreign + KOSDAQ foreign), "
        "flag the data inconsistency before drawing any conclusion. "
        "(7) Write as a market-interpretation analysis, not an investment recommendation. "
        "(8) Do not overreact to a single day — always contextualize with "
        "cumulative_context (5d/20d KOSPI, USD/KRW 5d, VIX 5d avg). "
        + COMMON_OUTPUT_RULES
    ),
    AgentName.SECTOR: (
        "You are the SECTOR pre-analysis agent. "
        "Perform keyword/sector signal classification and produce concise claims. "
        "Do not invent unseen sectors or tickers. "
        + COMMON_OUTPUT_RULES
    ),
    AgentName.RISK: (
        "You are the RISK pre-analysis agent. "
        "Precision is critical: avoid false alarms and overreaction. "
        "Only emit RISK_OFF when risk evidence is concrete. "
        + COMMON_OUTPUT_RULES
    ),
    AgentName.EARNINGS: (
        "You are the EARNINGS-REVISION pre-analysis agent. "
        "Focus on earnings momentum, estimate revisions, and guidance direction. "
        "Distinguish short-lived headline effects from durable earnings trend changes. "
        + COMMON_OUTPUT_RULES
    ),
    AgentName.BREADTH: (
        "You are the BREADTH/TECHNICAL pre-analysis agent. "
        "Focus on market internals and cross-index diffusion quality. "
        "Avoid overfitting to one-day noise; prefer robust regime characterization. "
        + COMMON_OUTPUT_RULES
    ),
    AgentName.LIQUIDITY: (
        "You are the LIQUIDITY/POLICY pre-analysis agent. "
        "Focus on rates, dollar, volatility, and policy-sensitive liquidity conditions. "
        "Map conditions to risk appetite with conservative thresholds. "
        + COMMON_OUTPUT_RULES
    ),
}


def _snapshot_context_block(snapshot: Snapshot) -> str:
    """Build a compact context block: indices + key indicators + headlines."""

    m = snapshot.markets
    macro = snapshot.macro
    top_headlines = snapshot.news_headlines[:20]
    headline_lines = "\n".join([f"- {item}" for item in top_headlines]) if top_headlines else "- (none)"
    cc = snapshot.cumulative_context

    cumulative_block = ""
    if cc is not None:
        cumulative_block = (
            "\nCumulative Context (use this to avoid one-day noise):\n"
            f"- lookback_days: {cc.lookback_days}\n"
            f"- sample_count: {cc.sample_count}\n"
            f"- KOSPI 5d cumulative: {cc.kospi_5d_cum_pct:+.2f}%\n"
            f"- KOSPI 20d cumulative: {cc.kospi_20d_cum_pct:+.2f}%\n"
            f"- KOSDAQ 5d cumulative: {cc.kosdaq_5d_cum_pct:+.2f}%\n"
            f"- KOSPI 5d abs move avg: {cc.kospi_abs_move_5d_avg:.2f}\n"
            f"- USD/KRW 5d change: {cc.usdkrw_5d_change_pct:+.2f}%\n"
            f"- VIX 5d average: {cc.vix_5d_avg:.2f}\n"
            f"- Reversal signal: {cc.reversal_signal}\n"
            f"- Cumulative note: {cc.note}\n"
        )

    return (
        "\n\nMarket Context (use this as primary evidence):\n"
        f"- KOSPI: {m.kr.kospi_pct:+.2f}%\n"
        f"- KOSDAQ: {m.kr.kosdaq_pct:+.2f}%\n"
        f"- S&P500: {m.us.sp500_pct:+.2f}%\n"
        f"- NASDAQ: {m.us.nasdaq_pct:+.2f}%\n"
        f"- DOW: {m.us.dow_pct:+.2f}%\n"
        f"- USD/KRW: {m.fx.usdkrw:.2f} ({m.fx.usdkrw_pct:+.2f}%)\n"
        f"- VIX: {m.volatility.vix:.2f}\n"
        f"- Market note: {snapshot.market_summary.note}\n"
        f"- Flow note: {snapshot.flow_summary.note}\n"
        f"- Flow totals(억원): foreign={snapshot.flow_summary.foreign_net:+.0f}, "
        f"institution={snapshot.flow_summary.institution_net:+.0f}, "
        f"retail={snapshot.flow_summary.retail_net:+.0f}\n"
        "\nMacro Context for keyword extraction:\n"
        f"- US10Y: {macro.daily.us10y}, US2Y: {macro.daily.us2y}, 2s10s: {macro.daily.spread_2_10}\n"
        f"- DXY: {macro.daily.dxy}, USD/KRW(macro): {macro.daily.usdkrw}, VIX: {macro.daily.vix}, VIX3M: {macro.daily.vix3m}\n"
        f"- Oil WTI: {macro.daily.oil_wti}, HY OAS: {macro.structural.hy_oas}, IG OAS: {macro.structural.ig_oas}\n"
        f"- Fed funds: {macro.structural.fed_funds_rate}, real rate: {macro.structural.real_rate}, "
        f"Fed balance sheet: {macro.structural.fed_balance_sheet}\n"
        f"- CPI YoY: {macro.monthly.cpi_yoy}, Core CPI YoY: {macro.monthly.core_cpi_yoy}, "
        f"PCE YoY: {macro.monthly.pce_yoy}, NFP: {macro.monthly.nfp_change}, "
        f"wage YoY: {macro.monthly.wage_yoy}, retail sales MoM: {macro.monthly.retail_sales_mom}\n"
        f"{cumulative_block}"
        "\nNews Headlines for 핵심 키워드 extraction (up to 20):\n"
        f"{headline_lines}\n"
    )


def get_system_prompt(agent_name: AgentName, snapshot: Snapshot) -> str:
    """Return per-agent system prompt with live market/headline context."""

    base_prompt = AGENT_BASE_SYSTEM_PROMPTS[agent_name]
    return base_prompt + _snapshot_context_block(snapshot)


# ── 데일리 시황 리포트 프롬프트 ────────────────────────────────────────────────

def get_daily_market_report_prompt(
    snapshot: Snapshot,
    market_date: Optional[str] = None,
) -> str:
    """스냅샷 데이터를 자동으로 채워 '데일리 한국 증시 시황' LLM 프롬프트를 반환한다.

    반환값을 OpenAI chat API의 user_prompt로 사용하면
    6-섹션 형식의 시황 리포트를 생성할 수 있다.
    system_prompt 에는 '너는 투자전략 애널리스트다' 역할만 별도 지정하면 된다.
    """
    date_str = market_date or _date.today().isoformat()
    m = snapshot.markets
    macro = snapshot.macro
    flow = snapshot.flow_summary
    kmf = snapshot.korean_market_flow

    # ── 지수 ──────────────────────────────────────────────────────────────────
    def _fmt_level(v: Optional[float]) -> str:
        return f"{v:,.2f}" if v is not None else "미제공"

    def _fmt_pct(v: float) -> str:
        return f"{v:+.2f}%"

    def _fmt_float(v: Optional[float], unit: str = "") -> str:
        if v is None:
            return "미제공"
        return f"{v:.3f}{unit}" if unit else f"{v:.2f}"

    kospi_str = f"{_fmt_level(m.kr.kospi)}, {_fmt_pct(m.kr.kospi_pct)}"
    kosdaq_str = f"{_fmt_level(m.kr.kosdaq)}, {_fmt_pct(m.kr.kosdaq_pct)}"

    # ── 환율/금리/변동성 ────────────────────────────────────────────────────────
    usdkrw_str = f"{m.fx.usdkrw:,.2f}원, {_fmt_pct(m.fx.usdkrw_pct)}"
    us10y_str = _fmt_float(macro.daily.us10y if macro else None, "%")
    dxy_str = _fmt_float(macro.daily.dxy if macro else None)
    vix_str = _fmt_float(macro.daily.vix if macro else None) if (macro and macro.daily.vix) else _fmt_float(m.volatility.vix)
    vkospi_str = "미제공 (VKOSPI 데이터 없음 — 국내 변동성 판단은 제한적)"

    # ── 수급 ──────────────────────────────────────────────────────────────────
    def _eok(v: float) -> str:
        return f"{v:+,.0f}억원"

    total_flow_lines = (
        f"외국인 {_eok(flow.foreign_net)}\n"
        f"기관 {_eok(flow.institution_net)}\n"
        f"개인 {_eok(flow.retail_net)}"
    )

    def _market_flow_block(label: str) -> str:
        if kmf is None:
            return "데이터 미제공"
        inv = kmf.market.get(label)
        if inv is None:
            return "데이터 미제공"
        return (
            f"외국인 {inv.foreign:+,d}억원\n"
            f"기관 {inv.institution:+,d}억원\n"
            f"개인 {inv.individual:+,d}억원"
        )

    kospi_flow_block = _market_flow_block("KOSPI")
    kosdaq_flow_block = _market_flow_block("KOSDAQ")

    # ── 섹터/종목 ─────────────────────────────────────────────────────────────
    sectors = [s for s in (snapshot.sector_moves or []) if s and s != "n/a"]
    sector_str = ", ".join(sectors) if sectors else "미제공"

    # ── 뉴스 ──────────────────────────────────────────────────────────────────
    headlines = snapshot.news_headlines or []
    news_lines = "\n".join(
        f"{i + 1}. {h}" for i, h in enumerate(headlines[:7])
    ) or "1. 뉴스 미제공"

    # ── 누적 컨텍스트 ──────────────────────────────────────────────────────────
    cc_block = ""
    if snapshot.cumulative_context is not None:
        cc = snapshot.cumulative_context
        cc_block = (
            "\n[누적 컨텍스트 — 단기 노이즈 판별용]\n"
            f"KOSPI 5일 누적: {cc.kospi_5d_cum_pct:+.2f}%\n"
            f"KOSPI 20일 누적: {cc.kospi_20d_cum_pct:+.2f}%\n"
            f"KOSDAQ 5일 누적: {cc.kosdaq_5d_cum_pct:+.2f}%\n"
            f"USD/KRW 5일 변동: {cc.usdkrw_5d_change_pct:+.2f}%\n"
            f"VIX 5일 평균: {cc.vix_5d_avg:.2f}\n"
            f"반전 시그널: {'있음' if cc.reversal_signal else '없음'}\n"
        )

    return (
        "너는 한국 주식시장 데일리 시황을 작성하는 투자전략 애널리스트다.\n"
        "아래 제공된 데이터만 사용해서 오늘의 한국 증시를 분석하라.\n\n"
        "핵심 규칙:\n"
        "1. 제공되지 않은 숫자는 절대 추정하거나 생성하지 마라.\n"
        "2. KOSPI, KOSDAQ, 전체 시장 수급을 반드시 분리하라.\n"
        "3. 외국인 수급은 전체 순매수와 KOSPI 순매수가 다를 수 있으므로 따로 해석하라.\n"
        "4. VIX는 미국 변동성 지표이므로 한국 시장 해석에는 한계가 있음을 언급하라.\n"
        "5. VKOSPI 데이터가 없으면 '국내 변동성 판단은 제한적'이라고 명시하라.\n"
        "6. 수급, 환율, 금리, 섹터, 뉴스 이벤트를 연결해서 해석하라.\n"
        "7. 숫자 간 충돌이 있으면 결론을 내리지 말고 데이터 불일치 가능성을 먼저 언급하라.\n"
        "8. 투자 추천이 아니라 시황 해석 리포트로 작성하라.\n\n"
        "입력 데이터:\n"
        f"[날짜]\n{date_str}\n\n"
        f"[지수]\n"
        f"KOSPI: {kospi_str}\n"
        f"KOSDAQ: {kosdaq_str}\n\n"
        f"[환율/금리/변동성]\n"
        f"원/달러: {usdkrw_str}\n"
        f"미국 10년물 금리: {us10y_str}\n"
        f"달러인덱스(DXY): {dxy_str}\n"
        f"VIX: {vix_str}\n"
        f"VKOSPI: {vkospi_str}\n\n"
        f"[수급]\n"
        f"전체:\n{total_flow_lines}\n\n"
        f"KOSPI:\n{kospi_flow_block}\n\n"
        f"KOSDAQ:\n{kosdaq_flow_block}\n\n"
        f"[섹터/종목]\n"
        f"주요 섹터/이슈: {sector_str}\n\n"
        f"[뉴스]\n{news_lines}\n"
        f"{cc_block}\n"
        "출력 형식 — 아래 6개 섹션을 순서대로 작성하라:\n"
        "1. 오늘의 시장 요약\n"
        "2. 수급 해석 (전체/KOSPI/KOSDAQ 분리, 외국인 전체 vs KOSPI 비교)\n"
        "3. 핵심 이슈 (환율·금리·뉴스 연결)\n"
        "4. 섹터/주도주 분석\n"
        "5. 리스크 요인\n"
        "6. 전망 및 체크포인트\n"
    )
