from __future__ import annotations

from datetime import date, datetime, timezone
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest

from committee.future_economy.collectors import (
    collect_live_policy_evidence,
    collect_market_evidence,
    collect_stored_news_evidence,
    load_historical_analogue_evidence,
)
from scripts.run_future_economy_weekly import build_artifacts


DOMAIN = {
    "domain_id": "robotics-automation-autonomy",
    "name": "로봇·자동화·자율주행",
    "evidence_keywords": ["로봇", "자동화", "robot"],
    "industry_ids": ["machinery_industrials"],
}


def make_db(path: Path) -> None:
    conn = sqlite3.connect(path)
    try:
        conn.executescript(
            """
            CREATE TABLE industry_news (
                industry_id TEXT, link TEXT, title TEXT, source TEXT,
                published_at TEXT, collected_at TEXT
            );
            CREATE TABLE industry_master (
                industry_id TEXT PRIMARY KEY, name_kr TEXT
            );
            CREATE TABLE industry_cycle_v2_signal (
                industry_id TEXT, as_of TEXT, model_version TEXT,
                market_confirmation_score REAL, data_completeness REAL,
                entry_signal TEXT
            );
            CREATE TABLE industry_cycle_signal (
                industry_id TEXT, as_of TEXT, model_version TEXT,
                representative_market TEXT
            );
            """
        )
        conn.execute(
            "INSERT INTO industry_master VALUES (?, ?)",
            ("machinery_industrials", "기계·산업재"),
        )
        conn.commit()
    finally:
        conn.close()


