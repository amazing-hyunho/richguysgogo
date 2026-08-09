from __future__ import annotations

from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from committee.industry_cycle import cycle_model_config, cycle_state_machine as csm


class ClassifyRawCycleStateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.thresholds = cycle_model_config.load_cycle_model_config()["state_thresholds"]

    def test_none_score_is_insufficient_data(self) -> None:
        state = csm.classify_raw_cycle_state(None, 30.0, self.thresholds)
        self.assertEqual(state, csm.CYCLE_INSUFFICIENT_DATA)

    def test_high_score_and_high_overheat_is_overheated(self) -> None:
        state = csm.classify_raw_cycle_state(70.0, 80.0, self.thresholds)
        self.assertEqual(state, csm.CYCLE_OVERHEATED)

    def test_overheat_score_none_never_triggers_overheated(self) -> None:
        state = csm.classify_raw_cycle_state(70.0, None, self.thresholds, prev_cycle_score=68.0)
        self.assertNotEqual(state, csm.CYCLE_OVERHEATED)

    def test_sharp_negative_change_from_mid_score_is_slowing(self) -> None:
        state = csm.classify_raw_cycle_state(50.0, 10.0, self.thresholds, prev_cycle_score=55.0)
        self.assertEqual(state, csm.CYCLE_SLOWING)

    def test_sharp_negative_change_from_low_score_is_recession(self) -> None:
        state = csm.classify_raw_cycle_state(35.0, 10.0, self.thresholds, prev_cycle_score=40.0)
        self.assertEqual(state, csm.CYCLE_RECESSION)

    def test_low_score_with_no_prior_is_recession(self) -> None:
        state = csm.classify_raw_cycle_state(30.0, 5.0, self.thresholds)
        self.assertEqual(state, csm.CYCLE_RECESSION)

    def test_high_score_positive_change_is_expansion(self) -> None:
        state = csm.classify_raw_cycle_state(70.0, 20.0, self.thresholds, prev_cycle_score=68.0)
        self.assertEqual(state, csm.CYCLE_EXPANSION)

    def test_high_score_with_no_prior_is_expansion(self) -> None:
        state = csm.classify_raw_cycle_state(70.0, 20.0, self.thresholds)
        self.assertEqual(state, csm.CYCLE_EXPANSION)

    def test_mid_rising_score_is_recovery_early(self) -> None:
        state = csm.classify_raw_cycle_state(50.0, 20.0, self.thresholds, prev_cycle_score=46.0)
        self.assertEqual(state, csm.CYCLE_RECOVERY_EARLY)

    def test_mid_falling_score_is_not_recovery_early(self) -> None:
        state = csm.classify_raw_cycle_state(50.0, 20.0, self.thresholds, prev_cycle_score=58.0)
        self.assertNotEqual(state, csm.CYCLE_RECOVERY_EARLY)

    def test_result_is_always_one_of_the_valid_states(self) -> None:
        for score in (5.0, 20.0, 35.0, 45.0, 50.0, 55.0, 65.0, 80.0, 95.0):
            for prev in (None, 30.0, 50.0, 70.0):
                for overheat in (None, 10.0, 70.0):
                    state = csm.classify_raw_cycle_state(score, overheat, self.thresholds, prev_cycle_score=prev)
                    self.assertIn(state, csm.VALID_CYCLE_STATES)


