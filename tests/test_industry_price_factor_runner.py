from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from committee.industry_cycle import factor_repository, price_factor_runner, price_model_config, price_repository
from committee.industry_cycle.price_models import AssetPriceRecord

SAMPLE_UNIVERSE = {
    "benchmarks": [
        {"asset_id": "KOSPI", "market": "KR", "currency": "KRW", "provider": "yahoo_chart", "symbol": "^KS11"},
        {"asset_id": "SP500", "market": "US", "currency": "USD", "provider": "yahoo_chart", "symbol": "^GSPC"},
    ],
    "assets": [
        {
            "asset_id": "091160.KS",
            "market": "KR",
            "currency": "KRW",
            "provider": "yahoo_chart",
            "symbol": "091160.KS",
            "asset_type": "ETF",
            "industry_id": "semiconductors",
        },
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
            "asset_id": "NOT_MAPPED",
            "market": "US",
            "currency": "USD",
            "provider": "yahoo_chart",
            "symbol": "NOT_MAPPED",
            "asset_type": "ETF",
            "industry_id": None,
        },
    ],
}


def _seed_prices(db_path: Path, asset_id: str, market: str, currency: str, prices, *, start_date="2019-01-01") -> None:
    d0 = date.fromisoformat(start_date)
    records = []
    for i, price in enumerate(prices):
        trade_date = (d0 + timedelta(days=i)).isoformat()
        records.append(
            AssetPriceRecord(
                asset_id=asset_id,
                market=market,
                currency=currency,
                trade_date=trade_date,
                close_price=float(price),
                adj_close_price=float(price),
                adjustment_status="adjusted",
                available_at=f"{trade_date}T23:59:59+00:00",
            )
        )
    price_repository.bulk_upsert_asset_price_daily(records, db_path=db_path)


class BuildTargetsTests(unittest.TestCase):
    def test_skips_assets_without_industry_id(self) -> None:
        targets = price_factor_runner.build_targets_from_universe(SAMPLE_UNIVERSE)
        asset_ids = {t.asset_id for t in targets}
        self.assertEqual(asset_ids, {"091160.KS", "SOXX"})

    def test_kr_asset_resolves_kospi_benchmark_us_asset_resolves_sp500(self) -> None:
        targets = price_factor_runner.build_targets_from_universe(SAMPLE_UNIVERSE)
        by_id = {t.asset_id: t for t in targets}
        self.assertEqual(by_id["091160.KS"].benchmark_asset_id, "KOSPI")
        self.assertEqual(by_id["SOXX"].benchmark_asset_id, "SP500")


class DryRunTests(unittest.TestCase):
    def test_dry_run_touches_no_db_and_returns_planned(self) -> None:
        targets = price_factor_runner.build_targets_from_universe(SAMPLE_UNIVERSE)
        model_config = price_model_config.load_price_model_config()
        with tempfile.TemporaryDirectory() as td:
            db_path = Path(td) / "does_not_exist_yet" / "investment.db"
            results = price_factor_runner.run_factor_batch(
                targets, as_of="2026-07-24", model_config=model_config, dry_run=True, db_path=db_path
            )
            self.assertEqual(len(results), 2)
            self.assertTrue(all(r.status == "planned" for r in results))
            self.assertFalse(db_path.exists())  # no DB file created at all -- true no-op

    def test_dry_run_is_the_default(self) -> None:
        targets = price_factor_runner.build_targets_from_universe(SAMPLE_UNIVERSE)
        model_config = price_model_config.load_price_model_config()
        results = price_factor_runner.run_factor_batch(targets, as_of="2026-07-24", model_config=model_config)
        self.assertTrue(all(r.status == "planned" for r in results))


