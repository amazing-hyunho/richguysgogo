from __future__ import annotations

# Core daily pipeline orchestration.

from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import List

from committee.core.report_renderer import Report, build_report, render_report
from committee.core.database import (
    safe_upsert_daily_macro,
    safe_upsert_market_daily,
    safe_upsert_market_flow_daily,
    safe_upsert_monthly_macro,
    safe_upsert_quarterly_macro,
)
from committee.core.storage import save_run
from committee.core.snapshot_builder import build_snapshot, get_last_snapshot_status
from committee.schemas.committee_result import (
    CommitteeResult,
    Disagreement,
    OpsGuidance,
    OpsGuidanceLevel,
)
from committee.schemas.stance import AgentName, ConfidenceLevel, RegimeTag, Stance


def run_pre_analysis(snapshot: object, agent_ids: List[str]) -> List[Stance]:
    """Generate stub stances for configured agent IDs."""
    stances: List[Stance] = []
    for agent_id in agent_ids:
        stances.append(
            Stance(
                agent_name=AgentName(agent_id),
                core_claims=[
                    f"{agent_id} sees balanced risk.",
                    "Liquidity is stable.",
                ],
                regime_tag=RegimeTag.NEUTRAL,
                evidence_ids=["snapshot.market_summary.note", "snapshot.flow_summary.note"],
                confidence=ConfidenceLevel.MED,
            )
        )
    return stances


def run_committee(snapshot: object, stances: List[Stance]) -> CommitteeResult:
    """Generate a stub committee result from stances."""
    key_points = _build_key_points(stances, None)
    return CommitteeResult(
        consensus="Committee agrees on a neutral stance with selective monitoring.",
        key_points=key_points,
        disagreements=[
            Disagreement(
                topic="Regime tags",
                majority=RegimeTag.NEUTRAL.value,
                minority="None",
                minority_agents=["none"],
                why_it_matters="No dissenting regime tags are present.",
            )
        ],
        ops_guidance=[
            OpsGuidance(level=OpsGuidanceLevel.OK, text="Keep watchlist tight and avoid overexposure."),
            OpsGuidance(level=OpsGuidanceLevel.CAUTION, text="Keep position sizes moderate."),
            OpsGuidance(level=OpsGuidanceLevel.AVOID, text="Avoid aggressive leverage."),
        ],
    )


def _build_key_points(stances: List[Stance], majority_tag: RegimeTag | None) -> list[dict]:
    if not stances:
        return [{"point": "No stances provided.", "sources": ["none"]}]

    tag_to_agents: dict[RegimeTag, list[str]] = {
        RegimeTag.RISK_ON: [],
        RegimeTag.NEUTRAL: [],
        RegimeTag.RISK_OFF: [],
    }
    for stance in stances:
        tag_to_agents[stance.regime_tag].append(stance.agent_name.value)

    if majority_tag is None:
        majority_tag = max(tag_to_agents, key=lambda tag: len(tag_to_agents[tag]))
    return [
        {
            "point": f"Majority regime tag: {majority_tag.value}.",
            "sources": tag_to_agents[majority_tag][:5] or ["unknown"],
        }
    ]


@dataclass(frozen=True)
class DailyPipeline:
    """Pipeline runner for daily snapshot-to-report flow."""
    agent_ids: List[str]

    def run(self, market_date: date, output_dir: Path) -> Report:
        """Run the full pipeline and write the report."""
        snapshot = build_snapshot(market_date)
        status = get_last_snapshot_status()
        # DB persistence layer (additive): best-effort upsert.
        # Must not break the existing pipeline even if DB is unavailable/locked.
        # Data integrity: use NULL (not 0.0) for missing/unavailable/not-implemented values.
        usdkrw_pct_db = snapshot.markets.fx.usdkrw_pct if status.get("usdkrw_pct") == "OK" else None
        # Not implemented yet: explicitly store NULL rather than 0.0 placeholders.
        us10y_db = None
        vix_db = snapshot.markets.volatility.vix if status.get("vix") == "OK" else None
        safe_upsert_market_daily(
            date=market_date.isoformat(),
            kospi_pct=snapshot.markets.kr.kospi_pct,
            kosdaq_pct=snapshot.markets.kr.kosdaq_pct,
            sp500_pct=snapshot.markets.us.sp500_pct,
            nasdaq_pct=snapshot.markets.us.nasdaq_pct,
            dow_pct=snapshot.markets.us.dow_pct,
            usdkrw=snapshot.markets.fx.usdkrw,
            usdkrw_pct=usdkrw_pct_db,
            us10y=us10y_db,
            vix=vix_db,
        )
        foreign_net_db = snapshot.flow_summary.foreign_net if status.get("flows") == "OK" else None
        safe_upsert_market_flow_daily(
            date=market_date.isoformat(),
            foreign_net=foreign_net_db,
        )

        # Macro engine persistence (additive). Values are Optional in snapshot.macro and map to NULL in DB.
        if snapshot.macro is not None:
            d = snapshot.macro.daily
            m = snapshot.macro.monthly
            q = snapshot.macro.quarterly
            s = snapshot.macro.structural

            safe_upsert_daily_macro(
                date=market_date.isoformat(),
                us10y=d.us10y,
                us2y=d.us2y,
                spread_2_10=d.spread_2_10,
                vix=d.vix,
                dxy=d.dxy,
                usdkrw=d.usdkrw,
                fed_funds_rate=s.fed_funds_rate,
                real_rate=s.real_rate,
            )
            safe_upsert_monthly_macro(
                date=market_date.isoformat(),
                unemployment_rate=m.unemployment_rate,
                cpi_yoy=m.cpi_yoy,
                core_cpi_yoy=m.core_cpi_yoy,
                pce_yoy=m.pce_yoy,
                pmi=m.pmi,
                wage_level=m.wage_level,
                wage_yoy=m.wage_yoy,
            )
            safe_upsert_quarterly_macro(
                date=market_date.isoformat(),
                real_gdp=q.real_gdp,
                gdp_qoq_annualized=q.gdp_qoq_annualized,
            )
        stances = run_pre_analysis(snapshot, self.agent_ids)
        committee_result = run_committee(snapshot, stances)

        report = build_report(
            market_date=market_date.isoformat(),
            snapshot=snapshot,
            stances=stances,
            committee_result=committee_result,
        )

        output_path = output_dir / f"{market_date.isoformat()}.json"
        render_report(report, output_path)
        save_run(output_dir, market_date, snapshot, stances, committee_result, report)
        return report
