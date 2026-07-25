from __future__ import annotations

"""Phase 2 weekly fundamentals-factor CLI (dry-run by default).

Loads `config/industry_taxonomy.json` (Phase 0) and
`config/industry_cycle_fundamentals_model.json` (Phase 2), computes one
`fundamentals_score` per active industry as-of a given date
(`committee.industry_cycle.fundamentals_scoring.compute_fundamentals_score`,
point-in-time gated via `known_at <= as_of`), and either:
- prints the plan (default; no DB writes at all), or
- persists `industry_fundamentals_weekly` rows, only when `--execute` is
  passed.

`--as-of` lets a past week be reproduced deterministically -- it defaults to
today. Not wired into `scripts/run_nightly.py` (same constraint as Phase 1-B's
`run_industry_price_factors.py`).
"""

import argparse
from datetime import date
from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from committee.industry_cycle import (
    fundamentals_model_config,
    fundamentals_repository,
    fundamentals_scoring,
    indicator_catalog,
    repository,
    taxonomy,
)

DB_PATH = ROOT_DIR / "data" / "investment.db"


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compute (and optionally persist) Phase 2 weekly fundamentals_score per industry."
    )
    parser.add_argument("--as-of", default=date.today().isoformat(), help="Point-in-time cutoff date (YYYY-MM-DD).")
    parser.add_argument(
        "--taxonomy",
        default=str(taxonomy.TAXONOMY_PATH),
        help="Path to industry_taxonomy.json.",
    )
    parser.add_argument(
        "--model-config",
        default=str(fundamentals_model_config.FUNDAMENTALS_MODEL_CONFIG_PATH),
        help="Path to industry_cycle_fundamentals_model.json.",
    )
    parser.add_argument(
        "--indicators-config",
        default=str(indicator_catalog.INDICATOR_CONFIG_PATH),
        help="Path to industry_indicators.json.",
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Actually write industry_fundamentals_weekly rows. Without this flag, only prints the plan.",
    )
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    taxonomy_config = taxonomy.load_taxonomy(Path(args.taxonomy))
    model_config = fundamentals_model_config.load_fundamentals_model_config(Path(args.model_config))
    industry_ids = [
        str(entry["industry_id"])
        for entry in taxonomy_config.get("industries", [])
        if entry.get("active", True)
    ]

    print(
        f"run_industry_fundamentals_factors_plan industries={len(industry_ids)} as_of={args.as_of} "
        f"model_version={model_config['model_version']} execute={args.execute}"
    )
    for industry_id in industry_ids:
        print(f"  target industry_id={industry_id}")

    if not args.execute:
        print("run_industry_fundamentals_factors_dry_run_only (pass --execute to actually compute and write)")
        return

    # Deterministic, idempotent sync of Phase 0 structural tables from config
    # (design doc section 12, Phase 0 completion criterion: "동일 입력으로
    # 같은 산업·지표 매핑을 재현할 수 있다") -- runs every --execute invocation
    # so this CLI is usable standalone without a separate manual sync step.
    indicators_payload = indicator_catalog.load_indicator_config(Path(args.indicators_config))
    repository.sync_industry_master_from_config(taxonomy_config, db_path=DB_PATH)
    repository.sync_indicator_catalog_from_config(indicators_payload, db_path=DB_PATH)
    repository.sync_industry_indicator_map_from_config(indicators_payload, db_path=DB_PATH)

    ok = 0
    failed = 0
    for industry_id in industry_ids:
        try:
            bundle = fundamentals_scoring.compute_fundamentals_score(
                industry_id, args.as_of, fundamentals_model_config=model_config, db_path=DB_PATH
            )
            fundamentals_repository.upsert_industry_fundamentals_weekly(
                {
                    "industry_id": industry_id,
                    "as_of": args.as_of,
                    "model_version": model_config["model_version"],
                    "data_cutoff_at": args.as_of,
                    "data_completeness": bundle.data_completeness,
                    "fundamentals_score": bundle.score,
                    "weighted_sum": bundle.weighted_sum,
                    "reason": bundle.reason,
                    "indicators_used": bundle.to_dict()["evidence"],
                },
                db_path=DB_PATH,
            )
            print(
                f"result industry_id={industry_id} status=ok score={bundle.score} "
                f"data_completeness={bundle.data_completeness:.2f} evidence_count={len(bundle.non_price_evidence())}"
            )
            ok += 1
        except Exception as exc:  # noqa: BLE001
            repository.record_data_quality_event(
                event_type="fundamentals_factor_run_failed",
                target=industry_id,
                severity="medium",
                message=str(exc),
                db_path=DB_PATH,
            )
            print(f"result industry_id={industry_id} status=failed error={exc}")
            failed += 1

    print(f"run_industry_fundamentals_factors_done ok={ok} failed={failed} total={len(industry_ids)}")


if __name__ == "__main__":
    main()