class ExecuteTests(unittest.TestCase):
    def test_execute_computes_and_persists_factor_and_state_rows(self) -> None:
        targets = price_factor_runner.build_targets_from_universe(SAMPLE_UNIVERSE)
        model_config = price_model_config.load_price_model_config()
        with tempfile.TemporaryDirectory() as td:
            db_path = Path(td) / "investment.db"
            _seed_prices(db_path, "KOSPI", "KR", "KRW", [2500.0 + i * 0.2 for i in range(400)])
            _seed_prices(db_path, "SP500", "US", "USD", [4500.0 + i * 0.5 for i in range(400)])
            _seed_prices(db_path, "091160.KS", "KR", "KRW", [10000.0 + i * 5 for i in range(400)])
            _seed_prices(db_path, "SOXX", "US", "USD", [400.0 + i * 0.3 for i in range(400)])

            as_of = (date.fromisoformat("2019-01-01") + timedelta(days=390)).isoformat()
            results = price_factor_runner.run_factor_batch(
                targets, as_of=as_of, model_config=model_config, dry_run=False, db_path=db_path
            )
            self.assertEqual(len(results), 2)
            self.assertTrue(all(r.status == "ok" for r in results))

            stored_factor = factor_repository.get_factor_weekly("SOXX", as_of, model_config["model_version"], db_path=db_path)
            self.assertIsNotNone(stored_factor)
            stored_state = factor_repository.get_price_state_weekly(
                "SOXX", as_of, model_config["model_version"], db_path=db_path
            )
            self.assertIsNotNone(stored_state)
            self.assertIn(stored_state["price_only_state"], {
                "PRICE_ONLY_RECOVERY_CANDIDATE",
                "PRICE_ONLY_EXPANSION",
                "PRICE_ONLY_OVERHEATED",
                "PRICE_ONLY_DETERIORATING",
                "PRICE_ONLY_WEAK",
                "PRICE_ONLY_INSUFFICIENT_DATA",
            })

    def test_rerunning_same_as_of_is_idempotent(self) -> None:
        targets = price_factor_runner.build_targets_from_universe(SAMPLE_UNIVERSE)
        model_config = price_model_config.load_price_model_config()
        with tempfile.TemporaryDirectory() as td:
            db_path = Path(td) / "investment.db"
            _seed_prices(db_path, "KOSPI", "KR", "KRW", [2500.0 + i * 0.2 for i in range(400)])
            _seed_prices(db_path, "SP500", "US", "USD", [4500.0 + i * 0.5 for i in range(400)])
            _seed_prices(db_path, "091160.KS", "KR", "KRW", [10000.0 + i * 5 for i in range(400)])
            _seed_prices(db_path, "SOXX", "US", "USD", [400.0 + i * 0.3 for i in range(400)])
            as_of = (date.fromisoformat("2019-01-01") + timedelta(days=390)).isoformat()

            price_factor_runner.run_factor_batch(targets, as_of=as_of, model_config=model_config, dry_run=False, db_path=db_path)
            price_factor_runner.run_factor_batch(targets, as_of=as_of, model_config=model_config, dry_run=False, db_path=db_path)
            price_factor_runner.run_factor_batch(targets, as_of=as_of, model_config=model_config, dry_run=False, db_path=db_path)

            rows = factor_repository.list_factor_weekly("SOXX", db_path=db_path)
            self.assertEqual(len(rows), 1)
            state_rows = factor_repository.list_price_state_weekly("SOXX", db_path=db_path)
            self.assertEqual(len(state_rows), 1)

    def test_different_model_version_preserves_old_run(self) -> None:
        targets = price_factor_runner.build_targets_from_universe(SAMPLE_UNIVERSE)
        model_config_v1 = price_model_config.load_price_model_config()
        model_config_v2 = dict(model_config_v1)
        model_config_v2["model_version"] = "price_only_v2_test"
        with tempfile.TemporaryDirectory() as td:
            db_path = Path(td) / "investment.db"
            _seed_prices(db_path, "KOSPI", "KR", "KRW", [2500.0 + i * 0.2 for i in range(400)])
            _seed_prices(db_path, "SP500", "US", "USD", [4500.0 + i * 0.5 for i in range(400)])
            _seed_prices(db_path, "091160.KS", "KR", "KRW", [10000.0 + i * 5 for i in range(400)])
            _seed_prices(db_path, "SOXX", "US", "USD", [400.0 + i * 0.3 for i in range(400)])
            as_of = (date.fromisoformat("2019-01-01") + timedelta(days=390)).isoformat()

            price_factor_runner.run_factor_batch(targets, as_of=as_of, model_config=model_config_v1, dry_run=False, db_path=db_path)
            price_factor_runner.run_factor_batch(targets, as_of=as_of, model_config=model_config_v2, dry_run=False, db_path=db_path)

            rows = factor_repository.list_factor_weekly("SOXX", db_path=db_path)
            self.assertEqual(len(rows), 2)
            versions = {r["model_version"] for r in rows}
            self.assertEqual(versions, {model_config_v1["model_version"], "price_only_v2_test"})

    def test_kr_and_us_assets_use_different_benchmarks_in_relative_return(self) -> None:
        """KR asset's rel_return uses KOSPI; US asset's uses SP500 -- distinct benchmark series
        produce a different relative-return outcome for an identical raw asset return."""
        targets = price_factor_runner.build_targets_from_universe(SAMPLE_UNIVERSE)
        model_config = price_model_config.load_price_model_config()
        with tempfile.TemporaryDirectory() as td:
            db_path = Path(td) / "investment.db"
            same_asset_prices = [1000.0 + i * 1.0 for i in range(400)]
            _seed_prices(db_path, "KOSPI", "KR", "KRW", [2500.0] * 400)  # flat KR benchmark
            _seed_prices(db_path, "SP500", "US", "USD", [4500.0 + i * 2.0 for i in range(400)])  # strongly rising US benchmark
            _seed_prices(db_path, "091160.KS", "KR", "KRW", same_asset_prices)
            _seed_prices(db_path, "SOXX", "US", "USD", same_asset_prices)
            as_of = (date.fromisoformat("2019-01-01") + timedelta(days=390)).isoformat()

            price_factor_runner.run_factor_batch(targets, as_of=as_of, model_config=model_config, dry_run=False, db_path=db_path)

            kr_factor = factor_repository.get_factor_weekly("091160.KS", as_of, model_config["model_version"], db_path=db_path)
            us_factor = factor_repository.get_factor_weekly("SOXX", as_of, model_config["model_version"], db_path=db_path)
            # Same absolute asset return, but KR benchmark is flat (rel_return == raw return)
            # while US benchmark rose sharply (rel_return << raw return).
            self.assertGreater(kr_factor["rel_return_12m"], us_factor["rel_return_12m"])

    def test_one_asset_failure_does_not_stop_the_batch(self) -> None:
        model_config = price_model_config.load_price_model_config()
        targets = [
            price_factor_runner.FactorTarget(
                asset_id="MISSING", market="US", industry_id="semiconductors", benchmark_asset_id="SP500"
            ),
            price_factor_runner.FactorTarget(
                asset_id="SOXX", market="US", industry_id="semiconductors", benchmark_asset_id="SP500"
            ),
        ]
        with tempfile.TemporaryDirectory() as td:
            db_path = Path(td) / "investment.db"
            _seed_prices(db_path, "SP500", "US", "USD", [4500.0 + i * 0.5 for i in range(400)])
            _seed_prices(db_path, "SOXX", "US", "USD", [400.0 + i * 0.3 for i in range(400)])
            as_of = (date.fromisoformat("2019-01-01") + timedelta(days=390)).isoformat()

            # "MISSING" has no price rows at all -- build_weekly_features handles that
            # gracefully (returns all-None features), so this specifically exercises that
            # both targets still complete successfully without one blocking the other.
            results = price_factor_runner.run_factor_batch(
                targets, as_of=as_of, model_config=model_config, dry_run=False, db_path=db_path
            )
            self.assertEqual(len(results), 2)
            by_id = {r.asset_id: r for r in results}
            self.assertEqual(by_id["SOXX"].status, "ok")
            self.assertEqual(by_id["MISSING"].status, "ok")
            self.assertEqual(by_id["MISSING"].price_only_state, "PRICE_ONLY_INSUFFICIENT_DATA")


if __name__ == "__main__":
    unittest.main()
