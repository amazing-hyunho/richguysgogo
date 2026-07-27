from __future__ import annotations

"""Phase 3 ETF/stock candidate ranking CLI (dry-run by default).

For every industry that currently has at least one asset in
`industry_asset_map` (Phase 0), computes:
- ETF quality pass/fail (`committee.industry_cycle.etf_quality`)
- Per-stock `stock_score` + exclusion reasons (`stock_scoring`)
- Industry-level `earnings_revision_score` / `breadth_score`
  (`industry_breadth_scoring`)

via `committee.industry_cycle.candidate_ranking`, and either:
- prints the plan + a per-industry summary (default; no DB writes), or
- persists `industry_candidate` + `industry_earnings_breadth_weekly` rows,
  only when `--execute` is passed.

`--as-of` lets a past week be reproduced deterministically -- it defaults to
today. Not wired into `scripts/run_nightly.py` (same constraint as Phase
1-B/2's CLIs). Mirrors `run_industry_fundamentals_factors.py`'s structure:
inline-syncs Phase 0 structural tables from config on `--execute` so this
CLI is usable standalone.
"""

import argparse
from datetime import date
from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from committee.industry_cycle import (
    candidate_ranking,
    etf_quality,
    price_model_config,
    price_universe,
    repository,
    stock_model_config,
    taxonomy,
)

DB_PATH = ROOT_DIR / "data" / "investment.db"


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compute (and optionally persist) Phase 3 ETF/stock candidate rankings per industry."
    )
    parser.add_argument("--as-of", default=date.today().isoformat(), help="Point-in-time cutoff date (YYYY-MM-DD).")
    parser.add_argument(
        "--taxonomy", default=str(taxonomy.TAXONOMY_PATH), help="Path to industry_taxonomy.json."
    )
    parser.add_argument(
        "--stock-model-config",
        default=str(stock_model_config.STOCK_MODEL_CONFIG_PATH),
        help="Path to industry_cycle_stock_model.json.",
    )
    parser.add_argument(
        "--price-model-config",
        default=str(price_model_config.PRICE_MODEL_CONFIG_PATH),
        help="Path to industry_cycle_price_model.json (reused here only for its return/MA/volatility windows).",
    )
    parser.add_argument(
        "--etf-quality-config",
        default=str(etf_quality.ETF_QUALITY_CONFIG_PATH),
        help="Path to industry_etf_quality.json.",
    )
    parser.add_argument(
        "--price-universe",
        default=str(price_universe.PRICE_UNIVERSE_PATH),
        help="Path to industry_price_universe.json (for country-benchmark lookup).",
    )
    parser.add_argument(
        "--assets-config",
        default=str(ROOT_DIR / "config" / "industry_etfs.json"),
        help="Path to the industry_asset_map config (ETF+STOCK mappings) to sync on --execute.",
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Actually write industry_candidate/industry_earnings_breadth_weekly rows. Without this flag, only prints the plan.",
    )
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    taxonomy_config = taxonomy.load_taxonomy(Path(args.taxonomy))
    stock_cfg = stock_model_config.load_stock_model_config(Path(args.stock_model_config))
    price_feature_cfg = price_model_config.load_price_model_config(Path(args.price_model_config))
    etf_quality_catalog = etf_quality.load_etf_quality_catalog(Path(args.etf_quality_config))
    price_universe_payload = price_universe.load_price_universe(Path(args.price_universe))

    active_ids = {
        str(entry["industry_id"])
        for entry in taxonomy_config.get("industries", [])
        if entry.get("active", True)
    }
    all_mappings = [
        mapping
        for mapping in repository.list_industry_assets(db_path=DB_PATH)
        if mapping["industry_id"] in active_ids and candidate_ranking.is_valid_at(mapping, args.as_of)
    ]
    industry_ids_with_assets = sorted({m["industry_id"] for m in all_mappings})

    print(
        f"run_industry_candidates_plan industries={len(industry_ids_with_assets)} as_of={args.as_of} "
        f"model_version={stock_cfg['model_version']} execute={args.execute}"
    )
    for industry_id in industry_ids_with_assets:
        n_etf = sum(1 for m in all_mappings if m["industry_id"] == industry_id and (m.get("asset_type") or "").upper() == "ETF")
        n_stock = sum(1 for m in all_mappings if m["industry_id"] == industry_id and (m.get("asset_type") or "").upper() == "STOCK")
        print(f"  target industry_id={industry_id} etfs={n_etf} stocks={n_stock}")

    if not args.execute:
        print("run_industry_candidates_dry_run_only (pass --execute to actually compute and write)")
        return

    # Inline sync of Phase 0 structural tables, matching run_industry_fundamentals_factors.py's
    # standalone-usability pattern (design doc Phase 0 completion criterion).
    import json

    assets_payload = json.loads(Path(args.assets_config).read_text(encoding="utf-8"))
    repository.sync_industry_master_from_config(taxonomy_config, db_path=DB_PATH)
    repository.sync_industry_assets_from_config(assets_payload, db_path=DB_PATH)

    # Re-derive the industry list post-sync in case the sync just added new mappings.
    all_mappings = [
        mapping
        for mapping in repository.list_industry_assets(db_path=DB_PATH)
        if mapping["industry_id"] in active_ids and candidate_ranking.is_valid_at(mapping, args.as_of)
    ]
    industry_ids_with_assets = sorted({m["industry_id"] for m in all_mappings})

    ok = 0
    failed = 0
    for industry_id in industry_ids_with_assets:
        try:
            result = candidate_ranking.build_candidates_for_industry(
                industry_id,
                args.as_of,
                stock_model_config=stock_cfg,
                price_feature_config=price_feature_cfg,
                etf_quality_catalog=etf_quality_catalog,
                price_universe_payload=price_universe_payload,
                db_path=DB_PATH,
            )
            n_written = candidate_ranking.persist_candidate_ranking(
                result,
                model_version=stock_cfg["model_version"],
                data_cutoff_at=args.as_of,
                db_path=DB_PATH,
            )
            n_etf_passed = sum(1 for e in result.etf_candidates if not e["excluded"])
            n_stock_passed = sum(1 for s in result.stock_candidates if not s["excluded"])
            print(
                f"result industry_id={industry_id} status=ok rows_written={n_written} "
                f"etf_passed={n_etf_passed}/{len(result.etf_candidates)} "
                f"stock_passed={n_stock_passed}/{len(result.stock_candidates)} "
                f"earnings_revision_score={result.earnings_revision.score if result.earnings_revision else None} "
                f"breadth_score={result.breadth.score if result.breadth else None}"
            )
            ok += 1
        except Exception as exc:  # noqa: BLE001 - failure isolation: one industry never stops the rest
            repository.record_data_quality_event(
                event_type="candidate_ranking_run_failed",
                target=industry_id,
                severity="medium",
                message=str(exc),
                db_path=DB_PATH,
            )
            print(f"result industry_id={industry_id} status=failed error={exc}")
            failed += 1

    print(f"run_industry_candidates_done ok={ok} failed={failed} total={len(industry_ids_with_assets)}")


if __name__ == "__main__":
    main()
