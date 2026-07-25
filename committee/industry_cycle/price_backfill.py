from __future__ import annotations

"""Phase 1-A price backfill orchestration (pure logic, provider-injected).

`scripts/backfill_industry_prices.py` is a thin CLI wrapper around the
functions here, so the backfill structure and dry-run behavior (design doc
section 12, Phase 1 item 1 / section 15 recommendation 5) can be unit
tested without touching the network or requiring the `scripts/` folder to
be importable as a package.

Failure isolation contract (design doc Phase 1-A item 8): a single asset's
provider failure must never stop the loop over the remaining assets, and
must never raise out of `run_backfill` to the caller.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Optional

from committee.industry_cycle import price_repository
from committee.tools.industry_price_provider import IndustryPriceProvider

ProviderResolver = Callable[[str], IndustryPriceProvider]


@dataclass(frozen=True)
class PriceBackfillTarget:
    """One asset to fetch prices for."""

    asset_id: str
    market: str
    currency: str
    provider_name: str
    symbol: str
    asset_type: Optional[str] = None
    industry_id: Optional[str] = None


@dataclass
class BackfillResult:
    """Outcome of attempting to backfill one target."""

    asset_id: str
    status: str  # 'planned' | 'ok' | 'failed'
    rows_fetched: int = 0
    rows_written: int = 0
    error: Optional[str] = None


def build_targets_from_universe(universe: Dict[str, Any]) -> List[PriceBackfillTarget]:
    """Convert a loaded `industry_price_universe.json` payload into targets."""
    targets: List[PriceBackfillTarget] = []
    for entry in universe.get("benchmarks", []):
        targets.append(
            PriceBackfillTarget(
                asset_id=str(entry["asset_id"]),
                market=str(entry["market"]),
                currency=str(entry["currency"]),
                provider_name=str(entry.get("provider", "yahoo_chart")),
                symbol=str(entry["symbol"]),
                asset_type="BENCHMARK",
            )
        )
    for entry in universe.get("assets", []):
        targets.append(
            PriceBackfillTarget(
                asset_id=str(entry["asset_id"]),
                market=str(entry["market"]),
                currency=str(entry["currency"]),
                provider_name=str(entry.get("provider", "yahoo_chart")),
                symbol=str(entry["symbol"]),
                asset_type=entry.get("asset_type"),
                industry_id=entry.get("industry_id"),
            )
        )
    return targets


def plan_backfill(targets: Iterable[PriceBackfillTarget]) -> List[BackfillResult]:
    """Return the no-op "what would happen" plan for `targets` (dry-run)."""
    return [BackfillResult(asset_id=t.asset_id, status="planned") for t in targets]


def run_backfill(
    targets: Iterable[PriceBackfillTarget],
    *,
    start: str,
    end: str,
    provider_resolver: ProviderResolver,
    dry_run: bool = True,
    db_path: Path | None = None,
) -> List[BackfillResult]:
    """Fetch and store prices for each target, isolating per-asset failures.

    When `dry_run` is True (the default), no provider or DB call is made —
    this returns the same plan as `plan_backfill`. Real network/DB access
    only happens when a caller explicitly passes `dry_run=False`.
    """
    if dry_run:
        return plan_backfill(targets)

    results: List[BackfillResult] = []
    for target in targets:
        try:
            provider = provider_resolver(target.provider_name)
            records = provider.fetch_daily_prices(
                asset_id=target.asset_id,
                symbol=target.symbol,
                market=target.market,
                currency=target.currency,
                start=start,
                end=end,
            )
            written = price_repository.bulk_upsert_asset_price_daily(records, db_path=db_path)
            results.append(
                BackfillResult(
                    asset_id=target.asset_id,
                    status="ok",
                    rows_fetched=len(records),
                    rows_written=written,
                )
            )
        except Exception as exc:  # noqa: BLE001 - isolation boundary (design item 8)
            results.append(BackfillResult(asset_id=target.asset_id, status="failed", error=str(exc)))
            continue
    return results
