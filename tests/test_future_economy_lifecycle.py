from __future__ import annotations

import unittest

from committee.future_economy.lifecycle import (
    FutureEconomyValidationError,
    build_committee_agenda,
    build_weekly_report,
    normalize_evidence,
)


def evidence(evidence_id: str, evidence_type: str, *, direction: str = "positive") -> dict:
    return {
        "evidence_id": evidence_id,
        "evidence_type": evidence_type,
        "title": f"근거 {evidence_id}",
        "claim": "출처가 직접 뒷받침하는 주장",
        "event_date": "2026-08-20",
        "known_at": "2026-08-20",
        "source_url": f"https://example.com/{evidence_id}",
        "source_name": "공식 출처",
        "source_kind": "official_policy" if evidence_type == "policy" else "academic_primary",
        "direction": direction,
        "strength": 0.8,
    }


def candidate(research_id: str, evidence_types: list[str]) -> dict:
    return {
        "research_id": research_id,
        "domain_id": "ai-semiconductor-datacenter",
        "title": f"연구 {research_id}",
        "thesis": "글로벌 변화가 한국 산업에 전달되는지 추적한다.",
        "horizon_months": 12,
        "transmission_chain": ["세계 변화", "산업 수요", "한국 공급망"],
        "watch_industries": ["반도체"],
        "watch_companies": [],
        "historical_analogues": [],
        "invalidation_conditions": ["핵심 수요 감소"],
        "evidence": [evidence(f"{research_id}-{kind}", kind) for kind in evidence_types],
    }


class FutureEconomyLifecycleTests(unittest.TestCase):
    def test_source_url_is_required_for_scored_evidence(self) -> None:
        row = evidence("policy-1", "policy")
        row["source_url"] = ""
        with self.assertRaises(FutureEconomyValidationError):
            normalize_evidence(row, as_of="2026-08-24")

    def test_future_known_at_evidence_is_excluded(self) -> None:
        row = evidence("paper-1", "research")
        row["known_at"] = "2026-08-25"
        self.assertIsNone(normalize_evidence(row, as_of="2026-08-24"))

    def test_expired_evidence_is_excluded_and_task_is_recomputed(self) -> None:
        expired = evidence("market-old", "market")
        expired["valid_until"] = "2026-08-23"
        self.assertIsNone(normalize_evidence(expired, as_of="2026-08-24"))

        previous = build_weekly_report(
            as_of="2026-08-20",
            candidates=[candidate("aging", ["research", "policy", "market"])],
        )
        for row in previous["research_tasks"][0]["evidence"]:
            if row["evidence_type"] in {"policy", "market"}:
                row["valid_until"] = "2026-08-23"
        refreshed = build_weekly_report(as_of="2026-08-24", candidates=[], previous_report=previous)
        task = refreshed["research_tasks"][0]
        self.assertEqual(task["evidence_type_count"], 1)
        self.assertEqual(task["status"], "initial_watch")
        self.assertEqual(task["weekly_change"], "weakened")

    def test_evidence_type_thresholds_control_status_and_agenda(self) -> None:
        report = build_weekly_report(
            as_of="2026-08-24",
            candidates=[
                candidate("one", ["research"]),
                candidate("two", ["research", "policy"]),
                candidate("three", ["research", "policy", "corporate"]),
            ],
        )
        by_id = {row["research_id"]: row for row in report["research_tasks"]}
        self.assertEqual(by_id["one"]["status"], "initial_watch")
        self.assertEqual(by_id["two"]["status"], "active")
        self.assertEqual(by_id["three"]["status"], "committee_review")
        agenda = build_committee_agenda(report)
        self.assertEqual(agenda["item_count"], 1)
        self.assertEqual(agenda["items"][0]["research_id"], "three")
        self.assertEqual(
            {row["evidence_type"] for row in agenda["items"][0]["top_evidence"]},
            {"research", "policy", "corporate"},
        )

    def test_new_and_active_limits_are_enforced(self) -> None:
        report = build_weekly_report(
            as_of="2026-08-24",
            candidates=[candidate(f"theme-{index:02d}", ["research"]) for index in range(12)],
        )
        self.assertEqual(len(report["research_tasks"]), 3)
        self.assertEqual(report["summary"]["new"], 3)

        previous = {
            "research_tasks": [candidate(f"old-{index:02d}", ["research"]) for index in range(10)]
        }
        for row in previous["research_tasks"]:
            row.update({
                "status": "initial_watch",
                "weekly_change": "maintained",
                "research_score": 30.0,
                "evidence_type_count": 1,
                "first_seen_at": "2026-08-17",
                "last_updated_at": "2026-08-17",
            })
        full = build_weekly_report(
            as_of="2026-08-24",
            candidates=[candidate("extra", ["research"])],
            previous_report=previous,
        )
        self.assertEqual(len(full["research_tasks"]), 10)
        self.assertNotIn("extra", {row["research_id"] for row in full["research_tasks"]})

    def test_zero_new_research_is_a_valid_report(self) -> None:
        report = build_weekly_report(as_of="2026-08-24", candidates=[])
        self.assertEqual(report["research_tasks"], [])
        self.assertEqual(report["summary"]["new"], 0)
        self.assertEqual(build_committee_agenda(report)["items"], [])


if __name__ == "__main__":
    unittest.main()
