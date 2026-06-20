from __future__ import annotations

from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from committee.agents.greed_pot import GreedPotResult


class GreedPotTests(unittest.TestCase):
    def test_greed_pot_result_schema(self) -> None:
        result = GreedPotResult.model_validate(
            {
                "agent_name": "탐욕의 항아리",
                "market_story": "항아리가 속삭인다. 이건 결론이 아니라 가설이다.",
                "hidden_themes": ["반도체/AI", "환율", "2차 수혜"],
                "hypotheses": [
                    {
                        "theme": "AI 전력망의 그림자",
                        "visible_winner": "AI 반도체",
                        "hidden_beneficiary": "전력기기와 냉각 공급망",
                        "candidate_stocks": ["전력기기", "냉각장비"],
                        "narrative": "탐욕은 늘 본체보다 주변 장비에서 늦게 들킨다는 가설이다.",
                        "possible_catalyst": "AI 설비투자 뉴스 확대",
                        "why_market_may_miss_it": "시장은 칩 이름만 보느라 주변부 병목을 늦게 볼 수 있다.",
                        "invalidation_condition": "AI 설비투자 둔화가 확인될 때",
                        "confidence": "MED",
                    }
                ],
                "contrarian_view": "인기 테마의 바깥쪽을 보자는 가설이다.",
                "wildcard_scenario": "정책 뉴스가 공급망 하단으로 번질 수 있다.",
                "reality_check": "투자 추천이 아니며 숫자와 공시 재검증이 필요하다.",
            }
        )

        self.assertEqual(result.agent_name, "탐욕의 항아리")
        self.assertEqual(result.hypotheses[0].confidence, "MED")


if __name__ == "__main__":
    unittest.main()
