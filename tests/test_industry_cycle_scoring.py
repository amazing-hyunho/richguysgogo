from __future__ import annotations

from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from committee.industry_cycle import candidate_repository, cycle_model_config, cycle_scoring, factor_repository, fundamentals_repository, repository


class CycleScoringTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmpdir = tempfile.TemporaryDirectory()
        self.db_path = Path(self._tmpdir.name) / "test.db"
        self.cycle_cfg = cycle_model_config.load_cycle_model_config()
        self.as_of = "2026-07-25"

        repository.upsert_industry_master(industry_id="semiconductors", name_kr="반도체", db_path=self.db_path)
        repository.upsert_industry_asset_map(
            asset_id="GOODETF", industry_id="semiconductors", asset_type="ETF", market="US",
            weight=1.0, valid_from="2026-01-01", db_path=self.db_path,
        )

        fundamentals_repository.upsert_industry_fundamentals_weekly(
            {
                "industry_id": "semiconductors", "as_of": self.as_of, "model_version": "fundamentals_v1",
                "data_cutoff_at": self.as_of, "fundamentals_score": 70.0, "data_completeness": 0.9,
            },
            db_path=self.db_path,
        )
        candidate_repository.upsert_industry_earnings_breadth_weekly(
            {
                "industry_id": "semiconductors", "as_of": self.as_of, "model_version": "stock_candidate_v1",
                "data_cutoff_at": self.as_of, "earnings_revision_score": 65.0, "breadth_score": 80.0,
            },
            db_path=self.db_path,
        )
        factor_repository.upsert_industry_factor_weekly(
            {
                "industry_id": "semiconductors", "market": "US", "asset_id": "GOODETF", "as_of": self.as_of,
                "model_version": "price_v1", "data_cutoff_at": self.as_of,
                "relative_strength_score": 72.0, "trend_score": 68.0, "overheat_score": 30.0,
                "price_risk_score": 20.0,
            },
            db_path=self.db_path,
        )

    def tearDown(self) -> None:
        self._tmpdir.cleanup()

    def _compute(self, **overrides):
        kwargs = dict(
            industry_id="semiconductors",
            as_of=self.as_of,
            cycle_model_config=self.cycle_cfg,
            fundamentals_model_version="fundamentals_v1",
            candidate_model_version="stock_candidate_v1",
            price_model_version="price_v1",
            db_path=self.db_path,
        )
        kwargs.update(overrides)
        return cycle_scoring.compute_cycle_score(**kwargs)

    def test_full_data_produces_a_score(self) -> None:
        bundle = self._compute()
        self.assertIsNotNone(bundle.score)
        self.assertEqual(bundle.fundamentals_score, 70.0)
        self.assertEqual(bundle.earnings_revision_score, 65.0)
        self.assertEqual(bundle.breadth_score, 80.0)
        self.assertEqual(bundle.relative_strength_score, 72.0)
        self.assertEqual(bundle.overheat_score, 30.0)
        self.assertIn("GOODETF", bundle.representative_asset_ids)

    def test_flow_and_macro_are_always_none(self) -> None:
        bundle = self._compute()
        self.assertIsNone(bundle.flow_score)
        self.assertIsNone(bundle.macro_fit_score)

    def test_data_completeness_reflects_missing_flow_and_macro(self) -> None:
        bundle = self._compute()
        # 4 of 6 components available: fundamentals(.25) + earnings_revision(.20)
        # + relative_strength(.20) + breadth(.10) = 0.75 of total weight 1.0
        self.assertAlmostEqual(bundle.data_completeness, 0.75)

    def test_no_data_at_all_gives_none_score(self) -> None:
        bundle = self._compute(industry_id="no_such_industry")
        self.assertIsNone(bundle.score)
        self.assertEqual(bundle.data_completeness, 0.0)

    def test_missing_price_factor_row_falls_back_gracefully(self) -> None:
        bundle = self._compute(price_model_version="some_other_version_never_run")
        self.assertIsNone(bundle.relative_strength_score)
        self.assertIsNone(bundle.overheat_score)
        # still scores from fundamentals + earnings_revision + breadth
        self.assertIsNotNone(bundle.score)

    def test_confidence_is_between_0_and_1(self) -> None:
        bundle = self._compute()
        self.assertGreaterEqual(bundle.confidence, 0.0)
        self.assertLessEqual(bundle.confidence, 1.0)

    def test_representative_price_factors_fall_back_to_stocks_when_no_etf(self) -> None:
        repository.upsert_industry_master(industry_id="banks", name_kr="은행", db_path=self.db_path)
        repository.upsert_industry_asset_map(
            asset_id="GOODSTOCK", industry_id="banks", asset_type="STOCK", market="US",
            weight=1.0, valid_from="2026-01-01", db_path=self.db_path,
        )
        factor_repository.upsert_industry_factor_weekly(
            {
                "industry_id": "banks", "market": "US", "asset_id": "GOODSTOCK", "as_of": self.as_of,
                "model_version": "price_v1", "data_cutoff_at": self.as_of,
                "relative_strength_score": 55.0, "trend_score": 50.0, "overheat_score": 10.0,
                "price_risk_score": 15.0,
            },
            db_path=self.db_path,
        )
        result = cycle_scoring.select_representative_price_factors(
            "banks", self.as_of, price_model_version="price_v1", db_path=self.db_path
        )
        self.assertIsNotNone(result)
        self.assertEqual(result.source_asset_type, "STOCK")
        self.assertEqual(result.relative_strength_score, 55.0)


class ConfidenceHelperTests(unittest.TestCase):
    def setUp(self) -> None:
        self.cycle_cfg = cycle_model_config.load_cycle_model_config()

    def test_signal_strength_none_weighted_sum_is_zero(self) -> None:
        self.assertEqual(cycle_scoring.compute_signal_strength(None, cycle_model_config=self.cycle_cfg), 0.0)

    def test_signal_strength_is_clipped_to_one(self) -> None:
        strength = cycle_scoring.compute_signal_strength(1000.0, cycle_model_config=self.cycle_cfg)
        self.assertEqual(strength, 1.0)

    def test_model_agreement_unknown_when_either_side_missing(self) -> None:
        expected = self.cycle_cfg["confidence"]["model_agreement_unknown_value"]
        self.assertEqual(
            cycle_scoring.compute_model_agreement(None, "PRICE_ONLY_EXPANSION", cycle_model_config=self.cycle_cfg),
            expected,
        )
        self.assertEqual(
            cycle_scoring.compute_model_agreement(70.0, None, cycle_model_config=self.cycle_cfg), expected
        )

    def test_model_agreement_penalizes_conflicting_directions(self) -> None:
        penalty = self.cycle_cfg["confidence"]["model_agreement_conflict_penalty"]
        self.assertEqual(
            cycle_scoring.compute_model_agreement(
                70.0, "PRICE_ONLY_DETERIORATING", cycle_model_config=self.cycle_cfg
            ),
            penalty,
        )
        self.assertEqual(
            cycle_scoring.compute_model_agreement(
                30.0, "PRICE_ONLY_EXPANSION", cycle_model_config=self.cycle_cfg
            ),
            penalty,
        )

    def test_model_agreement_full_when_directions_match(self) -> None:
        self.assertEqual(
            cycle_scoring.compute_model_agreement(70.0, "PRICE_ONLY_EXPANSION", cycle_model_config=self.cycle_cfg),
            1.0,
        )


if __name__ == "__main__":
    unittest.main()
