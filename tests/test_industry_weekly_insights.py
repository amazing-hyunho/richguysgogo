from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from committee.industry_cycle import industry_ai_opinion, industry_news, insight_repository, repository
from committee.industry_cycle import cycle_repository
from committee.tools.openai_chat import ChatCompletionResult, OpenAIConfig
from scripts import run_industry_weekly_insights


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
                "prompt_version": "industry_weekly_v2",
                "input_hash": "abc123",
                "investment_view": "중립",
                "opinion": "정량 신호는 개선 중이나 가격 부담을 확인해야 합니다.",
                "weekly_change": "전주 대비 점수가 개선됐습니다.",
                "structural_context": "반도체는 재고와 설비투자 순환의 영향을 받습니다.",
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
        self.assertEqual(opinion["investment_view"], "중립")
        self.assertEqual(opinion["prompt_version"], "industry_weekly_v2")


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
                    "investment_view": "우호",
                    "opinion": "회복 신호와 뉴스를 함께 확인합니다.",
                    "weekly_change": "전주 대비 개선",
                    "structural_context": "수요와 재고 순환에 민감합니다.",
                    "news_assessment": "강화",
                    "catalysts": ["수요"],
                    "risks": ["가격"],
                    "cited_links": ["https://example.com/a", "https://invented.example/x"],
                    "confidence": "보통",
                },
                {
                    "industry_id": "banks",
                    "investment_view": "주의",
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
        self.assertEqual(result.opinions[0]["investment_view"], "우호")
        self.assertIn("재고 순환", result.opinions[0]["structural_context"])

    def test_validation_requires_every_industry(self) -> None:
        with self.assertRaisesRegex(ValueError, "missing_industries:banks"):
            industry_ai_opinion.validate_opinion_payload(
                {
                    "overall_summary": "요약",
                    "industries": [{"industry_id": "semiconductors", "opinion": "의견"}],
                },
                self.industries,
            )

    def test_ai_confidence_is_capped_by_quantitative_confidence(self) -> None:
        industries = [
            {
                "industry_id": "semiconductors",
                "latest_signal": {"confidence": 0.2, "data_completeness": 1.0},
                "news": [],
            }
        ]
        result = industry_ai_opinion.validate_opinion_payload(
            {
                "overall_summary": "요약",
                "industries": [
                    {
                        "industry_id": "semiconductors",
                        "investment_view": "우호",
                        "opinion": "조건부 관찰",
                        "confidence": "높음",
                    }
                ],
            },
            industries,
        )
        self.assertEqual(result.opinions[0]["confidence"], "낮음")

    def test_prompt_separates_model_prior_from_current_evidence(self) -> None:
        system, user = industry_ai_opinion.build_prompts(self.industries)
        self.assertIn("사전학습 지식", system)
        self.assertIn("현재 판단의 증거로", system)
        self.assertIn("매수·매도", system)
        self.assertIn('"structural_context"', user)

    def test_generation_keeps_usage_metadata_for_audit(self) -> None:
        payload = {
            "overall_summary": "혼조입니다.",
            "industries": [
                {
                    "industry_id": item["industry_id"],
                    "investment_view": "중립",
                    "opinion": "조건부 관찰입니다.",
                    "weekly_change": "최초 관측",
                    "structural_context": "시점 비의존 일반론입니다.",
                    "news_assessment": "중립",
                    "catalysts": [],
                    "risks": [],
                    "cited_links": [],
                    "confidence": "낮음",
                }
                for item in self.industries
            ],
        }

        def fake_call(**_kwargs):
            import json

            return ChatCompletionResult(
                content=json.dumps(payload, ensure_ascii=False),
                model="gpt-4.1",
                input_tokens=123,
                output_tokens=45,
            )

        batch = industry_ai_opinion.generate_industry_opinions(
            self.industries,
            config=OpenAIConfig(api_key="test"),
            model="gpt-4.1",
            llm_call=fake_call,
        )
        self.assertEqual(batch.input_tokens, 123)
        self.assertEqual(batch.output_tokens, 45)
        self.assertEqual(batch.prompt_version, "industry_weekly_v2")
        self.assertEqual(len(batch.input_hash or ""), 64)


class WeeklyInsightContextTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.db_path = Path(self.tmp.name) / "test.db"
        repository.upsert_industry_master(
            industry_id="semiconductors", name_kr="반도체", db_path=self.db_path
        )
        repository.upsert_industry_master(
            industry_id="banks", name_kr="은행", db_path=self.db_path
        )
        cycle_repository.upsert_industry_cycle_signal(
            {
                "industry_id": "semiconductors",
                "as_of": "2026-07-18",
                "model_version": "cycle_v1",
                "data_cutoff_at": "2026-07-18",
                "cycle_score": 55.0,
            },
            db_path=self.db_path,
        )
        cycle_repository.upsert_industry_cycle_signal(
            {
                "industry_id": "semiconductors",
                "as_of": "2026-07-25",
                "model_version": "cycle_v1",
                "data_cutoff_at": "2026-07-25",
                "cycle_score": 65.0,
            },
            db_path=self.db_path,
        )

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_only_industries_with_same_week_signal_are_sent_to_llm(self) -> None:
        with patch.object(run_industry_weekly_insights, "DB_PATH", self.db_path):
            rows = run_industry_weekly_insights._load_analysis_industries(
                "2026-07-25", "cycle_v1", "stock_candidate_v1"
            )
        self.assertEqual([row["industry_id"] for row in rows], ["semiconductors"])
        self.assertEqual(rows[0]["previous_signal"]["cycle_score"], 55.0)


if __name__ == "__main__":
    unittest.main()
