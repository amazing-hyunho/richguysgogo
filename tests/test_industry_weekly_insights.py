from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
import tempfile
import unittest

from committee.industry_cycle import industry_ai_opinion, industry_news, insight_repository, repository


class IndustryNewsTests(unittest.TestCase):
    def test_recent_news_is_filtered_and_near_duplicates_are_removed(self) -> None:
        now = datetime(2026, 7, 25, tzinfo=timezone.utc)

        def fake_fetcher(**_kwargs):
            return [
                ("반도체 수요 회복 기대 - 매체A", "https://example.com/a?utm_source=x", now),
                ("반도체 수요 회복 기대 - 매체B", "https://example.com/b", now),
                ("오래된 반도체 기사 - 매체C", "https://example.com/c", now - timedelta(days=30)),
            ]

        rows = industry_news.collect_industry_news(
            {"industry_id": "semiconductors", "name_kr": "반도체", "name_en": "Semiconductors"},
            now=now,
            lookback_days=14,
            limit=8,
            fetcher=fake_fetcher,
        )
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0].source, "매체A")
        self.assertNotIn("utm_source", rows[0].link)


class IndustryInsightRepositoryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.db_path = Path(self.tmp.name) / "test.db"
        repository.upsert_industry_master(
            industry_id="semiconductors", name_kr="반도체", db_path=self.db_path
        )

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_news_and_ai_opinion_round_trip(self) -> None:
        insight_repository.upsert_industry_news(
            {
                "industry_id": "semiconductors",
                "link": "https://example.com/a",
                "title": "반도체 기사",
                "source": "테스트",
                "published_at": "2026-07-25T00:00:00+00:00",
            },
            db_path=self.db_path,
        )
        insight_repository.upsert_industry_ai_opinion(
            {
                "industry_id": "semiconductors",
                "as_of": "2026-07-25",
                "cycle_model_version": "cycle_v1",
                "llm_model": "test-model",
                "opinion": "정량 신호는 개선 중이나 가격 부담을 확인해야 합니다.",
                "catalysts": ["수요 개선"],
                "risks": ["단기 급등"],
                "cited_links": ["https://example.com/a"],
                "confidence": "보통",
            },
            db_path=self.db_path,
        )
        self.assertEqual(len(insight_repository.list_industry_news("semiconductors", db_path=self.db_path)), 1)
        opinion = insight_repository.get_industry_ai_opinion(
            "semiconductors", "2026-07-25", "cycle_v1", db_path=self.db_path
        )
        self.assertEqual(opinion["risks"], ["단기 급등"])


class IndustryAiOpinionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.industries = [
            {
                "industry_id": "semiconductors",
                "name_kr": "반도체",
                "latest_signal": {"cycle_score": 61.0, "confirmed_state": "CYCLE_RECOVERY_EARLY"},
                "news": [{"title": "기사", "link": "https://example.com/a", "source": "테스트"}],
            },
            {
                "industry_id": "banks",
                "name_kr": "은행",
                "latest_signal": {"cycle_score": 52.0, "confirmed_state": "CYCLE_OVERHEATED"},
                "news": [],
            },
        ]

    def test_validation_removes_unprovided_citations(self) -> None:
        payload = {
            "overall_summary": "전체 산업은 혼조입니다.",
            "industries": [
                {
                    "industry_id": "semiconductors",
                    "opinion": "회복 신호와 뉴스를 함께 확인합니다.",
                    "news_assessment": "강화",
                    "catalysts": ["수요"],
                    "risks": ["가격"],
                    "cited_links": ["https://example.com/a", "https://invented.example/x"],
                    "confidence": "보통",
                },
                {
                    "industry_id": "banks",
                    "opinion": "과열 신호를 우선 확인합니다.",
                    "news_assessment": "뉴스 부족",
                    "catalysts": [],
                    "risks": ["과열"],
                    "cited_links": ["https://invented.example/y"],
                    "confidence": "높음",
                },
            ],
        }
        result = industry_ai_opinion.validate_opinion_payload(payload, self.industries)
        self.assertEqual(result.opinions[0]["cited_links"], ["https://example.com/a"])
        self.assertEqual(result.opinions[1]["cited_links"], [])

    def test_validation_requires_every_industry(self) -> None:
        with self.assertRaisesRegex(ValueError, "missing_industries:banks"):
            industry_ai_opinion.validate_opinion_payload(
                {
                    "overall_summary": "요약",
                    "industries": [{"industry_id": "semiconductors", "opinion": "의견"}],
                },
                self.industries,
            )


if __name__ == "__main__":
    unittest.main()

