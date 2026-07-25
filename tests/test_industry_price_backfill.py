from __future__ import annotations

from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from committee.industry_cycle import price_backfill, price_repository
from committee.industry_cycle.price_models import AssetPriceRecord
from committee.tools.industry_price_provider import IndustryPriceProvider

SAMPLE_UNIVERSE = {
    "benchmarks": [
        {"asset_id": "KOSPI", "market": "KR", "currency": "KRW", "provider": "yahoo_chart", "symbol": "^KS11"},
        {"asset_id": "SP500", "market": "US", "currency": "USD", "provider": "yahoo_chart", "symbol": "^GSPC"},
    ],
    "assets": [
        {
            "asset_id": "SOXX",
            "market": "US",
            "currency": "USD",
            "provider": "yahoo_chart",
            "symbol": "SOXX",
            "asset_type": "ETF",
            "industry_id": "semiconductors",
        },
        {
            "asset_id": "091160.KS",
            "market": "KR",
            "currency": "KRW",
            "provider": "flaky_krx",
            "symbol": "091160.KS",
            "asset_type": "ETF",
            "industry_id": "semiconductors",
        },
    ],
}


class BuildTargetsTests(unittest.TestCase):
    def test_builds_targets_from_benchmarks_and_assets(self) -> None:
        targets = price_backfill.build_targets_from_universe(SAMPLE_UNIVERSE)
        self.assertEqual(len(targets), 4)
        by_id = {t.asset_id: t for t in targets}
        self.assertEqual(by_id["KOSPI"].asset_type, "BENCHMARK")
        self.assertEqual(by_id["SOXX"].industry_id, "semiconductors")


class _FakeSucceedingProvider(IndustryPriceProvider):
    name = "fake_ok"

    def fetch_daily_prices(self, *, asset_id, symbol, market, currency, start, end):
        return [
            AssetPriceRecord(
                asset_id=asset_id,
                market=market,
                currency=currency,
                trade_date=start,
                close_price=100.0,
                adj_close_price=100.0,
                adjustment_status="adjusted",
                source=self.name,
                source_ref=symbol,
                available_at=f"{start}T23:59:59+00:00",
                collected_at="2026-07-25T00:00:00+00:00",
            )
        ]


class _FakeFailingProvider(IndustryPriceProvider):
    name = "fake_fail"

    def fetch_daily_prices(self, **kwargs):
        raise RuntimeError("simulated_krx_outage")


def _resolver(name: str) -> IndustryPriceProvider:
    if name == "yahoo_chart":
        return _FakeSucceedingProvider()
    if name == "flaky_krx":
        return _FakeFailingProvider()
    raise ValueError(f"unexpected provider: {name}")


class RunBackfillDryRunTests(unittest.TestCase):
    def test_dry_run_makes_no_provider_or_db_calls(self) -> None:
        targets = price_backfill.build_targets_from_universe(SAMPLE_UNIVERSE)

        def _explode(_name: str) -> IndustryPriceProvider:
            raise AssertionError("provider_resolver must not be called in dry-run mode")

        results = price_backfill.run_backfill(
            targets,
            start="2026-01-01",
            end="2026-07-01",
            provider_resolver=_explode,
            dry_run=True,
        )
        self.assertEqual(len(results), 4)
        self.assertTrue(all(r.status == "planned" for r in results))

    def test_dry_run_is_the_default(self) -> None:
        targets = price_backfill.build_targets_from_universe(SAMPLE_UNIVERSE)
        results = price_backfill.run_backfill(
            targets, start="2026-01-01", end="2026-07-01", provider_resolver=_resolver
        )
        self.assertTrue(all(r.status == "planned" for r in results))


class RunBackfillExecuteTests(unittest.TestCase):
    def test_one_provider_failure_does_not_stop_other_assets(self) -> None:
        """Design item 8: provider failure isolation — one asset's failure must
        not raise or prevent the remaining assets from being processed."""
        targets = price_backfill.build_targets_from_universe(SAMPLE_UNIVERSE)
        with tempfile.TemporaryDirectory() as td:
            db_path = Path(td) / "investment.db"
            results = price_backfill.run_backfill(
                targets,
                start="2026-07-01",
                end="2026-07-01",
                provider_resolver=_resolver,
                dry_run=False,
                db_path=db_path,
            )
            self.assertEqual(len(results), 4)
            by_id = {r.asset_id: r for r in results}
            self.assertEqual(by_id["091160.KS"].status, "failed")
            self.assertIn("simulated_krx_outage", by_id["091160.KS"].error or "")
            # The other three (yahoo_chart-backed) targets must still succeed.
            for asset_id in ("KOSPI", "SP500", "SOXX"):
                self.assertEqual(by_id[asset_id].status, "ok")
                self.assertEqual(by_id[asset_id].rows_written, 1)

            stored = price_repository.get_prices("SOXX", db_path=db_path)
            self.assertEqual(len(stored), 1)
            self.assertEqual(price_repository.get_prices("091160.KS", db_path=db_path), [])

    def test_unknown_provider_name_is_isolated_too(self) -> None:
        targets = [
            price_backfill.PriceBackfillTarget(
                asset_id="X", market="US", currency="USD", provider_name="does_not_exist", symbol="X"
            )
        ]
        with tempfile.TemporaryDirectory() as td:
            db_path = Path(td) / "investment.db"
            results = price_backfill.run_backfill(
                targets,
                start="2026-07-01",
                end="2026-07-01",
                provider_resolver=_resolver,
                dry_run=False,
                db_path=db_path,
            )
            self.assertEqual(results[0].status, "failed")


if __name__ == "__main__":
    unittest.main()
