from __future__ import annotations

from datetime import date, datetime, timezone
import json
from pathlib import Path
import tempfile
import unittest

from committee.research_radar.weekly import (
    PaperCandidate,
    build_interpretation_prompts,
    build_report,
    filter_papers_for_topic_scope,
    filter_papers_for_window,
    parse_arxiv_feed,
    validate_interpretation_payload,
)


ATOM_FIXTURE = """<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <entry>
    <id>http://arxiv.org/abs/2608.01234v1</id>
    <updated>2026-08-04T10:00:00Z</updated>
    <published>2026-08-03T10:00:00Z</published>
    <title>  A Physical World Model for Robot Manipulation  </title>
    <summary>We test a world model on three real robot platforms.</summary>
    <author><name>Alice Example</name></author>
    <author><name>Bob Example</name></author>
    <category term="cs.RO" />
  </entry>
</feed>
"""


def _topic() -> dict[str, object]:
    return {
        "theme_id": "physical-ai-foundation-models",
        "name": "피지컬 AI·로봇 파운데이션 모델",
        "thesis": "범용 로봇 학습의 반복 가능한 진전을 추적한다.",
        "scope": ["world model", "VLA"],
    }


class ResearchRadarWeeklyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.paper = PaperCandidate(
            paper_id="2608-01234v1",
            title="A Physical World Model for Robot Manipulation",
            abstract="We test a world model on three real robot platforms.",
            authors=("Alice Example", "Bob Example"),
            published_at=datetime(2026, 8, 3, 10, tzinfo=timezone.utc),
            updated_at=datetime(2026, 8, 4, 10, tzinfo=timezone.utc),
            url="https://arxiv.org/abs/2608.01234v1",
            categories=("cs.RO",),
        )

    def test_parse_arxiv_feed_preserves_primary_metadata(self) -> None:
        papers = parse_arxiv_feed(ATOM_FIXTURE)
        self.assertEqual(len(papers), 1)
        self.assertEqual(papers[0], self.paper)

    def test_window_filter_excludes_future_and_old_papers(self) -> None:
        old = PaperCandidate(
            **{**self.paper.__dict__, "paper_id": "old", "published_at": datetime(2026, 6, 1, tzinfo=timezone.utc)}
        )
        future = PaperCandidate(
            **{**self.paper.__dict__, "paper_id": "future", "published_at": datetime(2026, 8, 12, tzinfo=timezone.utc)}
        )
        selected = filter_papers_for_window(
            [old, self.paper, future], as_of=date(2026, 8, 11), lookback_days=28
        )
        self.assertEqual([paper.paper_id for paper in selected], [self.paper.paper_id])

    def test_topic_scope_filter_applies_explicit_exclusions(self) -> None:
        wireless = PaperCandidate(
            **{**self.paper.__dict__, "paper_id": "wireless", "title": "Omni-Photonic Base Station"}
        )
        selected = filter_papers_for_topic_scope(
            [wireless, self.paper], {"exclude_terms": ["base station"]}
        )
        self.assertEqual([paper.paper_id for paper in selected], [self.paper.paper_id])

    def test_prompt_forbids_commercial_inference_and_contains_every_paper(self) -> None:
        system, user = build_interpretation_prompts(_topic(), [self.paper], as_of=date(2026, 8, 11))
        self.assertIn("기업의 매출·투자·상용화를 증명한다고 추론하지 않는다", system)
        self.assertIn(self.paper.paper_id, user)

    def test_validation_caps_strength_and_rejects_unknown_ids(self) -> None:
        payload = {
            "papers": [
                {
                    "paper_id": self.paper.paper_id,
                    "relevant": True,
                    "direction": "positive",
                    "claim": "세 종류의 실제 로봇에서 조작을 시험했다.",
                    "limitation": "초록에는 독립 재현 결과가 없다.",
                    "strength": 9,
                    "tags": ["World Model"],
                },
                {"paper_id": "invented", "relevant": True, "strength": 1},
            ]
        }
        rows = validate_interpretation_payload(payload, [self.paper])
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0].strength, 0.85)
        self.assertEqual(rows[0].tags, ("world-model",))

    def test_report_uses_llm_as_evidence_parser_not_final_scorer(self) -> None:
        rows = validate_interpretation_payload(
            {
                "papers": [
                    {
                        "paper_id": self.paper.paper_id,
                        "relevant": True,
                        "direction": "positive",
                        "claim": "세 종류의 실제 로봇에서 조작을 시험했다.",
                        "limitation": "본문과 독립 재현 여부는 확인하지 않았다.",
                        "strength": 0.85,
                        "tags": ["world-model", "real-robot"],
                    }
                ]
            },
            [self.paper],
        )
        report = build_report(_topic(), [self.paper], rows, as_of=date(2026, 8, 11))
        self.assertEqual(report.status, "validating")
        self.assertEqual(report.stages[0].score, 63.75)
        self.assertEqual(report.stages[1].score, 0.0)
        self.assertEqual(report.evidence[0].source_kind, "academic_preprint")


if __name__ == "__main__":
    unittest.main()
