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
    cycle_model_config,
    cycle_repository,
    industry_ai_opinion,
    industry_news,
    insight_repository,
    repository,
)
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


def _load_industries(as_of: str, model_version: str) -> list[dict[str, object]]:
    result: list[dict[str, object]] = []
    for industry in repository.list_industries(active_only=True, db_path=DB_PATH):
        signal = cycle_repository.get_cycle_signal(
            str(industry["industry_id"]), as_of, model_version, db_path=DB_PATH
        )
        result.append({**industry, "latest_signal": signal})
    return result


def main() -> None:
    args = _parse_args()
    cfg = cycle_model_config.load_cycle_model_config()
    model_version = str(cfg["model_version"])
    industries = _load_industries(args.as_of, model_version)
    print(
        f"industry_weekly_insights_plan as_of={args.as_of} industries={len(industries)} "
        f"lookback_days={args.lookback_days} model={args.model} execute={args.execute}"
    )
    if not args.execute:
        print("industry_weekly_insights_dry_run_only (no network or DB writes)")
        return
    if not industries:
        print("industry_weekly_insights_no_signals")
        return

    collection = industry_news.collect_and_store_industry_news(
        industries,
        lookback_days=args.lookback_days,
        limit_per_industry=args.news_limit,
        dry_run=False,
        db_path=DB_PATH,
    )
    print(f"industry_news_collected counts={collection['counts']} errors={collection['errors']}")
    if args.skip_llm:
        print("industry_weekly_insights_done news_only=true")
        return

    since = (
        datetime.fromisoformat(args.as_of)
        .replace(tzinfo=timezone.utc)
        - timedelta(days=max(1, args.lookback_days))
    ).isoformat()
    llm_industries: list[dict[str, object]] = []
    for item in industries:
        industry_id = str(item["industry_id"])
        llm_industries.append(
            {
                **item,
                "news": insight_repository.list_industry_news(
                    industry_id,
                    published_since=since,
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
