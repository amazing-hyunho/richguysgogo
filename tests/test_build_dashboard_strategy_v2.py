from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

_SPEC = importlib.util.spec_from_file_location("build_dashboard", ROOT / "scripts" / "build_dashboard.py")
build_dashboard = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(build_dashboard)  # type: ignore[union-attr]


class StrategyV2DashboardTemplateTests(unittest.TestCase):
    def test_v2_tab_is_added_without_removing_existing_tabs(self) -> None:
        template = build_dashboard.TEMPLATE_PATH.read_text(encoding="utf-8")

        self.assertIn('data-tab="strategy-v2"', template)
        self.assertIn('id="tab-strategy-v2"', template)
        self.assertIn("renderStrategyV2Tab();", template)

        for existing_tab in (
            "market",
            "stocks",
            "future-economy",
            "news",
            "industry-cycle",
            "retire",
        ):
            self.assertIn(f'data-tab="{existing_tab}"', template)
            self.assertIn(f'id="tab-{existing_tab}"', template)

    def test_v2_tab_preserves_ai_analysis_and_collapsible_minutes(self) -> None:
        template = build_dashboard.TEMPLATE_PATH.read_text(encoding="utf-8")

        self.assertIn("오늘의 의장 심층 분석", template)
        self.assertIn("한 달 전략의 Daily 판단 근거", template)
        self.assertIn('id="v2-chair-analysis"', template)
        self.assertIn('id="v2-chair-analysis-body"', template)
        self.assertIn("markdownToHtml(chairNarrative)", template)
        self.assertIn("기존 AI 분석 보기", template)
        self.assertIn("위원회 회의록 펼쳐보기", template)
        self.assertIn('id="v2-agent-grid"', template)
        self.assertIn('id="v2-minutes"', template)

    def test_v2_chair_analysis_has_date_and_freshness_warning(self) -> None:
        template = build_dashboard.TEMPLATE_PATH.read_text(encoding="utf-8")

        self.assertIn('id="v2-chair-freshness"', template)
        self.assertIn("committee.market_date", template)
        self.assertIn("최신 Daily 분석 아님", template)
        self.assertIn("chairDetails.open = false", template)

    def test_dashboard_brand_and_v2_labels_are_clear(self) -> None:
        template = build_dashboard.TEMPLATE_PATH.read_text(encoding="utf-8")

        self.assertIn("<title>방구석 경제연구소</title>", template)
        self.assertIn("<h1>방구석 경제연구소</h1>", template)
        self.assertIn(">🧭 AI 투자 위원회</button>", template)
        self.assertNotIn("데이터는 DB·최신 런 스냅샷·뉴스 다이제스트에서만 구성됩니다.", template)
        self.assertNotIn('class="v2-rule-row"', template)
        self.assertNotIn("기존 위원회 분석 참고", template)
        self.assertIn("오늘의 시장 판단", template)
        self.assertIn("수급·거시·뉴스를 종합한 Daily 결론", template)
        self.assertIn("매일 새 데이터로 점검", template)
        self.assertIn("데이터가 충분한 분야만 표시", template)


if __name__ == "__main__":
    unittest.main()
