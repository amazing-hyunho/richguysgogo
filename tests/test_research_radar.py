from __future__ import annotations

import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from committee.research_radar.models import RadarValidationError, ThemeInput
from committee.research_radar.report import render_markdown
from committee.research_radar.runner import load_theme_input
from committee.research_radar.scoring import analyze_theme


FIXTURE = ROOT / "config" / "research_radar_transformer.json"


def _base_payload() -> dict:
    return {
        "schema_version": "research-radar-input-v1",
        "as_of": "2024-01-31",
        "theme": {"theme_id": "test-theme", "name": "테스트", "thesis": "검증용 가설"},
        "evidence": [
            {
                "evidence_id": "paper-one",
                "stage": "research_validation",
                "event_type": "paper",
                "title": "Paper one",
                "claim": "Primary result",
                "event_date": "2024-01-01",
                "known_at": "2024-01-02",
                "source_url": "https://arxiv.org/abs/0000.00001",
                "source_name": "arXiv",
                "source_kind": "academic_primary",
                "direction": "positive",
                "strength": 0.9,
            }
        ],
        "public_companies": [],
        "limitations": [],
    }


class ResearchRadarTests(unittest.TestCase):
    def test_transformer_fixture_reaches_earnings_confirmation(self) -> None:
        report = analyze_theme(load_theme_input(FIXTURE))
        self.assertEqual(report.status, "earnings_confirmed")
        self.assertGreater(report.chain_score, 80.0)
        self.assertGreater(report.confidence, 60.0)
        self.assertTrue(all(stage.passed for stage in report.stages))
        self.assertEqual(len(report.evidence), 7)
        self.assertEqual(report.excluded_evidence, ())
        self.assertEqual(report.public_companies[0].ticker, "GOOGL")

    def test_as_of_override_excludes_future_known_evidence(self) -> None:
        report = analyze_theme(load_theme_input(FIXTURE, as_of_override="2018-12-31"))
        self.assertEqual(report.status, "validating")
        self.assertEqual(len(report.evidence), 2)
        self.assertEqual(len(report.excluded_evidence), 5)
        excluded_ids = {row.evidence_id for row in report.excluded_evidence}
        self.assertIn("nvidia-fy2024-results", excluded_ids)
        microsoft = next(row for row in report.public_companies if row.ticker == "MSFT")
        self.assertEqual(microsoft.link_strength, 0.0)
        self.assertEqual(microsoft.unavailable_evidence_ids, ("microsoft-openai-partnership-2023",))

    def test_negative_evidence_reduces_stage_score_and_confidence(self) -> None:
        payload = _base_payload()
        negative = dict(payload["evidence"][0])
        negative.update(
            {
                "evidence_id": "paper-refutation",
                "title": "Independent refutation",
                "claim": "Result did not replicate",
                "source_url": "https://example.org/refutation",
                "source_name": "Independent Lab",
                "direction": "negative",
                "strength": 0.9,
            }
        )
        payload["evidence"].append(negative)
        report = analyze_theme(ThemeInput.from_dict(payload))
        stage = report.stages[0]
        self.assertEqual(stage.score, 0.0)
        self.assertLess(stage.confidence, 80.0)
        self.assertFalse(stage.passed)
        self.assertEqual(report.status, "emerging")

    def test_unknown_company_evidence_reference_is_rejected(self) -> None:
        payload = _base_payload()
        payload["public_companies"] = [
            {
                "ticker": "TEST",
                "market": "US",
                "company_name": "Test Co",
                "role": "supplier",
                "directness": "enabler",
                "thesis": "test",
                "evidence_ids": ["missing-evidence"],
            }
        ]
        with self.assertRaisesRegex(RadarValidationError, "unknown IDs"):
            ThemeInput.from_dict(payload)

    def test_duplicate_evidence_id_is_rejected(self) -> None:
        payload = _base_payload()
        payload["evidence"].append(dict(payload["evidence"][0]))
        with self.assertRaisesRegex(RadarValidationError, "duplicate evidence_id"):
            ThemeInput.from_dict(payload)

    def test_markdown_contains_methodology_sources_and_disclaimer(self) -> None:
        report = analyze_theme(load_theme_input(FIXTURE))
        markdown = render_markdown(report)
        self.assertIn("Research-to-Market Radar", markdown)
        self.assertIn("Attention Is All You Need", markdown)
        self.assertIn("known_at <= as_of", markdown)
        self.assertIn("기대수익률", markdown)
        self.assertIn("https://arxiv.org/abs/1706.03762", markdown)

    def test_report_json_round_trip_is_serializable(self) -> None:
        report = analyze_theme(load_theme_input(FIXTURE))
        encoded = json.dumps(report.to_dict(), ensure_ascii=False)
        decoded = json.loads(encoded)
        self.assertEqual(decoded["schema_version"], "research-radar-report-v1")
        self.assertEqual(decoded["status"], "earnings_confirmed")


if __name__ == "__main__":
    unittest.main()
