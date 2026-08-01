from __future__ import annotations

"""Reconstruct the full industry-cycle pipeline for a weekly historical range.

This runner intentionally reuses the production scoring functions in their
normal order for every historical ``as_of``:

1. price factors
2. industry fundamentals
3. earnings revision and industry breadth
4. final cycle signal

The source tables must be collected first. Price reads are point-in-time
gated by ``available_at`` and indicator reads by ``known_at``, so future data
is not exposed to an older weekly signal. News and AI commentary are excluded:
free RSS feeds cannot reliably reconstruct what was available in each past
week.
"""

import argparse
from datetime import date, timedelta
import json
from pathlib import Path
import sys
from typing import Any

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from committee.industry_cycle import (
    candidate_repository,
    cycle_model_config,
    cycle_runner,
    factor_repository,
    fundamentals_model_config,
    fundamentals_repository,
    fundamentals_scoring,
    indicator_catalog,
    industry_breadth_scoring,
    price_factor_runner,
    price_model_config,
    price_universe,
    repository,
    stock_model_config,
    taxonomy,
)
from committee.core.database import connect

DB_PATH = ROOT_DIR / "data" / "investment.db"
ASSETS_CONFIG_PATH = ROOT_DIR / "config" / "industry_etfs.json"


def generate_recent_weekly_dates(end_date: str, weeks: int, *, weekday: int = 4) -> list[str]:
    """Return exactly ``weeks`` weekly dates ending on/before ``end_date``.

    ``weekday`` follows ``datetime.date.weekday`` (Monday=0, Friday=4).
    """
    if weeks < 1:
        raise ValueError("weeks must be at least 1")
    if weekday < 0 or weekday > 6:
        raise ValueError("weekday must be between 0 and 6")
    end = date.fromisoformat(end_date)
    last = end - timedelta(days=(end.weekday() - weekday) % 7)
    first = last - timedelta(days=7 * (weeks - 1))
    return [(first + timedelta(days=7 * i)).isoformat() for i in range(weeks)]


def _is_valid_at(mapping: dict[str, Any], as_of: str) -> bool:
    valid_from = mapping.get("valid_from")
    valid_to = mapping.get("valid_to")
    return not ((valid_from and as_of < str(valid_from)) or (valid_to and as_of > str(valid_to)))


