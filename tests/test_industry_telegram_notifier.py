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
    cycle_repository,
    telegram_dispatch_repository,
    telegram_notifier,
)


def _signal(industry_id: str, **overrides):
    base = {
        "industry_id": industry_id,
        "as_of": "2026-07-25",
        "model_version": "cycle_v1",
        "cycle_score": 55.0,
        "raw_state": "CYCLE_RECOVERY_EARLY",
        "confirmed_state": None,
        "confirmation_status": "first_observation",
        "action_signal": "NONE",
        "consecutive_weeks": 1,
        "previous_confirmed_state": None,
        "urgent_flags": [],
    }
    base.update(overrides)
    return base


class ClassifyWeeklyGroupsTests(unittest.TestCase):
    def test_newly_confirmed_recovery(self) -> None:
        s = _signal("semiconductors", confirmation_status="confirmed", consecutive_weeks=2)
        groups = telegram_notifier.classify_weekly_groups([s], weeks_required_recovery=2)
        self.assertEqual(groups["newly_confirmed_recovery"], [s])

    def test_recovery_maintained_after_threshold(self) -> None:
        s = _signal("semiconductors", confirmation_status="confirmed", consecutive_weeks=3)
        groups = telegram_notifier.classify_weekly_groups([s], weeks_required_recovery=2)
        self.assertEqual(groups["recovery_maintained"], [s])

    def test_recovery_released(self) -> None:
        s = _signal(
            "semiconductors", raw_state="CYCLE_SLOWING", confirmation_status="first_observation",
            confirmed_state=None, previous_confirmed_state="CYCLE_RECOVERY_EARLY",
        )
        groups = telegram_notifier.classify_weekly_groups([s], weeks_required_recovery=2)
        self.assertEqual(groups["recovery_released"], [s])

    def test_overheat_warning(self) -> None:
        s = _signal("semiconductors", raw_state="CYCLE_OVERHEATED", confirmation_status="warning")
        groups = telegram_notifier.classify_weekly_groups([s], weeks_required_recovery=2)
        self.assertEqual(groups["overheat_warning"], [s])

    def test_deterioration_confirmed(self) -> None:
        s = _signal("semiconductors", raw_state="CYCLE_RECESSION", confirmation_status="confirmed")
        groups = telegram_notifier.classify_weekly_groups([s], weeks_required_recovery=2)
        self.assertEqual(groups["deterioration_confirmed"], [s])

    def test_insufficient_data_bucket(self) -> None:
        s = _signal("semiconductors", raw_state="CYCLE_INSUFFICIENT_DATA", confirmation_status="held")
        groups = telegram_notifier.classify_weekly_groups([s], weeks_required_recovery=2)
        self.assertEqual(groups["no_recommendation_or_insufficient_data"], [s])

    def test_every_signal_lands_in_exactly_one_group(self) -> None:
        signals = [
            _signal("a", confirmation_status="confirmed", consecutive_weeks=2),
            _signal("b", raw_state="CYCLE_OVERHEATED", confirmation_status="warning"),
            _signal("c", raw_state="CYCLE_RECESSION", confirmation_status="confirmed"),
            _signal("d", raw_state="CYCLE_INSUFFICIENT_DATA", confirmation_status="held"),
            _signal("e", raw_state="CYCLE_EXPANSION", confirmation_status="not_applicable"),
        ]
        groups = telegram_notifier.classify_weekly_groups(signals, weeks_required_recovery=2)
        total = sum(len(v) for v in groups.values())
        self.assertEqual(total, len(signals))


