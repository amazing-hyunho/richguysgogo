from __future__ import annotations

"""Phase 2 indicator backfill CLI (dry-run by default).

Loads `config/industry_indicators.json`'s `indicators` catalog and, per
entry's `provider`, fetches point-in-time FRED/KOSIS observations
(`committee.industry_cycle.fundamentals_ingest.ingest_catalog`) into
`indicator_observation`. Only writes to the DB when `--execute` is passed;
one indicator's provider failure / missing API key never stops the rest
(failure isolation, recorded as a `data_quality_event`).

Free-source only (task constraint: "무료 데이터 소스 우선"); ECOS is not yet
wired into this generic path (see `fundamentals_ingest` module docstring) --
indicators declaring `provider: "ECOS"` are isolated with `status=skipped`.
"""

import argparse
from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from committee.industry_cycle import fundamentals_ingest, indicator_catalog

DB_PATH = ROOT_DIR / "data" / "investment.db"


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Backfill FRED/KOSIS industry indicator observations into indicator_observation."
    )
    parser.add_argument(
        "--indicators-config",
        default=str(indicator_catalog.INDICATOR_CONFIG_PATH),
        help="Path to industry_indicators.json.",
    )
    parser.add_argument(
        "--observation-start",
        default=None,
        help="Optional inclusive start date (YYYY-MM-DD) for provider history fetches.",
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help=(
            "Actually call providers and write to the DB. Without this flag, "
            "the CLI only prints the plan (dry-run; no network/DB access)."
        ),
    )
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    config = indicator_catalog.load_indicator_config(Path(args.indicators_config))
    entries = config.get("indicators", [])

    print(f"backfill_industry_indicators_plan indicators={len(entries)} execute={args.execute}")
    for entry in entries:
        print(
            f"  indicator_id={entry.get('indicator_id')} provider={entry.get('provider')} "
            f"series_id={entry.get('series_id')} transform={entry.get('transform')}"
        )

    if not args.execute:
        print("backfill_industry_indicators_dry_run_only (pass --execute to actually fetch and write)")
        return

    results = fundamentals_ingest.ingest_catalog(
        entries, observation_start=args.observation_start, db_path=DB_PATH
    )
    for result in results:
        print(
            f"result indicator_id={result.indicator_id} status={result.status} "
            f"rows_written={result.rows_written} reason={result.reason}"
        )
    ok = sum(1 for r in results if r.status == "ok")
    skipped = sum(1 for r in results if r.status == "skipped")
    failed = sum(1 for r in results if r.status == "failed")
    print(f"backfill_industry_indicators_done ok={ok} skipped={skipped} failed={failed} total={len(results)}")


if __name__ == "__main__":
    main()
