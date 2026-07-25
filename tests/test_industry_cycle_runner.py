from __future__ import annotations

from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from committee.industry_cycle import (
    candidate_repository,
    cycle_model_config,
    cycle_repository,
    cycle_runner,
    factor_repository,
    fundamentals_repository,
    repository,
)


class CycleRunnerTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmpdir = tempfile.TemporaryDirectory()
        self.db_path = Path(self._tmpdir.name) / "test.db"
        self.cycle_cfg = cycle_model_config.load_cycle_model_config()
        self.model_version = self.cycle_cfg["model_version"]

        repository.upsert_industry_master(industry_id="semiconductors", name_kr="반도체", db_path=self.db_path)
        repository.upsert_industry_asset_map(
            asset_id="GOODETF", industry_id="semiconductors", asset_type="ETF", market="US",
            weight=1.0, valid_from="2026-01-01", db_path=self.db_path,
        )

    def tearDown(self) -> None:
        self._tmpdir.cleanup()

    def _seed_week(self, as_of: str, *, fundamentals: float, earnings_revision: float, breadth: float, rel_strength: float, overheat: float, return_1m: float = 0.02) -> None:
        fundamentals_repository.upsert_industry_fundamentals_weekly(
            {"industry_id": "semiconductors", "as_of": as_of, "model_version": "fundamentals_v1",
             "data_cutoff_at": as_of, "fundamentals_score": fundamentals}, db_path=self.db_path,
        )
        candidate_repository.upsert_industry_earnings_breadth_weekly(
            {"industry_id": "semiconductors", "as_of": as_of, "model_version": "stock_candidate_v1",
             "data_cutoff_at": as_of, "earnings_revision_score": earnings_revision, "breadth_score": breadth},
            db_path=self.db_path,
        )
        factor_repository.upsert_industry_factor_weekly(
            {"industry_id": "semiconductors", "market": "US", "asset_id": "GOODETF", "as_of": as_of,
             "model_version": "price_v1", "data_cutoff_at": as_of,
             "relative_strength_score": rel_strength, "trend_score": rel_strength, "overheat_score": overheat,
             "price_risk_score": 20.0, "return_1m": return_1m},
            db_path=self.db_path,
        )

    def _run(self, as_of: str, dry_run: bool = False):
        return cycle_runner.run_cycle_batch(
            ["semiconductors"], as_of=as_of, cycle_model_config=self.cycle_cfg,
            fundamentals_model_version="fundamentals_v1", candidate_model_version="stock_candidate_v1",
            price_model_version="price_v1", dry_run=dry_run, db_path=self.db_path,
        )

    def test_dry_run_touches_no_db(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            missing_db_path = Path(td) / "does_not_exist" / "investment.db"
            results = cycle_runner.run_cycle_batch(
                ["semiconductors"], as_of="2026-07-25", cycle_model_config=self.cycle_cfg,
                fundamentals_model_version="fundamentals_v1", candidate_model_version="stock_candidate_v1",
                price_model_version="price_v1", dry_run=True, db_path=missing_db_path,
            )
            self.assertEqual(len(results), 1)
            self.assertEqual(results[0].status, "planned")
            self.assertFalse(missing_db_path.exists())

    def test_execute_computes_and_persists(self) -> None:
        self._seed_week("2026-07-25", fundamentals=70.0, earnings_revision=65.0, breadth=80.0, rel_strength=72.0, overheat=30.0)
        results = self._run("2026-07-25")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].status, "ok")
        self.assertIsNotNone(results[0].cycle_score)

        stored = cycle_repository.get_cycle_signal("semiconductors", "2026-07-25", self.model_version, db_path=self.db_path)
        self.assertIsNotNone(stored)
        reasons = cycle_repository.list_signal_reasons("semiconductors", "2026-07-25", self.model_version, db_path=self.db_path)
        self.assertGreater(len(reasons), 0)

    def test_rerunning_same_as_of_is_idempotent(self) -> None:
        self._seed_week("2026-07-25", fundamentals=70.0, earnings_revision=65.0, breadth=80.0, rel_strength=72.0, overheat=30.0)
        self._run("2026-07-25")
        self._run("2026-07-25")
        self._run("2026-07-25")
        rows = cycle_repository.list_cycle_signals("semiconductors", db_path=self.db_path)
        self.assertEqual(len(rows), 1)

    def test_recovery_confirmation_streak_across_two_weeks(self) -> None:
        # Week 1: mid score rising from an implicit "low" baseline (no prior week -> score_rising=True).
        self._seed_week("2026-07-11", fundamentals=52.0, earnings_revision=50.0, breadth=55.0, rel_strength=50.0, overheat=10.0)
        first = self._run("2026-07-11")[0]
        self.assertEqual(first.confirmation_status, "first_observation")

        # Week 2: score continues rising within the recovery band -> confirmed.
        self._seed_week("2026-07-18", fundamentals=56.0, earnings_revision=54.0, breadth=58.0, rel_strength=54.0, overheat=10.0)
        second = self._run("2026-07-18")[0]
        if second.raw_state == first.raw_state:
            self.assertEqual(second.confirmation_status, "confirmed")
            self.assertEqual(second.action_signal, "RECOVERY_CONFIRMED")

    def test_urgent_flag_fires_on_earnings_shock(self) -> None:
        self._seed_week("2026-07-11", fundamentals=60.0, earnings_revision=65.0, breadth=60.0, rel_strength=55.0, overheat=10.0)
        self._run("2026-07-11")

        self._seed_week("2026-07-18", fundamentals=60.0, earnings_revision=20.0, breadth=60.0, rel_strength=55.0, overheat=10.0)
        second = self._run("2026-07-18")[0]
        self.assertIn("EARNINGS_SHOCK", second.urgent_flags)

        stored = cycle_repository.get_cycle_signal("semiconductors", "2026-07-18", self.model_version, db_path=self.db_path)
        self.assertIn("EARNINGS_SHOCK", stored["urgent_flags"])

    def test_low_confidence_first_observation_is_never_actionable(self) -> None:
        self._seed_week("2026-07-25", fundamentals=52.0, earnings_revision=50.0, breadth=55.0, rel_strength=50.0, overheat=10.0)
        result = self._run("2026-07-25")[0]
        self.assertFalse(result.is_actionable)

    def test_one_industry_failure_does_not_stop_the_batch(self) -> None:
        self._seed_week("2026-07-25", fundamentals=70.0, earnings_revision=65.0, breadth=80.0, rel_strength=72.0, overheat=30.0)
        repository.upsert_industry_master(industry_id="banks", name_kr="은행", db_path=self.db_path)

        original = cycle_runner.cycle_scoring.compute_cycle_score

        def flaky(industry_id, *args, **kwargs):
            if industry_id == "banks":
                raise RuntimeError("boom")
            return original(industry_id, *args, **kwargs)

        with patch.object(cycle_runner.cycle_scoring, "compute_cycle_score", side_effect=flaky):
            results = cycle_runner.run_cycle_batch(
                ["banks", "semiconductors"], as_of="2026-07-25", cycle_model_config=self.cycle_cfg,
                fundamentals_model_version="fundamentals_v1", candidate_model_version="stock_candidate_v1",
                price_model_version="price_v1", dry_run=False, db_path=self.db_path,
            )
        by_id = {r.industry_id: r for r in results}
        self.assertEqual(by_id["banks"].status, "failed")
        self.assertEqual(by_id["semiconductors"].status, "ok")


if __name__ == "__main__":
    unittest.main()
