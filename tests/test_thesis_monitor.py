from __future__ import annotations

from pathlib import Path
import sqlite3
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from committee.core.database import init_db
from committee.core.thesis_monitor import (
    calculate_thesis_score,
    create_thesis_from_text,
    filter_point_in_time_rows,
    insert_thesis_evidence,
    parse_news_evidence_json,
    score_market_regime,
)


class ThesisMonitorTests(unittest.TestCase):
    def test_score_calculation(self) -> None:
        result = calculate_thesis_score(
            evidence_support_score=30,
            evidence_contradiction_score=5,
            macro_confirmation_score=15,
            flow_confirmation_score=10,
            price_confirmation_score=8,
            risk_score=4,
            recent_5d_delta=10,
            market_regime="neutral",
        )
        self.assertEqual(result["thesis_trend"], "strengthening")
        self.assertGreaterEqual(result["thesis_score"], 50)

    def test_invalidation_penalty(self) -> None:
        result = calculate_thesis_score(
            evidence_support_score=20,
            macro_confirmation_score=10,
            risk_score=5,
            invalidation_hit=True,
            recent_5d_delta=-12,
            market_regime="neutral",
        )
        self.assertLess(result["thesis_score"], -20)
        self.assertIn(result["thesis_trend"], {"weakening", "invalidated"})

    def test_risk_off_caps_aggressive_buy(self) -> None:
        result = calculate_thesis_score(
            evidence_support_score=70,
            macro_confirmation_score=30,
            flow_confirmation_score=20,
            price_confirmation_score=20,
            market_regime="stress",
        )
        self.assertNotEqual(result["recommended_action"], "strong_buy_candidate")

    def test_news_classification_result_saved(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            db_path = Path(td) / "investment.db"
            init_db(db_path)
            conn = sqlite3.connect(db_path)
            conn.execute(
                """
                INSERT INTO investment_thesis (
                    id, title, raw_study_text, status, created_at, updated_at
                ) VALUES (1, 'AI capex cycle', 'note', 'Active', '2026-01-01', '2026-01-01')
                """
            )
            conn.commit()
            conn.close()
            evidence = parse_news_evidence_json(
                {
                    "thesis_id": 1,
                    "relevance": 0.9,
                    "direction": "support",
                    "strength": 0.8,
                    "novelty": 0.4,
                    "reliability": 0.7,
                    "summary": "AI 투자 확대",
                    "reasoning": "수요 가설을 강화",
                }
            )
            row_id = insert_thesis_evidence(evidence, date="2026-06-20", db_path=db_path)
            self.assertGreater(row_id, 0)
            conn = sqlite3.connect(db_path)
            direction = conn.execute("SELECT direction FROM thesis_evidence_daily WHERE id=?", (row_id,)).fetchone()[0]
            conn.close()
            self.assertEqual(direction, "support")

    def test_point_in_time_filter(self) -> None:
        rows = [
            {"date": "2026-05-01", "observed_at": "2026-05-02", "v": 1},
            {"date": "2026-05-01", "observed_at": "2026-05-10", "v": 2},
            {"date": "2026-05-03", "v": 3},
        ]
        visible = filter_point_in_time_rows(rows, "2026-05-03")
        self.assertEqual([r["v"] for r in visible], [1, 3])

    def test_market_regime_stress(self) -> None:
        regime = score_market_regime(
            daily_macro=[
                {"date": "2026-06-01", "vix": 18, "dxy": 100, "usdkrw": 1350, "hy_oas": 3.5, "ig_oas": 1.2},
                {"date": "2026-06-10", "vix": 35, "dxy": 106, "usdkrw": 1420, "hy_oas": 5.0, "ig_oas": 1.8},
            ],
            market_daily=[],
            market_flow_daily=[{"foreign_20d": -40000}],
        )
        self.assertIn(regime["regime"], {"risk_off", "stress"})

    def test_user_keywords_are_preserved_first(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            db_path = Path(td) / "investment.db"
            created = create_thesis_from_text(
                title="조선업 슈퍼사이클",
                raw_study_text="LNG선과 신조선가를 관찰",
                sector="조선",
                related_tickers=["329180"],
                news_keywords=["LNG선", "Clarksons", "orderbook"],
                db_path=db_path,
            )
            self.assertEqual(created["keywords"], ["LNG선", "Clarksons", "orderbook"])


if __name__ == "__main__":
    unittest.main()