class ComposeMessageTests(unittest.TestCase):
    def test_compose_weekly_message_mentions_industry_and_no_signal_fallback(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            db_path = Path(tmp) / "test.db"
            s = _signal("semiconductors", raw_state="CYCLE_EXPANSION", confirmation_status="not_applicable")
            msg = telegram_notifier.compose_weekly_message(
                [s], as_of="2026-07-25", weeks_required_recovery=2, db_path=db_path
            )
            self.assertIn("semiconductors", msg)
            self.assertIn("2026-07-25", msg)

    def test_compose_urgent_message_lists_flags(self) -> None:
        s = _signal("semiconductors", urgent_flags=["PRICE_CRASH", "EARNINGS_SHOCK"])
        msg = telegram_notifier.compose_urgent_message(s)
        self.assertIn("PRICE_CRASH", msg)
        self.assertIn("EARNINGS_SHOCK", msg)
        self.assertIn("semiconductors", msg)

    def test_compose_weekly_message_labels_ai_summary_as_non_authoritative(self) -> None:
        msg = telegram_notifier.compose_weekly_message(
            [_signal("semiconductors")],
            as_of="2026-07-25",
            weeks_required_recovery=2,
            ai_summary="산업 전반의 정량 신호는 혼조입니다.",
        )
        self.assertIn("[AI 조건부 해설]", msg)
        self.assertIn("정량 신호를 변경하지 않는", msg)


class SendWeeklyDigestTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmpdir = tempfile.TemporaryDirectory()
        self.db_path = Path(self._tmpdir.name) / "test.db"
        cycle_repository.upsert_industry_cycle_signal(
            {
                "industry_id": "semiconductors", "as_of": "2026-07-25", "model_version": "cycle_v1",
                "data_cutoff_at": "2026-07-25", "cycle_score": 70.0, "raw_state": "CYCLE_EXPANSION",
                "confirmation_status": "not_applicable", "urgent_flags": [],
            },
            db_path=self.db_path,
        )

    def tearDown(self) -> None:
        self._tmpdir.cleanup()

    def test_no_signals_returns_none(self) -> None:
        result = telegram_notifier.send_weekly_digest(
            "2099-01-01", "cycle_v1", weeks_required_recovery=2, db_path=self.db_path, dry_run=True
        )
        self.assertIsNone(result)

    def test_dry_run_never_records_dispatch_or_sends(self) -> None:
        with patch("committee.industry_cycle.telegram_notifier.send_report") as mock_send:
            msg = telegram_notifier.send_weekly_digest(
                "2026-07-25", "cycle_v1", weeks_required_recovery=2, db_path=self.db_path, dry_run=True
            )
        self.assertIsNotNone(msg)
        mock_send.assert_not_called()
        self.assertFalse(
            telegram_dispatch_repository.has_been_dispatched(
                telegram_notifier.WEEKLY_ALERT_TYPE, "2026-07-25", "cycle_v1", "weekly", db_path=self.db_path
            )
        )

    def test_execute_sends_once_and_dedups_on_rerun(self) -> None:
        with patch("committee.industry_cycle.telegram_notifier.send_report") as mock_send:
            telegram_notifier.send_weekly_digest(
                "2026-07-25", "cycle_v1", weeks_required_recovery=2, db_path=self.db_path, dry_run=False
            )
            telegram_notifier.send_weekly_digest(
                "2026-07-25", "cycle_v1", weeks_required_recovery=2, db_path=self.db_path, dry_run=False
            )
        self.assertEqual(mock_send.call_count, 1)


class SendUrgentAlertsTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmpdir = tempfile.TemporaryDirectory()
        self.db_path = Path(self._tmpdir.name) / "test.db"
        cycle_repository.upsert_industry_cycle_signal(
            {
                "industry_id": "semiconductors", "as_of": "2026-07-25", "model_version": "cycle_v1",
                "data_cutoff_at": "2026-07-25", "cycle_score": 30.0, "raw_state": "CYCLE_RECESSION",
                "confirmation_status": "confirmed", "urgent_flags": ["PRICE_CRASH"],
            },
            db_path=self.db_path,
        )
        cycle_repository.upsert_industry_cycle_signal(
            {
                "industry_id": "banks", "as_of": "2026-07-25", "model_version": "cycle_v1",
                "data_cutoff_at": "2026-07-25", "cycle_score": 60.0, "raw_state": "CYCLE_EXPANSION",
                "confirmation_status": "not_applicable", "urgent_flags": [],
            },
            db_path=self.db_path,
        )

    def tearDown(self) -> None:
        self._tmpdir.cleanup()

    def test_only_flagged_industries_produce_messages(self) -> None:
        with patch("committee.industry_cycle.telegram_notifier.send_report"):
            sent = telegram_notifier.send_urgent_alerts("2026-07-25", "cycle_v1", db_path=self.db_path, dry_run=False)
        self.assertEqual(len(sent), 1)
        self.assertIn("semiconductors", sent[0])

    def test_rerunning_does_not_resend_same_flag(self) -> None:
        with patch("committee.industry_cycle.telegram_notifier.send_report") as mock_send:
            telegram_notifier.send_urgent_alerts("2026-07-25", "cycle_v1", db_path=self.db_path, dry_run=False)
            telegram_notifier.send_urgent_alerts("2026-07-25", "cycle_v1", db_path=self.db_path, dry_run=False)
        self.assertEqual(mock_send.call_count, 1)

    def test_dry_run_never_touches_dispatch_log(self) -> None:
        with patch("committee.industry_cycle.telegram_notifier.send_report") as mock_send:
            telegram_notifier.send_urgent_alerts("2026-07-25", "cycle_v1", db_path=self.db_path, dry_run=True)
        mock_send.assert_not_called()
        self.assertFalse(
            telegram_dispatch_repository.has_been_dispatched(
                "semiconductors", "2026-07-25", "cycle_v1", "PRICE_CRASH", db_path=self.db_path
            )
        )


if __name__ == "__main__":
    unittest.main()
