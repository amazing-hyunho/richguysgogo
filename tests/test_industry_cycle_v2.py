from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest
from unittest.mock import patch

from committee.industry_cycle import (
    candidate_repository,
    cycle_v2,
    cycle_v2_model_config,
    cycle_v2_repository,
    fundamentals_repository,
    repository,
)


class CycleV2MathTests(unittest.TestCase):
    def test_percentile_rank_uses_midrank_for_ties(self) -> None:
        self.assertEqual(cycle_v2.percentile_rank(20.0, [10.0, 20.0, 20.0, 40.0]), 50.0)

    def test_ridge_learns_direction_without_configured_feature_weights(self) -> None:
        rows = [(float(x), float(100 - x), 0.001 * float(x)) for x in range(10, 100, 10)]
        model = cycle_v2._fit_ridge(rows, 0.1)
        self.assertGreater(model.predict(90.0, 10.0), model.predict(10.0, 90.0))


class CycleV2BatchTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmpdir = tempfile.TemporaryDirectory()
        self.db_path = Path(self._tmpdir.name) / "test.db"
        self.config = cycle_v2_model_config.load_cycle_v2_model_config()
        for industry_id in ("a", "b"):
            repository.upsert_industry_master(industry_id=industry_id, name_kr=industry_id, db_path=self.db_path)
        dates = [f"2026-01-{day:02d}" for day in (2, 9, 16, 23, 30)] + [
            "2026-02-06", "2026-02-13", "2026-02-20"
        ]
        for index, as_of in enumerate(dates):
            fundamentals_repository.upsert_industry_fundamentals_weekly(
                {
                    "industry_id": "a", "as_of": as_of, "model_version": "fund_v1",
                    "data_cutoff_at": as_of, "fundamentals_score": 10.0 + index * 10.0,
                },
                db_path=self.db_path,
            )
            fundamentals_repository.upsert_industry_fundamentals_weekly(
                {
                    "industry_id": "b", "as_of": as_of, "model_version": "fund_v1",
                    "data_cutoff_at": as_of, "fundamentals_score": 90.0 - index * 10.0,
                },
                db_path=self.db_path,
            )
        candidate_repository.upsert_industry_earnings_breadth_weekly(
            {
                "industry_id": "a", "as_of": dates[-1], "model_version": "stock_v1",
                "data_cutoff_at": dates[-1], "breadth_score": 80.0,
            }, db_path=self.db_path,
        )
        self.as_of = dates[-1]

    def tearDown(self) -> None:
        self._tmpdir.cleanup()

    def test_fixed_market_block_is_not_renormalized_when_breadth_is_missing(self) -> None:
        factors = {
            "a": SimpleNamespace(relative_strength_score=80.0, overheat_score=40.0),
            "b": SimpleNamespace(relative_strength_score=20.0, overheat_score=60.0),
        }
        with patch.object(
            cycle_v2.cycle_scoring,
            "select_representative_price_factors",
            side_effect=lambda industry_id, *args, **kwargs: factors[industry_id],
        ):
            rows = cycle_v2.compute_cycle_v2_batch(
                ["a", "b"], as_of=self.as_of, config=self.config,
                fundamentals_model_version="fund_v1", candidate_model_version="stock_v1",
                price_model_version="price_v1", persist=False, db_path=self.db_path,
            )
        by_id = {row["industry_id"]: row for row in rows}
        self.assertEqual(by_id["a"]["market_confirmation_score"], 62.5)
        self.assertIsNone(by_id["b"]["market_confirmation_score"])
        self.assertAlmostEqual(by_id["b"]["data_completeness"], 2.0 / 3.0)
        self.assertGreater(by_id["a"]["kpi_cycle_score"], by_id["b"]["kpi_cycle_score"])

    def test_repository_round_trip(self) -> None:
        cycle_v2_repository.upsert_cycle_v2_signal(
            {
                "industry_id": "a", "as_of": self.as_of, "model_version": "cycle_v2",
                "kpi_cycle_score": 75.0, "market_confirmation_score": 65.0,
                "entry_signal": "EARLY_ENTRY", "training_sample_count": 100,
            },
            db_path=self.db_path,
        )
        rows = cycle_v2_repository.list_cycle_v2_signals(
            industry_id="a", model_version="cycle_v2", db_path=self.db_path
        )
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["entry_signal"], "EARLY_ENTRY")


if __name__ == "__main__":
    unittest.main()
