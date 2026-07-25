from __future__ import annotations

from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from committee.industry_cycle import price_model_config, price_state_machine
from committee.industry_cycle.price_scoring import PriceScoreBundle, ScoreResult


def _scores(*, rs=None, tr=None, oh=None, risk=None) -> PriceScoreBundle:
    return PriceScoreBundle(
        relative_strength=ScoreResult(score=rs),
        trend=ScoreResult(score=tr),
        overheat=ScoreResult(score=oh),
        price_risk=ScoreResult(score=risk),
    )


class ClassifyRawStateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.thresholds = price_model_config.load_price_model_config()["state_thresholds"]

    def test_missing_relative_strength_or_trend_is_insufficient_data(self) -> None:
        self.assertEqual(
            price_state_machine.classify_raw_state(_scores(rs=None, tr=60, oh=30, risk=20), self.thresholds),
            price_state_machine.PRICE_ONLY_INSUFFICIENT_DATA,
        )
        self.assertEqual(
            price_state_machine.classify_raw_state(_scores(rs=60, tr=None, oh=30, risk=20), self.thresholds),
            price_state_machine.PRICE_ONLY_INSUFFICIENT_DATA,
        )

    def test_high_overheat_score_wins_regardless_of_other_scores(self) -> None:
        state = price_state_machine.classify_raw_state(_scores(rs=90, tr=90, oh=85, risk=10), self.thresholds)
        self.assertEqual(state, price_state_machine.PRICE_ONLY_OVERHEATED)

    def test_high_risk_and_weak_trend_is_deteriorating(self) -> None:
        state = price_state_machine.classify_raw_state(_scores(rs=30, tr=20, oh=10, risk=75), self.thresholds)
        self.assertEqual(state, price_state_machine.PRICE_ONLY_DETERIORATING)

    def test_high_relative_strength_and_trend_is_expansion(self) -> None:
        state = price_state_machine.classify_raw_state(_scores(rs=70, tr=70, oh=20, risk=10), self.thresholds)
        self.assertEqual(state, price_state_machine.PRICE_ONLY_EXPANSION)

    def test_mid_relative_strength_rising_with_good_trend_is_recovery_candidate(self) -> None:
        state = price_state_machine.classify_raw_state(
            _scores(rs=45, tr=55, oh=20, risk=10), self.thresholds, prev_relative_strength_score=30
        )
        self.assertEqual(state, price_state_machine.PRICE_ONLY_RECOVERY_CANDIDATE)

    def test_mid_relative_strength_falling_is_not_recovery_candidate(self) -> None:
        state = price_state_machine.classify_raw_state(
            _scores(rs=45, tr=55, oh=20, risk=10), self.thresholds, prev_relative_strength_score=60
        )
        self.assertNotEqual(state, price_state_machine.PRICE_ONLY_RECOVERY_CANDIDATE)

    def test_low_relative_strength_and_trend_is_weak(self) -> None:
        state = price_state_machine.classify_raw_state(_scores(rs=10, tr=10, oh=5, risk=20), self.thresholds)
        self.assertEqual(state, price_state_machine.PRICE_ONLY_WEAK)

    def test_no_prior_relative_strength_does_not_block_recovery_candidate(self) -> None:
        state = price_state_machine.classify_raw_state(
            _scores(rs=45, tr=55, oh=20, risk=10), self.thresholds, prev_relative_strength_score=None
        )
        self.assertEqual(state, price_state_machine.PRICE_ONLY_RECOVERY_CANDIDATE)

    def test_result_is_always_one_of_the_six_valid_states(self) -> None:
        for rs in (5, 20, 40, 55, 75, 95):
            for tr in (5, 20, 40, 55, 75, 95):
                state = price_state_machine.classify_raw_state(_scores(rs=rs, tr=tr, oh=10, risk=10), self.thresholds)
                self.assertIn(state, price_state_machine.VALID_PRICE_ONLY_STATES)