class ApplyCycleConfirmationRuleTests(unittest.TestCase):
    def setUp(self) -> None:
        self.confirmation_cfg = cycle_model_config.load_cycle_model_config()["confirmation"]

    def test_insufficient_data_is_always_held_and_never_carries_forward(self) -> None:
        previous = {"raw_state": csm.CYCLE_EXPANSION, "consecutive_weeks": 5}
        result = csm.apply_cycle_confirmation_rule(
            csm.CYCLE_INSUFFICIENT_DATA, previous, confirmation_cfg=self.confirmation_cfg
        )
        self.assertEqual(result.confirmation_status, csm.STATUS_HELD)
        self.assertEqual(result.action_signal, csm.ACTION_HOLD_INSUFFICIENT_DATA)
        self.assertEqual(result.consecutive_weeks, 0)

    def test_recovery_early_first_week_is_first_observation(self) -> None:
        result = csm.apply_cycle_confirmation_rule(csm.CYCLE_RECOVERY_EARLY, None, confirmation_cfg=self.confirmation_cfg)
        self.assertEqual(result.confirmation_status, csm.STATUS_FIRST_OBSERVATION)
        self.assertEqual(result.consecutive_weeks, 1)

    def test_recovery_early_confirmed_on_second_consecutive_week(self) -> None:
        previous = {"raw_state": csm.CYCLE_RECOVERY_EARLY, "consecutive_weeks": 1}
        result = csm.apply_cycle_confirmation_rule(
            csm.CYCLE_RECOVERY_EARLY, previous, confirmation_cfg=self.confirmation_cfg
        )
        self.assertEqual(result.confirmation_status, csm.STATUS_CONFIRMED)
        self.assertEqual(result.action_signal, csm.ACTION_RECOVERY_CONFIRMED)
        self.assertEqual(result.consecutive_weeks, 2)

    def test_overheated_first_week_observation_second_week_warning(self) -> None:
        first = csm.apply_cycle_confirmation_rule(csm.CYCLE_OVERHEATED, None, confirmation_cfg=self.confirmation_cfg)
        self.assertEqual(first.confirmation_status, csm.STATUS_FIRST_OBSERVATION)

        previous = {"raw_state": csm.CYCLE_OVERHEATED, "consecutive_weeks": 1}
        second = csm.apply_cycle_confirmation_rule(csm.CYCLE_OVERHEATED, previous, confirmation_cfg=self.confirmation_cfg)
        self.assertEqual(second.confirmation_status, csm.STATUS_WARNING)
        self.assertEqual(second.action_signal, csm.ACTION_OVERHEAT_WARNING)

    def test_slowing_then_recession_confirmed_on_second_week(self) -> None:
        """A regime that changes raw label week to week between SLOWING/RECESSION
        (both deteriorating) still needs its own 2-week streak per label -- this
        documents that the streak resets, it doesn't silently merge the two."""
        first = csm.apply_cycle_confirmation_rule(csm.CYCLE_SLOWING, None, confirmation_cfg=self.confirmation_cfg)
        self.assertEqual(first.confirmation_status, csm.STATUS_FIRST_OBSERVATION)

        previous = {"raw_state": csm.CYCLE_SLOWING, "consecutive_weeks": 1}
        second = csm.apply_cycle_confirmation_rule(csm.CYCLE_SLOWING, previous, confirmation_cfg=self.confirmation_cfg)
        self.assertEqual(second.confirmation_status, csm.STATUS_CONFIRMED)
        self.assertEqual(second.action_signal, csm.ACTION_DETERIORATION_CONFIRMED)

    def test_streak_resets_when_state_changes(self) -> None:
        previous = {"raw_state": csm.CYCLE_OVERHEATED, "consecutive_weeks": 3}
        result = csm.apply_cycle_confirmation_rule(csm.CYCLE_EXPANSION, previous, confirmation_cfg=self.confirmation_cfg)
        self.assertEqual(result.consecutive_weeks, 1)

    def test_streak_resets_after_a_data_gap_week(self) -> None:
        previous_gap_row = {"raw_state": csm.CYCLE_INSUFFICIENT_DATA, "consecutive_weeks": 0}
        result = csm.apply_cycle_confirmation_rule(
            csm.CYCLE_RECOVERY_EARLY, previous_gap_row, confirmation_cfg=self.confirmation_cfg
        )
        self.assertEqual(result.consecutive_weeks, 1)
        self.assertEqual(result.confirmation_status, csm.STATUS_FIRST_OBSERVATION)

    def test_expansion_confirms_on_second_consecutive_week(self) -> None:
        first = csm.apply_cycle_confirmation_rule(
            csm.CYCLE_EXPANSION, None, confirmation_cfg=self.confirmation_cfg
        )
        self.assertEqual(first.confirmation_status, csm.STATUS_FIRST_OBSERVATION)
        second = csm.apply_cycle_confirmation_rule(
            csm.CYCLE_EXPANSION,
            {"raw_state": csm.CYCLE_EXPANSION, "consecutive_weeks": 1},
            confirmation_cfg=self.confirmation_cfg,
        )
        self.assertEqual(second.confirmation_status, csm.STATUS_CONFIRMED)
        self.assertEqual(second.action_signal, csm.ACTION_EXPANSION_CONFIRMED)


if __name__ == "__main__":
    unittest.main()
