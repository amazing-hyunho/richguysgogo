from __future__ import annotations

"""Collect industry news and generate one cross-industry weekly AI opinion."""

import argparse
from datetime import date, datetime, timedelta, timezone
import os
from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from committee.industry_cycle import (
    candidate_repository,
    cycle_model_config,
    cycle_repository,
    industry_ai_opinion,
    industry_news,
    insight_repository,
    repository,
    stock_model_config,
    virtual_portfolio_repository,
)
from committee.core.env_loader import load_project_env
from committee.tools.openai_chat import load_openai_config

DB_PATH = ROOT_DIR / "data" / "investment.db"


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="주간 산업 뉴스 수집 및 전체 산업 AI 종합의견 생성")
    parser.add_argument("--as-of", default=date.today().isoformat())
    parser.add_argument("--lookback-days", type=int, default=14)
    parser.add_argument("--news-limit", type=int, default=8)
    parser.add_argument("--model", default=os.getenv("INDUSTRY_LLM_MODEL", "gpt-4.1"))
    parser.add_argument("--skip-llm", action="store_true", help="뉴스만 수집하고 LLM 의견은 생성하지 않음")
    parser.add_argument("--execute", action="store_true", help="네트워크 호출 및 DB 저장 실행")
    return parser.parse_args()


def _compact_portfolio(
    positions: list[dict[str, object]], *, as_of: str
) -> dict[str, object]:
    open_position = next((p for p in reversed(positions) if p.get("status") == "OPEN"), None)
    weekly_events: list[dict[str, object]] = []
    for position in positions:
        if position.get("entry_as_of") == as_of:
            weekly_events.append(
                {
                    "action": "opened",
                    "asset_id": position.get("asset_id"),
                    "entry_state": position.get("entry_state"),
                }
            )
        if position.get("exit_as_of") == as_of:
            weekly_events.append(
                {
                    "action": "closed",
                    "asset_id": position.get("asset_id"),
                    "exit_reason": position.get("exit_reason"),
                }
            )
    return {
        "status": "OPEN" if open_position else "NONE",
        "asset_id": open_position.get("asset_id") if open_position else None,
        "entry_as_of": open_position.get("entry_as_of") if open_position else None,
        "weekly_events": weekly_events,
    }


def _load_analysis_industries(
    as_of: str,
    cycle_model_version: str,
    candidate_model_version: str,
) -> list[dict[str, object]]:
    """Load only industries with a successfully persisted signal for this week."""
    active = {
        str(industry["industry_id"]): industry
        for industry in repository.list_industries(active_only=True, db_path=DB_PATH)
    }
    signals = cycle_repository.list_cycle_signals(
        as_of=as_of, model_version=cycle_model_version, db_path=DB_PATH
    )
    result: list[dict[str, object]] = []
    for signal in signals:
        industry_id = str(signal["industry_id"])
        industry = active.get(industry_id)
        if industry is None:
            continue
        previous_signal = cycle_repository.get_latest_cycle_signal_before(
            industry_id, cycle_model_version, as_of, db_path=DB_PATH
        )
        reasons = cycle_repository.list_signal_reasons(
            industry_id, as_of, cycle_model_version, db_path=DB_PATH
        )
        candidates = candidate_repository.list_industry_candidates(
            industry_id,
            as_of,
            candidate_model_version,
            include_excluded=False,
            db_path=DB_PATH,
        )
        positions = virtual_portfolio_repository.list_positions(
            industry_id=industry_id,
            model_version=cycle_model_version,
            db_path=DB_PATH,
        )
        result.append(
            {
                **industry,
                "latest_signal": signal,
                "previous_signal": previous_signal,
                "signal_reasons": reasons,
                "candidates": candidates[:3],
                "portfolio": _compact_portfolio(positions, as_of=as_of),
            }
        )
    return result


def main() -> None:
    load_project_env(ROOT_DIR)
    args = _parse_args()
    cfg = cycle_model_config.load_cycle_model_config()
    model_version = str(cfg["model_version"])
    candidate_model_version = str(
        stock_model_config.load_stock_model_config()["model_version"]
    )
    industries = repository.list_industries(active_only=True, db_path=DB_PATH)
    print(
        f"industry_weekly_insights_plan as_of={args.as_of} industries={len(industries)} "
        f"lookback_days={args.lookback_days} model={args.model} execute={args.execute}"
    )
    if not args.execute:
        print("industry_weekly_insights_dry_run_only (no network or DB writes)")
        return
    as_of_start = datetime.fromisoformat(args.as_of).replace(tzinfo=timezone.utc)
    collection_now = as_of_start + timedelta(days=1) - timedelta(microseconds=1)
    collection = industry_news.collect_and_store_industry_news(
        industries,
        lookback_days=args.lookback_days,
        limit_per_industry=args.news_limit,
        dry_run=False,
        now=collection_now,
        db_path=DB_PATH,
    )
    print(f"industry_news_collected counts={collection['counts']} errors={collection['errors']}")
    if args.skip_llm:
        print("industry_weekly_insights_done news_only=true")
        return

    analysis_industries = _load_analysis_industries(
        args.as_of, model_version, candidate_model_version
    )
    if not analysis_industries:
        print("industry_weekly_insights_no_signals_for_as_of")
        return

    since = (as_of_start - timedelta(days=max(1, args.lookback_days))).isoformat()
    before = (as_of_start + timedelta(days=1)).isoformat()
    llm_industries: list[dict[str, object]] = []
    for item in analysis_industries:
        industry_id = str(item["industry_id"])
        llm_industries.append(
            {
                **item,
                "news": insight_repository.list_industry_news(
                    industry_id,
                    published_since=since,
                    published_before=before,
                    limit=args.news_limit,
                    db_path=DB_PATH,
                ),
            }
        )

    try:
        batch = industry_ai_opinion.generate_industry_opinions(
            llm_industries,
            config=load_openai_config(),
            model=args.model,
        )
        stored = industry_ai_opinion.store_industry_opinions(
            batch,
            as_of=args.as_of,
            cycle_model_version=model_version,
            llm_model=args.model,
            db_path=DB_PATH,
        )
        print(f"industry_ai_opinions_stored={stored}")
    except Exception as exc:
        repository.record_data_quality_event(
            event_type="industry_ai_opinion_failed",
            target=args.as_of,
            severity="low",
            message=str(exc),
            db_path=DB_PATH,
        )
        print(f"industry_ai_opinion_failed={exc}")
    print("industry_weekly_insights_done")


if __name__ == "__main__":
    main()
