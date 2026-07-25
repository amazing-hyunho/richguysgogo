from __future__ import annotations

from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from committee.industry_cycle import fundamentals_scoring, repository

_MODEL_CONFIG = {
    "model_version": "fundamentals_only_v1",
    "scale_k": 4.0,
    "min_components": 2,
    "staleness_max_periods_by_frequency": {"monthly": 3, "quarterly": 2},
    "min_data_completeness_for_score": 0.34,
    "min_non_price_evidence_count_for_recovery_candidate": 2,
}


def _seed_industry(db_path: Path, industry_id: str = "semiconductors") -> None:
    repository.upsert_industry_master(industry_id=industry_id, name_kr="반도체", db_path=db_path)


def _seed_indicator(
    db_path: Path,
    indicator_id: str,
    *,
    frequency: str = "monthly",
    baseline: float | None = None,
) -> None:
    repository.upsert_indicator_catalog(
        indicator_id=indicator_id, provider="FRED", series_id=indicator_id.upper(),
        frequency=frequency, transform="level", baseline=baseline, db_path=db_path,
    )


def _seed_mapping(
    db_path: Path,
    industry_id: str,
    indicator_id: str,
    *,
    direction: str = "positive",
    weight: float = 1.0,
) -> None:
    repository.upsert_industry_indicator_map(
        industry_id=industry_id, indicator_id=indicator_id, direction=direction,
        weight=weight, valid_from="2020-01-01", db_path=db_path,
    )


def _seed_observation(db_path: Path, indicator_id: str, observed_at: str, value: float, known_at: str | None = None) -> None:
    repository.insert_indicator_observation(
        indicator_id=indicator_id, observed_at=observed_at, value=value,
        known_at=known_at or observed_at, vintage_at=known_at or observed_at, db_path=db_path,
    )


