from __future__ import annotations

from datetime import date

from committee.core.database import (
    safe_upsert_daily_macro,
    safe_upsert_domestic_policy_rate_daily,
    safe_upsert_market_daily,
    safe_upsert_market_flow_daily,
    safe_upsert_monthly_macro,
    safe_upsert_quarterly_macro,
)
from committee.schemas.snapshot import Snapshot
from committee.tools.bok_policy_rate_provider import check_bok_base_rate


def persist_snapshot_metrics(
    snapshot: Snapshot,
    market_date: date,
    status: dict[str, str],
) -> None:
    """Persist snapshot-derived metrics into DB (best-effort upsert)."""
    kospi_pct_db = snapshot.markets.kr.kospi_pct if status.get("kospi") == "OK" else None
    kosdaq_pct_db = snapshot.markets.kr.kosdaq_pct if status.get("kosdaq") == "OK" else None
    sp500_pct_db = snapshot.markets.us.sp500_pct if status.get("sp500") == "OK" else None
    nasdaq_pct_db = snapshot.markets.us.nasdaq_pct if status.get("nasdaq") == "OK" else None
    dow_pct_db = snapshot.markets.us.dow_pct if status.get("dow") == "OK" else None
    kospi_db = snapshot.markets.kr.kospi if status.get("kospi") == "OK" else None
    kosdaq_db = snapshot.markets.kr.kosdaq if status.get("kosdaq") == "OK" else None
    sp500_db = snapshot.markets.us.sp500 if status.get("sp500") == "OK" else None
    nasdaq_db = snapshot.markets.us.nasdaq if status.get("nasdaq") == "OK" else None
    dow_db = snapshot.markets.us.dow if status.get("dow") == "OK" else None
    usdkrw_db = snapshot.markets.fx.usdkrw if status.get("usdkrw") == "OK" else None
    usdkrw_pct_db = snapshot.markets.fx.usdkrw_pct if status.get("usdkrw_pct") == "OK" else None
    us10y_db = (
        float(snapshot.macro.daily.us10y)
        if snapshot.macro is not None and snapshot.macro.daily.us10y is not None
        else None
    )
    vix_db = snapshot.markets.volatility.vix if status.get("vix") == "OK" else None
    safe_upsert_market_daily(
        date=market_date.isoformat(),
        kospi_pct=kospi_pct_db,
        kosdaq_pct=kosdaq_pct_db,
        sp500_pct=sp500_pct_db,
        nasdaq_pct=nasdaq_pct_db,
        dow_pct=dow_pct_db,
        kospi=kospi_db,
        kosdaq=kosdaq_db,
        sp500=sp500_db,
        nasdaq=nasdaq_db,
        dow=dow_db,
        usdkrw=usdkrw_db,
        usdkrw_pct=usdkrw_pct_db,
        us10y=us10y_db,
        vix=vix_db,
    )
    foreign_net_db = snapshot.flow_summary.foreign_net if status.get("flows") == "OK" else None
    institution_net_db = snapshot.flow_summary.institution_net if status.get("flows") == "OK" else None
    retail_net_db = snapshot.flow_summary.retail_net if status.get("flows") == "OK" else None
    # KOSPI 단독 수급 (korean_market_flow.market["KOSPI"])
    kospi_f_db: float | None = None
    kospi_i_db: float | None = None
    kospi_r_db: float | None = None
    if status.get("flows") == "OK" and snapshot.korean_market_flow is not None:
        _kospi = snapshot.korean_market_flow.market.get("KOSPI")
        if _kospi is not None:
            kospi_f_db = float(_kospi.foreign)
            kospi_i_db = float(_kospi.institution)
            kospi_r_db = float(_kospi.individual)
    safe_upsert_market_flow_daily(
        date=market_date.isoformat(),
        foreign_net=foreign_net_db,
        institution_net=institution_net_db,
        retail_net=retail_net_db,
        kospi_foreign_net=kospi_f_db,
        kospi_institution_net=kospi_i_db,
        kospi_retail_net=kospi_r_db,
    )
    rate_check = check_bok_base_rate(market_date=market_date)
    domestic_base_rate = rate_check.value
    safe_upsert_domestic_policy_rate_daily(
        date=market_date.isoformat(),
        base_rate=domestic_base_rate,
        source="BOK_ECOS_722Y001_D_0101000",
    )
    if rate_check.status == "ok":
        print(f"[ecos] domestic base rate ok: {domestic_base_rate:.2f}% ({market_date.isoformat()})")
    else:
        print(f"[ecos] domestic base rate check failed: {rate_check.status} ({rate_check.message})")

    if snapshot.macro is None:
        return

    d = snapshot.macro.daily
    m = snapshot.macro.monthly
    q = snapshot.macro.quarterly
    s = snapshot.macro.structural

    safe_upsert_daily_macro(
        date=market_date.isoformat(),
        us10y=d.us10y,
        us2y=d.us2y,
        spread_2_10=d.spread_2_10,
        us_3m_yield=d.us_3m_yield,
        us_2y_yield=d.us_2y_yield,
        us_10y_yield=d.us_10y_yield,
        spread_10y_2y=d.spread_10y_2y,
        spread_10y_3m=d.spread_10y_3m,
        vix=d.vix,
        dxy=d.dxy,
        usdkrw=d.usdkrw,
        fed_funds_rate=s.fed_funds_rate,
        real_rate=s.real_rate,
        vix3m=d.vix3m,
        vix_term_spread=d.vix_term_spread,
        oil_wti=d.oil_wti,
        hy_oas=s.hy_oas,
        ig_oas=s.ig_oas,
        fed_balance_sheet=s.fed_balance_sheet,
        russell2000=d.russell2000,
        oil_brent=d.oil_brent,
        tga_balance=s.tga_balance,
        boj_rate=s.boj_rate,
    )
    safe_upsert_monthly_macro(
        date=market_date.isoformat(),
        unemployment_rate=m.unemployment_rate,
        cpi_yoy=m.cpi_yoy,
        core_cpi_yoy=m.core_cpi_yoy,
        pce_yoy=m.pce_yoy,
        pmi=m.pmi,
        retail_sales_mom=m.retail_sales_mom,
        nfp_change=m.nfp_change,
        wage_level=m.wage_level,
        wage_yoy=m.wage_yoy,
        export_yoy=m.export_yoy,
    )
    safe_upsert_quarterly_macro(
        date=market_date.isoformat(),
        real_gdp=q.real_gdp,
        gdp_qoq_annualized=q.gdp_qoq_annualized,
    )
