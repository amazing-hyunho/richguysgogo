from __future__ import annotations

from datetime import date
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from committee.agents.chair_stub import ChairStub
from committee.agents.llm_chair import ChairLLMOptions, LLMChairAgent
from committee.core.snapshot_builder import build_dummy_snapshot
from committee.schemas.committee_result import AnalysisStatus
from committee.schemas.stance import AgentName, ConfidenceLevel, RegimeTag, Stance
from committee.tools.openai_chat import ChatCompletionResult, OpenAIConfig


def _stance() -> Stance:
    return Stance(
        agent_name=AgentName.MACRO,
        core_claims=["테스트 판단입니다."],
        korean_comment="테스트 의견입니다.",
        regime_tag=RegimeTag.NEUTRAL,
        evidence_ids=["snapshot.market_summary.kospi_change_pct"],
        confidence=ConfidenceLevel.MED,
    )


def _response(*, empty_minority_agents: bool = False) -> ChatCompletionResult:
    payload = {
        "consensus": "위원회는 중립 국면을 유지합니다.",
        "key_points": [
            {"point": "수급과 거시 신호가 엇갈립니다.", "sources": ["flow_data"]}
        ],
        "disagreements": [
            {
                "topic": "국면 판단",
                "majority": "중립",
                "minority": "방어",
                "minority_agents": [] if empty_minority_agents else ["risk"],
                "why_it_matters": "위험 한도에 영향을 줍니다.",
            }
        ],
        "ops_guidance": [
            {"level": "OK", "text": "균형 노출을 유지합니다."},
            {"level": "CAUTION", "text": "환율을 확인합니다."},
            {"level": "AVOID", "text": "과도한 레버리지를 피합니다."},
        ],
        "sugeup_narrative": "## 오늘의 흐름\n\n수급과 거시 신호를 함께 확인합니다.",
    }
    return ChatCompletionResult(
        content=json.dumps(payload, ensure_ascii=False),
        model="gpt-5.6-terra",
        input_tokens=100,
        output_tokens=200,
        request_id="req_test",
    )


class LLMChairResilienceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.snapshot = build_dummy_snapshot(date(2026, 9, 2))
        self.stances = [_stance()]

    def _agent(self, **overrides: object) -> LLMChairAgent:
        options = ChairLLMOptions(
            timeout_sec=180,
            same_model_retries=1,
            retry_model="gpt-5.6-luna",
            retry_reasoning_effort="low",
            **overrides,
        )
        return LLMChairAgent(fallback_agent=ChairStub(), options=options)

    @patch("committee.agents.llm_chair.load_openai_config")
    @patch("committee.agents.llm_chair.responses_completion_with_metadata")
    def test_empty_minority_agents_is_repaired(
        self,
        completion: Mock,
        load_config: Mock,
    ) -> None:
        load_config.return_value = OpenAIConfig(api_key="test")
        completion.return_value = _response(empty_minority_agents=True)

        result = self._agent().run(self.snapshot, self.stances)

        self.assertEqual(result.analysis_status, AnalysisStatus.RECOVERED)
        self.assertEqual(result.disagreements[0].minority_agents, ["출처 미지정"])
        self.assertIn("형식 자동 보정", result.analysis_note or "")
        completion.assert_called_once()

    @patch("committee.agents.llm_chair.load_openai_config")
    @patch("committee.agents.llm_chair.responses_completion_with_metadata")
    def test_timeout_retries_same_model_with_180_second_limit(
        self,
        completion: Mock,
        load_config: Mock,
    ) -> None:
        load_config.return_value = OpenAIConfig(api_key="test")
        completion.side_effect = [TimeoutError("slow"), _response()]

        result = self._agent().run(self.snapshot, self.stances)

        self.assertEqual(result.analysis_status, AnalysisStatus.RECOVERED)
        self.assertEqual(completion.call_count, 2)
        self.assertEqual(completion.call_args_list[0].kwargs["model"], "gpt-5.6-terra")
        self.assertEqual(completion.call_args_list[1].kwargs["model"], "gpt-5.6-terra")
        self.assertEqual(completion.call_args_list[0].kwargs["timeout"], 180)

    @patch("committee.agents.llm_chair.load_openai_config")
    @patch("committee.agents.llm_chair.responses_completion_with_metadata")
    def test_recovery_model_then_rule_fallback_remains_visible(
        self,
        completion: Mock,
        load_config: Mock,
    ) -> None:
        load_config.return_value = OpenAIConfig(api_key="test")
        completion.side_effect = TimeoutError("slow")

        result = self._agent().run(self.snapshot, self.stances)

        self.assertEqual(completion.call_count, 3)
        self.assertEqual(completion.call_args_list[2].kwargs["model"], "gpt-5.6-luna")
        self.assertEqual(completion.call_args_list[2].kwargs["reasoning_effort"], "low")
        self.assertEqual(result.analysis_status, AnalysisStatus.FALLBACK)
        self.assertIn("규칙 기반 대체 분석", result.sugeup_narrative or "")
        self.assertTrue(result.analysis_note)


if __name__ == "__main__":
    unittest.main()