class ConfirmationRuleTests(unittest.TestCase):
    def setUp(self) -> None:
        self.confirmation_cfg = price_model_config.load_price_model_config()["confirmation"]

    def test_insufficient_data_is_always_held_and_never_carries_forward(self) -> None:
        previous = {"price_only_state": price_state_machine.PRICE_ONLY_EXPANSION, "consecutive_weeks": 5}
        result = price_state_machine.apply_confirmation_rule(
            price_state_machine.PRICE_ONLY_INSUFFICIENT_DATA, previous, confirmation_cfg=self.confirmation_cfg
        )
        self.assertEqual(result.confirmation_status, price_state_machine.STATUS_HELD)
        self.assertEqual(result.action_signal, price_state_machine.ACTION_HOLD_INSUFFICIENT_DATA)
        self.assertEqual(result.consecutive_weeks, 0)

    def test_recovery_candidate_first_week_is_first_observation_not_confirmed(self) -> None:
        result = price_state_machine.apply_confirmation_rule(
            price_state_machine.PRICE_ONLY_RECOVERY_CANDIDATE, None, confirmation_cfg=self.confirmation_cfg
        )
        self.assertEqual(result.confirmation_status, price_state_machine.STATUS_FIRST_OBSERVATION)
        self.assertEqual(result.action_signal, price_state_machine.ACTION_NONE)
        self.assertEqual(result.consecutive_weeks, 1)

    def test_recovery_candidate_confirmed_on_second_consecutive_week(self) -> None:
        previous = {"price_only_state": price_state_machine.PRICE_ONLY_RECOVERY_CANDIDATE, "consecutive_weeks": 1}
        result = price_state_machine.apply_confirmation_rule(
            price_state_machine.PRICE_ONLY_RECOVERY_CANDIDATE, previous, confirmation_cfg=self.confirmation_cfg
        )
        self.assertEqual(result.confirmation_status, price_state_machine.STATUS_CONFIRMED)
        self.assertEqual(result.action_signal, price_state_machine.ACTION_RECOVERY_CONFIRMED)
        self.assertEqual(result.consecutive_weeks, 2)

    def test_overheat_first_week_is_observation_second_week_is_warning(self) -> None:
        first = price_state_machine.apply_confirmation_rule(
            price_state_machine.PRICE_ONLY_OVERHEATED, None, confirmation_cfg=self.confirmation_cfg
        )
        self.assertEqual(first.confirmation_status, price_state_machine.STATUS_FIRST_OBSERVATION)
        self.assertEqual(first.action_signal, price_state_machine.ACTION_NONE)

        previous = {"price_only_state": price_state_machine.PRICE_ONLY_OVERHEATED, "consecutive_weeks": 1}
        second = price_state_machine.apply_confirmation_rule(
            price_state_machine.PRICE_ONLY_OVERHEATED, previous, confirmation_cfg=self.confirmation_cfg
        )
        self.assertEqual(second.confirmation_status, price_state_machine.STATUS_WARNING)
        self.assertEqual(second.action_signal, price_state_machine.ACTION_OVERHEAT_WARNING)

    def test_deteriorating_confirmed_on_second_consecutive_week(self) -> None:
        first = price_state_machine.apply_confirmation_rule(
            price_state_machine.PRICE_ONLY_DETERIORATING, None, confirmation_cfg=self.confirmation_cfg
        )
        self.assertEqual(first.confirmation_status, price_state_machine.STATUS_FIRST_OBSERVATION)

        previous = {"price_only_state": price_state_machine.PRICE_ONLY_DETERIORATING, "consecutive_weeks": 1}
        second = price_state_machine.apply_confirmation_rule(
            price_state_machine.PRICE_ONLY_DETERIORATING, previous, confirmation_cfg=self.confirmation_cfg
        )
        self.assertEqual(second.confirmation_status, price_state_machine.STATUS_CONFIRMED)
        self.assertEqual(second.action_signal, price_state_machine.ACTION_DETERIORATION_CONFIRMED)

    def test_streak_resets_when_state_changes(self) -> None:
        previous = {"price_only_state": price_state_machine.PRICE_ONLY_OVERHEATED, "consecutive_weeks": 3}
        result = price_state_machine.apply_confirmation_rule(
            price_state_machine.PRICE_ONLY_EXPANSION, previous, confirmation_cfg=self.confirmation_cfg
        )
        self.assertEqual(result.consecutive_weeks, 1)

    def test_streak_resets_after_a_data_gap_week(self) -> None:
        """A week of INSUFFICIENT_DATA breaks the streak: the *next* real
        week starts back at 1 even if the state before the gap matched."""
        previous_gap_row = {"price_only_state": price_state_machine.PRICE_ONLY_INSUFFICIENT_DATA, "consecutive_weeks": 0}
        result = price_state_machine.apply_confirmation_rule(
            price_state_machine.PRICE_ONLY_RECOVERY_CANDIDATE, previous_gap_row, confirmation_cfg=self.confirmation_cfg
        )
        self.assertEqual(result.consecutive_weeks, 1)
        self.assertEqual(result.confirmation_status, price_state_machine.STATUS_FIRST_OBSERVATION)

    def test_expansion_and_weak_are_not_applicable_for_confirmation(self) -> None:
        result = price_state_machine.apply_confirmation_rule(
            price_state_machine.PRICE_ONLY_EXPANSION, None, confirmation_cfg=self.confirmation_cfg
        )
        self.assertEqual(result.confirmation_status, price_state_machine.STATUS_NOT_APPLICABLE)
        self.assertEqual(result.action_signal, price_state_machine.ACTION_NONE)


if __name__ == "__main__":
    unittest.main()
