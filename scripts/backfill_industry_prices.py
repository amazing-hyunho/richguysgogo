from __future__ import annotations

"""Phase 1-A price backfill CLI (structure + dry-run only for now).

Loads `config/industry_price_universe.json`, builds the list of KR/US
benchmark + industry-ETF price targets, and either:
- prints the plan (default; no network/DB access), or
- actually fetches and writes prices, only when `--execute` is passed.

Design doc constraints honored here:
- Provider failures are isolated per-asset (`price_backfill.run_backfill`);
  one failing symbol does not stop the rest of the run or raise.
- Nothing here is wired into `scripts/run_nightly.py` yet — Phase 1-A is
  explicitly scoped to *not* run a real full backfill (see task constraints).
"""

import argparse
from datetime import date
from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from committee.industry_cycle import price_backfill, price_universe
from committee.tools.industry_price_provider import IndustryPriceProvider, YahooChartPriceProvider

DB_PATH = ROOT_DIR / "data" / "investment.db"

_PROVIDERS: dict[str, type[IndustryPriceProvider]] = {
    "yahoo_chart": YahooChartPriceProvider,
}


def _resolve_provider(name: str) -> IndustryPriceProvider:
    provider_cls = _PROVIDERS.get(name)
    if provider_cls is None:
        raise ValueError(f"unknown_provider: {name}")
    return provider_cls()


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Backfill KR/US benchmark + industry ETF prices into asset_price_daily."
    )
    parser.add_argument("--start-date", default="2015-01-01", help="Inclusive start date (YYYY-MM-DD).")
    parser.add_argument("--end-date", default=date.today().isoformat(), help="Inclusive end date (YYYY-MM-DD).")
    parser.add_argument(
        "--universe",
        default=str(price_universe.PRICE_UNIVERSE_PATH),
        help="Path to industry_price_universe.json.",
    )
    parser.add_argument(
        "--asset-id",
        action="append",
        default=[],
        help="Collect only this asset_id (repeatable). Default: the full universe.",
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
    universe = price_universe.load_price_universe(Path(args.universe))
    targets = price_backfill.build_targets_from_universe(universe)
    if args.asset_id:
        selected = {str(asset_id).strip() for asset_id in args.asset_id}
        targets = [target for target in targets if target.asset_id in selected]

    print(
        f"backfill_industry_prices_plan targets={len(targets)} "
        f"start={args.start_date} end={args.end_date} execute={args.execute}"
    )
    for target in targets:
        print(
            f"  target asset_id={target.asset_id} market={target.market} "
            f"currency={target.currency} provider={target.provider_name} symbol={target.symbol} "
            f"asset_type={target.asset_type}"
        )

    if not args.execute:
        print("backfill_industry_prices_dry_run_only (pass --execute to actually fetch and write)")
        return

    results = price_backfill.run_backfill(
        targets,
        start=args.start_date,
        end=args.end_date,
        provider_resolver=_resolve_provider,
        dry_run=False,
        db_path=DB_PATH,
    )
    for result in results:
        print(
            f"result asset_id={result.asset_id} status={result.status} "
            f"fetched={result.rows_fetched} written={result.rows_written} error={result.error}"
        )
    ok = sum(1 for r in results if r.status == "ok")
    failed = sum(1 for r in results if r.status == "failed")
    print(f"backfill_industry_prices_done ok={ok} failed={failed} total={len(results)}")


if __name__ == "__main__":
    main()
