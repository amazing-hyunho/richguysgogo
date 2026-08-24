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
            "greed-pot",
            "news",
            "industry-cycle",
            "research-radar",
            "retire",
        ):
            self.assertIn(f'data-tab="{existing_tab}"', template)
            self.assertIn(f'id="tab-{existing_tab}"', template)

    def test_v2_tab_preserves_ai_analysis_and_collapsible_minutes(self) -> None:
        template = build_dashboard.TEMPLATE_PATH.read_text(encoding="utf-8")

        self.assertIn("기존 AI 분석 보기", template)
        self.assertIn("위원회 회의록 펼쳐보기", template)
        self.assertIn('id="v2-agent-grid"', template)
        self.assertIn('id="v2-minutes"', template)

    def test_v2_tab_exposes_agreed_safety_rules(self) -> None:
        template = build_dashboard.TEMPLATE_PATH.read_text(encoding="utf-8")

        self.assertIn("핵심 데이터 75% 이상", template)
        self.assertIn("일반 신호 2주 확인", template)
        self.assertIn("현금 상한 60%", template)
        self.assertIn("현금 비중 산식과 뉴스 보조점수는 다음 단계에서 연결", template)


if __name__ == "__main__":
    unittest.main()
