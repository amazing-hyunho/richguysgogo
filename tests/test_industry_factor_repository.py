from __future__ import annotations

from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from committee.industry_cycle import factor_repository


def _factor_record(**overrides):
    defaults = dict(
        industry_id="semiconductors",
        market="US",
        asset_id="SOXX",
        benchmark_asset_id="SP500",
        as_of="2026-07-24",
        price_trade_date="2026-07-24",
        model_version="price_only_v1",
        data_cutoff_at="2026-07-24",
        data_completeness=0.9,
        relative_strength_score=65.0,
        trend_score=70.0,
        overheat_score=40.0,
        price_risk_score=30.0,
        score_breakdown={"relative_strength": {"score": 65.0}},
    )
    defaults.update(overrides)
    return defaults


class FactorWeeklyUpsertTests(unittest.TestCase):
    def test_rerunning_same_key_is_idempotent(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            db_path = Path(td) / "investment.db"
            for _ in range(3):
                factor_repository.upsert_industry_factor_weekly(_factor_record(), db_path=db_path)
            rows = factor_repository.list_factor_weekly("SOXX", db_path=db_path)
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["relative_strength_score"], 65.0)

    def test_rerun_with_changed_values_overwrites_in_place(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            db_path = Path(td) / "investment.db"
            factor_repository.upsert_industry_factor_weekly(_factor_record(relative_strength_score=65.0), db_path=db_path)
            factor_repository.upsert_industry_factor_weekly(_factor_record(relative_strength_score=72.0), db_path=db_path)
            rows = factor_repository.list_factor_weekly("SOXX", db_path=db_path)
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["relative_strength_score"], 72.0)

    def test_different_model_version_creates_a_new_row_preserving_old_one(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            db_path = Path(td) / "investment.db"
            factor_repository.upsert_industry_factor_weekly(
                _factor_record(model_version="price_only_v1", relative_strength_score=65.0), db_path=db_path
            )
            factor_repository.upsert_industry_factor_weekly(
                _factor_record(model_version="price_only_v2", relative_strength_score=80.0), db_path=db_path
            )
            rows = factor_repository.list_factor_weekly("SOXX", db_path=db_path)
            self.assertEqual(len(rows), 2)
            by_version = {r["model_version"]: r for r in rows}
            self.assertEqual(by_version["price_only_v1"]["relative_strength_score"], 65.0)
            self.assertEqual(by_version["price_only_v2"]["relative_strength_score"], 80.0)

    def test_missing_score_is_stored_as_null_not_zero(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            db_path = Path(td) / "investment.db"
            factor_repository.upsert_industry_factor_weekly(
                _factor_record(relative_strength_score=None, trend_score=None), db_path=db_path
            )
            row = factor_repository.get_factor_weekly("SOXX", "2026-07-24", "price_only_v1", db_path=db_path)
            self.assertIsNone(row["relative_strength_score"])
            self.assertIsNone(row["trend_score"])

    def test_score_breakdown_is_json_encoded(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            db_path = Path(td) / "investment.db"
            factor_repository.upsert_industry_factor_weekly(_factor_record(), db_path=db_path)
            row = factor_repository.get_factor_weekly("SOXX", "2026-07-24", "price_only_v1", db_path=db_path)
            import json

            decoded = json.loads(row["score_breakdown_json"])
            self.assertIn("relative_strength", decoded)

    def test_missing_required_field_raises(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            db_path = Path(td) / "investment.db"
            record = _factor_record()
            del record["industry_id"]
            with self.assertRaises(ValueError):
                factor_repository.upsert_industry_factor_weekly(record, db_path=db_path)

    def test_get_latest_factor_before_returns_most_recent_prior_row(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            db_path = Path(td) / "investment.db"
            factor_repository.upsert_industry_factor_weekly(
                _factor_record(as_of="2026-07-10", relative_strength_score=40.0), db_path=db_path
            )
            factor_repository.upsert_industry_factor_weekly(
                _factor_record(as_of="2026-07-17", relative_strength_score=50.0), db_path=db_path
            )
            prev = factor_repository.get_latest_factor_before("SOXX", "price_only_v1", "2026-07-24", db_path=db_path)
            self.assertEqual(prev["as_of"], "2026-07-17")
            self.assertEqual(prev["relative_strength_score"], 50.0)

    def test_get_latest_factor_before_is_none_when_no_prior_row(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            db_path = Path(td) / "investment.db"
            self.assertIsNone(
                factor_repository.get_latest_factor_before("SOXX", "price_only_v1", "2026-07-24", db_path=db_path)
            )


def _state_record(**overrides):
    defaults = dict(
        industry_id="semiconductors",
        market="US",
        asset_id="SOXX",
        as_of="2026-07-24",
        model_version="price_only_v1",
        price_only_state="PRICE_ONLY_RECOVERY_CANDIDATE",
        confirmation_status="first_observation",
        action_signal="NONE",
        consecutive_weeks=1,
        previous_state=None,
        data_completeness=0.9,
        contributing_factors={"relative_strength": {"score": 45.0}},
    )
    defaults.update(overrides)
    return defaults


class PriceStateWeeklyUpsertTests(unittest.TestCase):
    def test_rerunning_same_key_is_idempotent(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            db_path = Path(td) / "investment.db"
            for _ in range(3):
                factor_repository.upsert_price_state_weekly(_state_record(), db_path=db_path)
            rows = factor_repository.list_price_state_weekly("SOXX", db_path=db_path)
            self.assertEqual(len(rows), 1)

    def test_different_model_version_preserves_old_state_row(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            db_path = Path(td) / "investment.db"
            factor_repository.upsert_price_state_weekly(
                _state_record(model_version="price_only_v1", price_only_state="PRICE_ONLY_WEAK"), db_path=db_path
            )
            factor_repository.upsert_price_state_weekly(
                _state_record(model_version="price_only_v2", price_only_state="PRICE_ONLY_EXPANSION"), db_path=db_path
            )
            rows = factor_repository.list_price_state_weekly("SOXX", db_path=db_path)
            self.assertEqual(len(rows), 2)
            by_version = {r["model_version"]: r for r in rows}
            self.assertEqual(by_version["price_only_v1"]["price_only_state"], "PRICE_ONLY_WEAK")
            self.assertEqual(by_version["price_only_v2"]["price_only_state"], "PRICE_ONLY_EXPANSION")

    def test_get_latest_price_state_before_returns_most_recent_prior_row(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            db_path = Path(td) / "investment.db"
            factor_repository.upsert_price_state_weekly(
                _state_record(as_of="2026-07-10", consecutive_weeks=1), db_path=db_path
            )
            factor_repository.upsert_price_state_weekly(
                _state_record(as_of="2026-07-17", consecutive_weeks=2), db_path=db_path
            )
            prev = factor_repository.get_latest_price_state_before(
                "SOXX", "price_only_v1", "2026-07-24", db_path=db_path
            )
            self.assertEqual(prev["as_of"], "2026-07-17")
            self.assertEqual(prev["consecutive_weeks"], 2)

    def test_missing_required_field_raises(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            db_path = Path(td) / "investment.db"
            record = _state_record()
            del record["price_only_state"]
            with self.assertRaises(ValueError):
                factor_repository.upsert_price_state_weekly(record, db_path=db_path)


def _performance_record(**overrides):
    defaults = dict(
        industry_id="semiconductors",
        market="US",
        asset_id="SOXX",
        benchmark_asset_id="SP500",
        signal_at="2026-01-05",
        signal_state="PRICE_ONLY_RECOVERY_CANDIDATE",
        model_version="price_only_v1",
        horizon_label="6m",
        horizon_trading_days=126,
        asset_return=0.15,
        benchmark_return=0.05,
        excess_return=0.10,
        mfe=0.20,
        mae=-0.03,
    )
    defaults.update(overrides)
    return defaults


class PriceSignalPerformanceTests(unittest.TestCase):
    def test_rerunning_same_key_is_idempotent(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            db_path = Path(td) / "investment.db"
            for _ in range(3):
                factor_repository.upsert_price_signal_performance(_performance_record(), db_path=db_path)
            rows = factor_repository.list_price_signal_performance("SOXX", db_path=db_path)
            self.assertEqual(len(rows), 1)

    def test_bulk_upsert_multiple_horizons(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            db_path = Path(td) / "investment.db"
            records = [
                _performance_record(horizon_label="1m", excess_return=0.02),
                _performance_record(horizon_label="3m", excess_return=0.05),
                _performance_record(horizon_label="6m", excess_return=0.10),
            ]
            written = factor_repository.bulk_upsert_price_signal_performance(records, db_path=db_path)
            self.assertEqual(written, 3)
            rows = factor_repository.list_price_signal_performance("SOXX", db_path=db_path)
            self.assertEqual(len(rows), 3)

    def test_different_model_version_preserves_old_performance_row(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            db_path = Path(td) / "investment.db"
            factor_repository.upsert_price_signal_performance(
                _performance_record(model_version="price_only_v1", excess_return=0.10), db_path=db_path
            )
            factor_repository.upsert_price_signal_performance(
                _performance_record(model_version="price_only_v2", excess_return=0.20), db_path=db_path
            )
            rows = factor_repository.list_price_signal_performance("SOXX", db_path=db_path)
            self.assertEqual(len(rows), 2)


if __name__ == "__main__":
    unittest.main()
