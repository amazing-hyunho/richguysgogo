from __future__ import annotations

from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from committee.industry_cycle import cycle_model_config, urgent_alerts as ua


class DetectUrgentFlagsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.cfg = cycle_model_config.load_cycle_model_config()["urgent_alert"]

    def _base_kwargs(self, **overrides):
        base = dict(
            earnings_revision_score=60.0,
            breadth_score=60.0,
            return_1m=0.02,
            confidence=0.6,
            prev_earnings_revision_score=60.0,
            prev_confidence=0.6,
            urgent_alert_cfg=self.cfg,
        )
        base.update(overrides)
        return base

    def test_no_flags_when_nothing_changed(self) -> None:
        flags = ua.detect_urgent_flags(**self._base_kwargs())
        self.assertEqual(flags, [])

    def test_earnings_shock_fires_on_sharp_drop(self) -> None:
        flags = ua.detect_urgent_flags(**self._base_kwargs(earnings_revision_score=30.0, prev_earnings_revision_score=60.0))
        self.assertIn(ua.EARNINGS_SHOCK, flags)

    def test_earnings_shock_does_not_fire_without_prior_week(self) -> None:
        flags = ua.detect_urgent_flags(**self._base_kwargs(earnings_revision_score=10.0, prev_earnings_revision_score=None))
        self.assertNotIn(ua.EARNINGS_SHOCK, flags)

    def test_price_crash_fires_on_deep_negative_return(self) -> None:
        flags = ua.detect_urgent_flags(**self._base_kwargs(return_1m=-0.20))
        self.assertIn(ua.PRICE_CRASH, flags)

    def test_price_crash_does_not_fire_on_mild_decline(self) -> None:
        flags = ua.detect_urgent_flags(**self._base_kwargs(return_1m=-0.03))
        self.assertNotIn(ua.PRICE_CRASH, flags)

    def test_breadth_collapse_fires_on_low_breadth(self) -> None:
        flags = ua.detect_urgent_flags(**self._base_kwargs(breadth_score=5.0))
        self.assertIn(ua.BREADTH_COLLAPSE, flags)

    def test_confidence_collapse_fires_on_sharp_drop(self) -> None:
        flags = ua.detect_urgent_flags(**self._base_kwargs(confidence=0.2, prev_confidence=0.6))
        self.assertIn(ua.CONFIDENCE_COLLAPSE, flags)

    def test_confidence_collapse_does_not_fire_without_prior_week(self) -> None:
        flags = ua.detect_urgent_flags(**self._base_kwargs(confidence=0.2, prev_confidence=None))
        self.assertNotIn(ua.CONFIDENCE_COLLAPSE, flags)

    def test_multiple_flags_can_fire_simultaneously(self) -> None:
        flags = ua.detect_urgent_flags(
            **self._base_kwargs(
                earnings_revision_score=20.0, prev_earnings_revision_score=60.0,
                return_1m=-0.25, breadth_score=2.0,
            )
        )
        self.assertIn(ua.EARNINGS_SHOCK, flags)
        self.assertIn(ua.PRICE_CRASH, flags)
        self.assertIn(ua.BREADTH_COLLAPSE, flags)

    def test_all_none_inputs_produce_no_flags(self) -> None:
        flags = ua.detect_urgent_flags(
            earnings_revision_score=None, breadth_score=None, return_1m=None, confidence=None,
            prev_earnings_revision_score=None, prev_confidence=None, urgent_alert_cfg=self.cfg,
        )
        self.assertEqual(flags, [])


if __name__ == "__main__":
    unittest.main()
