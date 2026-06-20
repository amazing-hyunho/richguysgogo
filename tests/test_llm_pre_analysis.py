from __future__ import annotations

from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from committee.agents.llm_pre_analysis import LLMPreAnalysisAgent
from committee.schemas.stance import Stance


class LLMPreAnalysisTests(unittest.TestCase):
    def test_evidence_ids_are_clamped_before_validation(self) -> None:
        parsed = {
            "agent_name": "flow",
            "core_claims": ["수급 분석 결과입니다."],
            "korean_comment": "수급 판단은 중립입니다.",
            "regime_tag": "NEUTRAL",
            "confidence": "MED",
            "evidence_ids": [
                "snapshot.market_summary.note",
                "snapshot.market_summary.usdkrw",
                "snapshot.market_summary.kospi_change_pct",
                "snapshot.flow_summary.note",
                "snapshot.flow_summary.foreign_net",
                "snapshot.flow_summary.institution_net",
                "snapshot.flow_summary.retail_net",
                "snapshot.korean_market_flow",
                "snapshot.sector_moves",
                "snapshot.news_headlines",
                "snapshot.watchlist",
            ],
        }

        normalized = LLMPreAnalysisAgent._normalize_parsed_response(parsed)
        stance = Stance.model_validate(normalized)

        self.assertEqual(len(stance.evidence_ids), 10)
        self.assertNotIn("snapshot.watchlist", stance.evidence_ids)


if __name__ == "__main__":
    unittest.main()
