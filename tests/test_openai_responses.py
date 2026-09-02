from __future__ import annotations

import json
from pathlib import Path
import sys
import unittest
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from committee.tools.openai_chat import OpenAIConfig, responses_completion_with_metadata


class OpenAIResponsesTests(unittest.TestCase):
    @patch("requests.post")
    def test_responses_request_uses_reasoning_and_json_mode(self, post: Mock) -> None:
        response = Mock(status_code=200)
        response.headers = {"x-request-id": "req_test"}
        response.json.return_value = {
            "status": "completed",
            "model": "gpt-5.6-terra-2026-08-01",
            "output": [
                {"type": "reasoning", "summary": []},
                {
                    "type": "message",
                    "content": [
                        {"type": "output_text", "text": '{"consensus":"중립"}'},
                    ],
                },
            ],
            "usage": {"input_tokens": 120, "output_tokens": 40},
        }
        post.return_value = response

        result = responses_completion_with_metadata(
            config=OpenAIConfig(api_key="test-key"),
            model="gpt-5.6-terra",
            system_prompt="system",
            user_prompt="user",
            reasoning_effort="medium",
        )

        self.assertEqual(result.content, '{"consensus":"중립"}')
        self.assertEqual(result.input_tokens, 120)
        self.assertEqual(result.output_tokens, 40)
        self.assertEqual(result.request_id, "req_test")
        self.assertEqual(post.call_args.args[0], "https://api.openai.com/v1/responses")
        payload = json.loads(post.call_args.kwargs["data"])
        self.assertEqual(payload["reasoning"], {"effort": "medium"})
        self.assertEqual(payload["text"]["format"], {"type": "json_object"})
        self.assertIn("JSON", payload["input"])
        self.assertTrue(payload["input"].endswith("user"))
        self.assertFalse(payload["store"])
        self.assertNotIn("temperature", payload)

    @patch("requests.post")
    def test_incomplete_response_is_rejected(self, post: Mock) -> None:
        response = Mock(status_code=200)
        response.json.return_value = {"status": "incomplete", "output": []}
        post.return_value = response

        with self.assertRaisesRegex(RuntimeError, "openai_response_incomplete"):
            responses_completion_with_metadata(
                config=OpenAIConfig(api_key="test-key"),
                model="gpt-5.6-sol",
                system_prompt="system",
                user_prompt="user",
                reasoning_effort="medium",
            )


if __name__ == "__main__":
    unittest.main()