def _mapped_industries(payload: dict[str, Any], key: str, as_of: str) -> set[str]:
    return {
        str(row["industry_id"])
        for row in payload.get(key, [])
        if row.get("industry_id") and _is_valid_at(row, as_of)
    }


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Backfill full weekly industry-cycle history from point-in-time source data."
    )
    parser.add_argument("--weeks", type=int, default=54, help="Number of weekly observations. Default: 54.")
    parser.add_argument(
        "--end-date",
        default=date.today().isoformat(),
        help="Range endpoint (YYYY-MM-DD); aligned backward to --weekday.",
    )
    parser.add_argument(
        "--weekday",
        type=int,
        default=4,
        help="Weekly anchor: 0=Mon .. 6=Sun. Default: 4 (Friday).",
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Write the 4 pipeline stages. Without this flag, only print and validate the plan.",
    )
    parser.add_argument(
        "--reuse-price-factors",
        action="store_true",
        help=(
            "Reuse a week when every configured asset already has a production "
            "price-factor row; otherwise that week is recomputed."
        ),
    )
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    weekly_dates = generate_recent_weekly_dates(args.end_date, args.weeks, weekday=args.weekday)
    first_as_of = weekly_dates[0]
    last_as_of = weekly_dates[-1]

    taxonomy_payload = taxonomy.load_taxonomy()
    assets_payload = json.loads(ASSETS_CONFIG_PATH.read_text(encoding="utf-8"))
    indicators_payload = indicator_catalog.load_indicator_config()
    price_universe_payload = price_universe.load_price_universe()

    active_industries = sorted(
        str(row["industry_id"])
        for row in taxonomy_payload.get("industries", [])
        if row.get("active", True)
    )
    active_set = set(active_industries)
    asset_coverage = _mapped_industries(assets_payload, "mappings", first_as_of)
    indicator_coverage = _mapped_industries(
        indicators_payload, "industry_indicator_mappings", first_as_of
    )
    missing_assets = sorted(active_set - asset_coverage)
    missing_indicators = sorted(active_set - indicator_coverage)
    if missing_assets or missing_indicators:
        raise SystemExit(
            "historical_mapping_coverage_failed "
            f"as_of={first_as_of} missing_assets={missing_assets} "
            f"missing_indicators={missing_indicators}"
        )

    price_cfg = price_model_config.load_price_model_config()
    fundamentals_cfg = fundamentals_model_config.load_fundamentals_model_config()
    stock_cfg = stock_model_config.load_stock_model_config()
    cycle_cfg = cycle_model_config.load_cycle_model_config()
    price_targets = price_factor_runner.build_targets_from_universe(price_universe_payload)
    price_target_ids = {target.asset_id for target in price_targets}

    print(
        "backfill_industry_cycle_history_plan "
        f"weeks={len(weekly_dates)} range={first_as_of}..{last_as_of} "
        f"industries={len(active_industries)} price_targets={len(price_targets)} "
        f"reuse_price_factors={args.reuse_price_factors} execute={args.execute}"
    )
    print(
        "point_in_time_policy="
        "prices:available_at<=as_of,indicators:known_at<=as_of,"
        "news:excluded,current_representative_basket:reconstructed"
    )
    if not args.execute:
        print("backfill_industry_cycle_history_dry_run_only (pass --execute to write results)")
        return

    repository.sync_industry_master_from_config(taxonomy_payload, db_path=DB_PATH)
    repository.sync_industry_assets_from_config(assets_payload, db_path=DB_PATH)
    repository.sync_indicator_catalog_from_config(indicators_payload, db_path=DB_PATH)
    repository.sync_industry_indicator_map_from_config(indicators_payload, db_path=DB_PATH)

    with connect(DB_PATH) as conn:
        source_dates = conn.execute(
            """
            SELECT MIN(source_date) AS first_source_date
            FROM (
                SELECT SUBSTR(updated_at, 1, 10) AS source_date
                FROM financial_metric
                WHERE updated_at IS NOT NULL
                UNION ALL
                SELECT date AS source_date
                FROM stock_consensus
                WHERE date IS NOT NULL
            );
            """
        ).fetchone()
    first_earnings_source_date = source_dates["first_source_date"] if source_dates else None
    print(f"first_earnings_source_date={first_earnings_source_date}")

    totals = {
        "price_ok": 0,
        "price_failed": 0,
        "fundamentals_ok": 0,
        "fundamentals_failed": 0,
        "breadth_ok": 0,
        "breadth_failed": 0,
        "cycle_ok": 0,
        "cycle_failed": 0,
    }

    for index, as_of in enumerate(weekly_dates, start=1):
        print(f"week_start index={index}/{len(weekly_dates)} as_of={as_of}")

        factor_rows = factor_repository.list_factor_weekly_for_as_of(
            as_of, price_cfg["model_version"], db_path=DB_PATH
        )
        existing_target_ids = {
            str(row["asset_id"]) for row in factor_rows if row["asset_id"] in price_target_ids
        }
        can_reuse_price = args.reuse_price_factors and existing_target_ids == price_target_ids
        if can_reuse_price:
            price_ok = len(price_targets)
            price_failed = 0
        else:
            price_results = price_factor_runner.run_factor_batch(
                price_targets,
                as_of=as_of,
                model_config=price_cfg,
                dry_run=False,
                db_path=DB_PATH,
            )
            price_ok = sum(1 for result in price_results if result.status == "ok")
            price_failed = len(price_results) - price_ok
            factor_rows = factor_repository.list_factor_weekly_for_as_of(
                as_of, price_cfg["model_version"], db_path=DB_PATH
            )
        totals["price_ok"] += price_ok
        totals["price_failed"] += price_failed

        fundamentals_ok = 0
        fundamentals_failed = 0
        for industry_id in active_industries:
            try:
                bundle = fundamentals_scoring.compute_fundamentals_score(
                    industry_id,
                    as_of,
                    fundamentals_model_config=fundamentals_cfg,
                    db_path=DB_PATH,
                )
                fundamentals_repository.upsert_industry_fundamentals_weekly(
                    {
                        "industry_id": industry_id,
                        "as_of": as_of,
                        "model_version": fundamentals_cfg["model_version"],
                        "data_cutoff_at": as_of,
                        "data_completeness": bundle.data_completeness,
                        "fundamentals_score": bundle.score,
                        "weighted_sum": bundle.weighted_sum,
                        "reason": bundle.reason,
                        "indicators_used": bundle.to_dict()["evidence"],
                    },
                    db_path=DB_PATH,
                )
                fundamentals_ok += 1
            except Exception as exc:  # noqa: BLE001 - isolate one industry
                fundamentals_failed += 1
                print(f"stage_error as_of={as_of} stage=fundamentals industry_id={industry_id} error={exc}")
        totals["fundamentals_ok"] += fundamentals_ok
        totals["fundamentals_failed"] += fundamentals_failed

        factor_rows = [
            row
            for row in factor_rows
            if row["asset_id"] in price_target_ids
        ]
        factor_rows_by_asset = {row["asset_id"]: row for row in factor_rows}

        breadth_ok = 0
        breadth_failed = 0
        for industry_id in active_industries:
            try:
                stock_mappings = [
                    row
                    for row in assets_payload.get("mappings", [])
                    if row.get("industry_id") == industry_id
                    and str(row.get("asset_type") or "").upper() == "STOCK"
                    and _is_valid_at(row, as_of)
                ]
                tickers = [str(row["asset_id"]) for row in stock_mappings]
                earnings_tickers = (
                    tickers
                    if first_earnings_source_date is None or as_of >= first_earnings_source_date
                    else []
                )
                earnings_revision = industry_breadth_scoring.compute_industry_earnings_revision_score(
                    industry_id,
                    as_of,
                    tickers=earnings_tickers,
                    stock_model_config=stock_cfg,
                    db_path=DB_PATH,
                )
                breadth = industry_breadth_scoring.compute_industry_breadth_score_from_factor_rows(
                    industry_id,
                    as_of,
                    factor_rows=[
                        factor_rows_by_asset[ticker]
                        for ticker in tickers
                        if ticker in factor_rows_by_asset
                    ],
                    stock_model_config=stock_cfg,
                )
                candidate_repository.upsert_industry_earnings_breadth_weekly(
                    {
                        "industry_id": industry_id,
                        "as_of": as_of,
                        "model_version": stock_cfg["model_version"],
                        "data_cutoff_at": as_of,
                        "earnings_revision_score": earnings_revision.score,
                        "earnings_revision_weighted_sum": earnings_revision.weighted_sum,
                        "earnings_revision_reason": earnings_revision.reason,
                        "earnings_revision_data_completeness": earnings_revision.data_completeness,
                        "earnings_revision_evidence": [
                            item.to_dict() for item in earnings_revision.evidence
                        ],
                        "breadth_score": breadth.score,
                        "breadth_weighted_sum": breadth.weighted_sum,
                        "breadth_reason": breadth.reason,
                        "breadth_data_completeness": breadth.data_completeness,
                        "breadth_evidence": [item.to_dict() for item in breadth.evidence],
                        "n_tickers_considered": len(tickers),
                    },
                    db_path=DB_PATH,
                )
                breadth_ok += 1
            except Exception as exc:  # noqa: BLE001 - isolate one industry
                breadth_failed += 1
                print(f"stage_error as_of={as_of} stage=breadth industry_id={industry_id} error={exc}")
        totals["breadth_ok"] += breadth_ok
        totals["breadth_failed"] += breadth_failed

        cycle_results = cycle_runner.run_cycle_batch(
            active_industries,
            as_of=as_of,
            cycle_model_config=cycle_cfg,
            fundamentals_model_version=fundamentals_cfg["model_version"],
            candidate_model_version=stock_cfg["model_version"],
            price_model_version=price_cfg["model_version"],
            dry_run=False,
            db_path=DB_PATH,
        )
        cycle_ok = sum(1 for result in cycle_results if result.status == "ok")
        cycle_failed = len(cycle_results) - cycle_ok
        totals["cycle_ok"] += cycle_ok
        totals["cycle_failed"] += cycle_failed

        print(
            f"week_done as_of={as_of} "
            f"price={price_ok}/{len(price_targets)} reused={can_reuse_price} "
            f"fundamentals={fundamentals_ok}/{len(active_industries)} "
            f"breadth={breadth_ok}/{len(active_industries)} "
            f"cycle={cycle_ok}/{len(active_industries)}"
        )

    failed = sum(value for key, value in totals.items() if key.endswith("_failed"))
    print(
        "backfill_industry_cycle_history_done "
        f"weeks={len(weekly_dates)} range={first_as_of}..{last_as_of} "
        + " ".join(f"{key}={value}" for key, value in totals.items())
    )
    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
