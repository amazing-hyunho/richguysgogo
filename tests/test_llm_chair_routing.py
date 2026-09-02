from __future__ import annotations

from datetime import date
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from committee.agents.llm_chair import ChairLLMOptions, select_chair_model
from committee.core.snapshot_builder import build_dummy_snapshot
from committee.schemas.stance import AgentName, ConfidenceLevel, RegimeTag, Stance


def _stance(agent_name: AgentName, regime_tag: RegimeTag) -> Stance:
    return Stance(
        agent_name=agent_name,
        core_claims=["테스트 판단입니다."],
        korean_comment="테스트용 의견입니다.",
        regime_tag=regime_tag,
        evidence_ids=["snapshot.market_summary.kospi_change_pct"],
        confidence=ConfidenceLevel.MED,
    )


class ChairModelRoutingTests(unittest.TestCase):
    def setUp(self) -> None:
        self.snapshot = build_dummy_snapshot(date(2026, 8, 24))
        self.options = ChairLLMOptions()

    def test_routine_day_uses_terra(self) -> None:
        selection = select_chair_model(
            snapshot=self.snapshot,
            stances=[_stance(AgentName.MACRO, RegimeTag.NEUTRAL)],
            debate_round=None,
            options=self.options,
        )

        self.assertFalse(selection.escalated)
        self.assertEqual(selection.model, "gpt-5.6-terra")
        self.assertEqual(selection.reasoning_effort, "medium")
        self.assertEqual(selection.reasons, ())

    def test_opposing_agent_regimes_escalate_to_sol(self) -> None:
        selection = select_chair_model(
            snapshot=self.snapshot,
            stances=[
                _stance(AgentName.MACRO, RegimeTag.RISK_ON),
                _stance(AgentName.RISK, RegimeTag.RISK_OFF),
            ],
            debate_round=None,
            options=self.options,
        )

        self.assertTrue(selection.escalated)
        self.assertEqual(selection.model, "gpt-5.6-sol")
        self.assertIn("agent_regime_conflict", selection.reasons)

    def test_market_shock_escalates_to_sol(self) -> None:
        self.snapshot.markets.volatility.vix = 35.0
        self.snapshot.markets.kr.kospi_pct = -3.2
        self.snapshot.market_summary.kospi_change_pct = -3.2

        selection = select_chair_model(
            snapshot=self.snapshot,
            stances=[],
            debate_round=None,
            options=self.options,
        )

        self.assertEqual(selection.model, "gpt-5.6-sol")
        self.assertIn("vix_stress", selection.reasons)
        self.assertIn("kospi_shock", selection.reasons)

    def test_monthly_mode_escalates_without_market_stress(self) -> None:
        selection = select_chair_model(
            snapshot=self.snapshot,
            stances=[],
            debate_round=None,
            options=ChairLLMOptions(report_mode="monthly"),
        )

        self.assertEqual(selection.model, "gpt-5.6-sol")
        self.assertEqual(selection.reasons, ("monthly_report",))

    def test_environment_policy_defaults_and_manual_override(self) -> None:
        env = {
            "CHAIR_OPENAI_MODEL": "gpt-5.6-terra",
            "CHAIR_ESCALATION_MODEL": "gpt-5.6-sol",
            "CHAIR_REASONING_EFFORT": "medium",
            "CHAIR_ESCALATION_REASONING_EFFORT": "high",
            "CHAIR_FORCE_SOL": "1",
        }
        with patch.dict("os.environ", env, clear=True):
            options = ChairLLMOptions.from_env()

        self.assertEqual(options.model, "gpt-5.6-terra")
        self.assertEqual(options.escalation_model, "gpt-5.6-sol")
        self.assertEqual(options.reasoning_effort, "medium")
        self.assertEqual(options.escalation_reasoning_effort, "high")
        self.assertTrue(options.force_escalation)
        self.assertEqual(options.timeout_sec, 180)
        self.assertEqual(options.same_model_retries, 1)
        self.assertEqual(options.retry_model, "gpt-5.6-luna")
        self.assertEqual(options.retry_reasoning_effort, "low")


if __name__ == "__main__":
    unittest.main()