class FutureEconomyCollectorTests(unittest.TestCase):
    def test_weekly_builder_merges_all_evidence_types_into_one_agenda(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "runs"
            radar_dir = root / "2026-08-24" / "research_radar"
            radar_dir.mkdir(parents=True)
            radar_dir.joinpath("robot.json").write_text(json.dumps({
                "schema_version": "research-radar-report-v1",
                "theme": {"theme_id": "robot", "name": "로봇 연구", "thesis": "로봇 변화 추적"},
                "as_of": "2026-08-24",
                "evidence": [{
                    "evidence_id": "paper-1", "title": "로봇 논문", "claim": "재현 가능한 성능 개선",
                    "event_date": "2026-08-20", "known_at": "2026-08-20",
                    "source_url": "https://arxiv.org/abs/example", "source_name": "arXiv",
                    "source_kind": "academic_preprint", "direction": "positive", "strength": 0.7,
                }],
            }, ensure_ascii=False), encoding="utf-8")
            db_path = Path(tmp) / "test.db"
            make_db(db_path)
            conn = sqlite3.connect(db_path)
            try:
                conn.executemany(
                    "INSERT INTO industry_news VALUES (?, ?, ?, ?, ?, ?)",
                    [
                        ("machinery_industrials", "https://example.com/policy", "정부, 로봇 지원 정책 발표 - 연합뉴스", "연합뉴스", "2026-08-20T01:00:00+00:00", "2026-08-20T02:00:00+00:00"),
                        ("machinery_industrials", "https://example.com/order", "로봇 공급계약 수주 - 한국경제", "한국경제", "2026-08-21T01:00:00+00:00", "2026-08-21T02:00:00+00:00"),
                    ],
                )
                conn.execute(
                    "INSERT INTO industry_cycle_v2_signal VALUES (?, ?, ?, ?, ?, ?)",
                    ("machinery_industrials", "2026-08-23", "cycle_v2", 72.0, 0.9, "CONFIRM_ADD"),
                )
                conn.execute(
                    "INSERT INTO industry_cycle_signal VALUES (?, ?, ?, ?)",
                    ("machinery_industrials", "2026-08-23", "cycle_v1", "KR"),
                )
                conn.commit()
            finally:
                conn.close()
            research_config = {"topics": [{
                "theme_id": "robot", "domain_id": DOMAIN["domain_id"], "name": "로봇 연구",
                "thesis": "로봇 변화 추적",
            }]}
            domain_config = {"horizon_months": 12, "domains": [{
                **DOMAIN,
                "transmission_chain": ["기술", "설비", "한국 공급망"],
                "watch_industries": ["기계"],
                "invalidation_conditions": ["도입 중단"],
            }]}
            historical_config = {"analogues": [{
                "analogue_id": "case", "domain_ids": [DOMAIN["domain_id"]], "title": "과거 사례",
                "claim": "과거 확산 경로", "event_date": "2017-01-01", "known_at": "2017-01-01",
                "source_url": "https://example.com/history", "source_name": "원문",
            }]}
            report, agenda, _evidence, audit = build_artifacts(
                as_of="2026-08-24", output_root=root, research_config=research_config,
                domain_config=domain_config, historical_config=historical_config, db_path=db_path,
                include_live_policy=False,
            )
            task = report["research_tasks"][0]
            self.assertEqual(task["status"], "committee_review")
            self.assertEqual(task["evidence_type_count"], 5)
            self.assertEqual(agenda["item_count"], 1)
            self.assertEqual(len(agenda["items"][0]["top_evidence"]), 5)
            self.assertEqual(audit["collector_errors"], [])

    def test_stored_news_creates_distinct_policy_and_corporate_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            db_path = Path(tmp) / "test.db"
            make_db(db_path)
            conn = sqlite3.connect(db_path)
            try:
                conn.executemany(
                    "INSERT INTO industry_news VALUES (?, ?, ?, ?, ?, ?)",
                    [
                        ("machinery_industrials", "https://example.com/policy", "정부, 로봇 산업 지원 정책 발표 - 연합뉴스", "연합뉴스", "2026-08-20T01:00:00+00:00", "2026-08-20T02:00:00+00:00"),
                        ("machinery_industrials", "https://example.com/order", "로봇 기업, 대규모 공급계약 수주 - 한국경제", "한국경제", "2026-08-21T01:00:00+00:00", "2026-08-21T02:00:00+00:00"),
                        ("machinery_industrials", "https://example.com/blog", "로봇 기업, 투자 유치 - Naver Blog", "Naver Blog", "2026-08-21T01:00:00+00:00", "2026-08-21T02:00:00+00:00"),
                        ("machinery_industrials", "https://example.com/future", "로봇 기업 투자 확대 - 매일경제", "매일경제", "2026-08-22T01:00:00+00:00", "2026-08-25T02:00:00+00:00"),
                        ("machinery_industrials", "https://example.com/noise", "탄소 규제 대응 지침 - 경향신문", "경향신문", "2026-08-20T01:00:00+00:00", "2026-08-20T02:00:00+00:00"),
                    ],
                )
                conn.commit()
            finally:
                conn.close()
            rows = collect_stored_news_evidence(
                domain=DOMAIN, as_of="2026-08-24", db_path=db_path
            )
            self.assertEqual({row["evidence_type"] for row in rows}, {"policy", "corporate"})
            self.assertTrue(all(row["source_url"].startswith("https://") for row in rows))
            self.assertNotIn("future", " ".join(row["source_url"] for row in rows))
            self.assertNotIn("noise", " ".join(row["source_url"] for row in rows))
            self.assertNotIn("blog", " ".join(row["source_url"] for row in rows))

    def test_market_signal_is_point_in_time_and_expires(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            db_path = Path(tmp) / "test.db"
            make_db(db_path)
            conn = sqlite3.connect(db_path)
            try:
                conn.execute(
                    "INSERT INTO industry_cycle_v2_signal VALUES (?, ?, ?, ?, ?, ?)",
                    ("machinery_industrials", "2026-08-23", "cycle_v2", 72.0, 0.9, "CONFIRM_ADD"),
                )
                conn.execute(
                    "INSERT INTO industry_cycle_signal VALUES (?, ?, ?, ?)",
                    ("machinery_industrials", "2026-08-23", "cycle_v1", "KR"),
                )
                conn.commit()
            finally:
                conn.close()
            rows = collect_market_evidence(domain=DOMAIN, as_of="2026-08-24", db_path=db_path)
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["evidence_type"], "market")
            self.assertEqual(rows[0]["direction"], "positive")
            self.assertEqual(rows[0]["valid_until"], "2026-09-06")

    def test_live_policy_collector_requires_same_day_and_explicit_terms(self) -> None:
        today = date.today().isoformat()

        def fake_fetcher(**_kwargs):
            return [
                ("정부, 로봇 산업 세액공제 정책 발표 - 연합뉴스", "https://example.com/live", datetime.now(timezone.utc)),
                ("정부, 식품 산업 지원 정책 발표 - 연합뉴스", "https://example.com/off-topic", datetime.now(timezone.utc)),
            ]

        rows = collect_live_policy_evidence(domain=DOMAIN, as_of=today, fetcher=fake_fetcher)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["evidence_type"], "policy")
        self.assertEqual(rows[0]["known_at"], today)
        self.assertEqual(
            collect_live_policy_evidence(domain=DOMAIN, as_of="2020-01-01", fetcher=fake_fetcher),
            [],
        )

    def test_historical_analogue_requires_matching_domain_and_known_date(self) -> None:
        payload = {
            "analogues": [{
                "analogue_id": "case-1",
                "domain_ids": ["robotics-automation-autonomy"],
                "title": "검증 사례",
                "claim": "검증된 원문 사례",
                "event_date": "2017-01-01",
                "known_at": "2017-01-02",
                "source_url": "https://example.com/case",
                "source_name": "원문",
                "similarities": ["유사점"],
                "differences": ["차이점"],
                "reapplication_conditions": ["재현 조건"],
            }]
        }
        evidence, analogues = load_historical_analogue_evidence(
            domain_id="robotics-automation-autonomy", as_of="2026-08-24", payload=payload
        )
        self.assertEqual(evidence[0]["evidence_type"], "historical_analogy")
        self.assertEqual(analogues[0]["differences"], ["차이점"])


if __name__ == "__main__":
    unittest.main()
