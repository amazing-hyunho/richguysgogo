from __future__ import annotations

from pathlib import Path
import unittest

from committee.agents.llm_chair import LLMChairAgent


ROOT = Path(__file__).resolve().parents[1]


class LLMChairFutureEconomyContextTests(unittest.TestCase):
    def test_system_prompt_treats_future_context_as_research_not_order(self) -> None:
        prompt = LLMChairAgent._system_prompt()
        self.assertIn("FUTURE ECONOMY CONTEXT RULE", prompt)
        self.assertIn("not current market signals or trading orders", prompt)
        self.assertIn("never invent", prompt)

    def test_user_prompt_loads_bounded_verified_agenda(self) -> None:
        source = (ROOT / "committee" / "agents" / "llm_chair.py").read_text(encoding="utf-8")
        self.assertIn('payload["future_economy_context"]', source)
        self.assertIn("load_latest_committee_agenda", source)
        self.assertIn("max_age_days=14", source)


if __name__ == "__main__":
    unittest.main()