class NoIndicatorsMappedTests(unittest.TestCase):
    def test_no_mappings_yields_none_score_with_reason(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            db_path = Path(td) / "investment.db"
            _seed_industry(db_path)
            bundle = fundamentals_scoring.compute_fundamentals_score(
                "semiconductors", "2024-06-01", fundamentals_model_config=_MODEL_CONFIG, db_path=db_path
            )
        self.assertIsNone(bundle.score)
        self.assertEqual(bundle.reason, "no_indicators_mapped")
        self.assertEqual(bundle.data_completeness, 0.0)


class MissingObservationTests(unittest.TestCase):
    def test_indicator_with_no_observation_is_excluded_not_zero(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            db_path = Path(td) / "investment.db"
            _seed_industry(db_path)
            _seed_indicator(db_path, "ind_a")
            _seed_indicator(db_path, "ind_b")
            _seed_mapping(db_path, "semiconductors", "ind_a", weight=0.5)
            _seed_mapping(db_path, "semiconductors", "ind_b", weight=0.5)
            _seed_observation(db_path, "ind_a", "2024-06-01", 5.0)
            # ind_b has no observation at all -- must not be treated as 0.
            bundle = fundamentals_scoring.compute_fundamentals_score(
                "semiconductors", "2024-06-15", fundamentals_model_config=_MODEL_CONFIG, db_path=db_path
            )
        # only 1/2 components available -> below min_components=2 -> score None
        self.assertIsNone(bundle.score)
        self.assertIn("insufficient_data", bundle.reason)
        ind_b_evidence = next(e for e in bundle.evidence if e.indicator_id == "ind_b")
        self.assertFalse(ind_b_evidence.included)
        self.assertEqual(ind_b_evidence.reason, "no_observation_available")
        self.assertIsNone(ind_b_evidence.raw_value)


class DirectionAndBaselineTests(unittest.TestCase):
    def test_negative_direction_flips_a_high_raw_value_to_lower_the_score(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            db_path = Path(td) / "investment.db"
            _seed_industry(db_path)
            _seed_indicator(db_path, "inventory_yoy")
            _seed_indicator(db_path, "orders_yoy")
            _seed_mapping(db_path, "semiconductors", "inventory_yoy", direction="negative", weight=0.5)
            _seed_mapping(db_path, "semiconductors", "orders_yoy", direction="positive", weight=0.5)
            _seed_observation(db_path, "inventory_yoy", "2024-06-01", 20.0)  # bearish: big inventory build-up
            _seed_observation(db_path, "orders_yoy", "2024-06-01", 20.0)  # bullish: same magnitude, opposite meaning
            bundle = fundamentals_scoring.compute_fundamentals_score(
                "semiconductors", "2024-06-15", fundamentals_model_config=_MODEL_CONFIG, db_path=db_path
            )
        inv = next(e for e in bundle.evidence if e.indicator_id == "inventory_yoy")
        orders = next(e for e in bundle.evidence if e.indicator_id == "orders_yoy")
        self.assertEqual(inv.standardized_value, -20.0)
        self.assertEqual(orders.standardized_value, 20.0)
        # Equal-magnitude opposite-direction inputs cancel out -> neutral score.
        self.assertAlmostEqual(bundle.score, 50.0, places=6)

    def test_baseline_centers_a_diffusion_index_like_pmi(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            db_path = Path(td) / "investment.db"
            _seed_industry(db_path)
            _seed_indicator(db_path, "pmi", baseline=50.0)
            _seed_indicator(db_path, "orders_yoy")
            _seed_mapping(db_path, "semiconductors", "pmi", direction="positive", weight=0.5)
            _seed_mapping(db_path, "semiconductors", "orders_yoy", direction="positive", weight=0.5)
            _seed_observation(db_path, "pmi", "2024-06-01", 47.0)  # below-50 PMI is contractionary
            _seed_observation(db_path, "orders_yoy", "2024-06-01", 0.0)
            bundle = fundamentals_scoring.compute_fundamentals_score(
                "semiconductors", "2024-06-15", fundamentals_model_config=_MODEL_CONFIG, db_path=db_path
            )
        pmi_evidence = next(e for e in bundle.evidence if e.indicator_id == "pmi")
        self.assertEqual(pmi_evidence.raw_value, 47.0)
        self.assertEqual(pmi_evidence.standardized_value, -3.0)
        self.assertLess(bundle.score, 50.0)


class StalenessTests(unittest.TestCase):
    def test_observation_older_than_max_periods_is_excluded_as_stale(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            db_path = Path(td) / "investment.db"
            _seed_industry(db_path)
            _seed_indicator(db_path, "ind_a", frequency="monthly")
            _seed_indicator(db_path, "ind_b", frequency="monthly")
            _seed_mapping(db_path, "semiconductors", "ind_a", weight=0.5)
            _seed_mapping(db_path, "semiconductors", "ind_b", weight=0.5)
            _seed_observation(db_path, "ind_a", "2024-01-01", 5.0)  # 5 months old at as_of, max=3 -> stale
            _seed_observation(db_path, "ind_b", "2024-06-01", 5.0)
            bundle = fundamentals_scoring.compute_fundamentals_score(
                "semiconductors", "2024-06-15", fundamentals_model_config=_MODEL_CONFIG, db_path=db_path
            )
        ind_a = next(e for e in bundle.evidence if e.indicator_id == "ind_a")
        self.assertFalse(ind_a.included)
        self.assertIn("stale", ind_a.reason)

    def test_recent_observation_within_max_periods_is_included(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            db_path = Path(td) / "investment.db"
            _seed_industry(db_path)
            _seed_indicator(db_path, "ind_a", frequency="monthly")
            _seed_indicator(db_path, "ind_b", frequency="monthly")
            _seed_mapping(db_path, "semiconductors", "ind_a", weight=0.5)
            _seed_mapping(db_path, "semiconductors", "ind_b", weight=0.5)
            _seed_observation(db_path, "ind_a", "2024-05-15", 5.0)  # ~1 month old, within max=3
            _seed_observation(db_path, "ind_b", "2024-06-01", 5.0)
            bundle = fundamentals_scoring.compute_fundamentals_score(
                "semiconductors", "2024-06-15", fundamentals_model_config=_MODEL_CONFIG, db_path=db_path
            )
        ind_a = next(e for e in bundle.evidence if e.indicator_id == "ind_a")
        self.assertTrue(ind_a.included)
        self.assertIsNotNone(bundle.score)


class DataCompletenessTests(unittest.TestCase):
    def test_completeness_reflects_fraction_of_usable_weight(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            db_path = Path(td) / "investment.db"
            _seed_industry(db_path)
            for iid in ("a", "b", "c", "d"):
                _seed_indicator(db_path, iid)
                _seed_mapping(db_path, "semiconductors", iid, weight=1.0)
            _seed_observation(db_path, "a", "2024-06-01", 1.0)
            _seed_observation(db_path, "b", "2024-06-01", 1.0)
            _seed_observation(db_path, "c", "2024-06-01", 1.0)
            # d has no observation
            bundle = fundamentals_scoring.compute_fundamentals_score(
                "semiconductors", "2024-06-15", fundamentals_model_config=_MODEL_CONFIG, db_path=db_path
            )
        self.assertAlmostEqual(bundle.data_completeness, 0.75)


class NonPriceEvidenceTests(unittest.TestCase):
    def test_non_price_evidence_counts_only_included_indicators(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            db_path = Path(td) / "investment.db"
            _seed_industry(db_path)
            _seed_indicator(db_path, "a")
            _seed_indicator(db_path, "b")
            _seed_indicator(db_path, "c")
            _seed_mapping(db_path, "semiconductors", "a", weight=1.0)
            _seed_mapping(db_path, "semiconductors", "b", weight=1.0)
            _seed_mapping(db_path, "semiconductors", "c", weight=1.0)
            _seed_observation(db_path, "a", "2024-06-01", 1.0)
            _seed_observation(db_path, "b", "2024-06-01", 1.0)
            bundle = fundamentals_scoring.compute_fundamentals_score(
                "semiconductors", "2024-06-15", fundamentals_model_config=_MODEL_CONFIG, db_path=db_path
            )
        self.assertEqual(len(bundle.non_price_evidence()), 2)


class PointInTimeSafetyTests(unittest.TestCase):
    def test_observation_known_after_as_of_never_leaks_into_a_past_score(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            db_path = Path(td) / "investment.db"
            _seed_industry(db_path)
            _seed_indicator(db_path, "a")
            _seed_indicator(db_path, "b")
            _seed_mapping(db_path, "semiconductors", "a", weight=1.0)
            _seed_mapping(db_path, "semiconductors", "b", weight=1.0)
            _seed_observation(db_path, "a", "2024-06-01", 1.0, known_at="2024-06-05")
            # b's value becomes known only in the FUTURE relative to as_of below.
            _seed_observation(db_path, "b", "2024-06-01", 999.0, known_at="2024-12-01")
            bundle = fundamentals_scoring.compute_fundamentals_score(
                "semiconductors", "2024-06-15", fundamentals_model_config=_MODEL_CONFIG, db_path=db_path
            )
        b_evidence = next(e for e in bundle.evidence if e.indicator_id == "b")
        self.assertFalse(b_evidence.included)
        self.assertEqual(b_evidence.reason, "no_observation_available")


if __name__ == "__main__":
    unittest.main()
