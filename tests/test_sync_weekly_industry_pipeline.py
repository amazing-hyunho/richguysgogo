from __future__ import annotations

import subprocess
import sys
import unittest
from unittest.mock import patch

from scripts import sync_weekly


class SyncWeeklyIndustryPipelineTests(unittest.TestCase):
    def test_existing_weekly_job_runs_industry_steps_before_dashboard(self) -> None:
        calls: list[list[str]] = []

        def fake_run(cmd, **_kwargs):
            calls.append(list(cmd))
            return subprocess.CompletedProcess(cmd, 0, stdout="", stderr="")

        with (
            patch.object(sys, "argv", ["sync_weekly.py", "--skip-stocks"]),
            patch.object(sync_weekly.subprocess, "run", side_effect=fake_run),
            patch("builtins.print"),
        ):
            sync_weekly.main()

        scripts_run = [next((part for part in cmd if part.startswith("scripts/")), "") for cmd in calls]
        expected = [
            "scripts/sync_industry_master.py",
            "scripts/backfill_industry_prices.py",
            "scripts/backfill_industry_indicators.py",
            "scripts/run_industry_price_factors.py",
            "scripts/run_industry_fundamentals_factors.py",
            "scripts/run_industry_candidates.py",
            "scripts/run_industry_cycle_weekly.py",
            "scripts/run_industry_weekly_insights.py",
            "scripts/run_industry_virtual_portfolio.py",
        ]
        positions = [scripts_run.index(name) for name in expected]
        self.assertEqual(positions, sorted(positions))
        self.assertLess(
            scripts_run.index("scripts/run_industry_virtual_portfolio.py"),
            scripts_run.index("scripts/build_dashboard.py"),
        )

    def test_skip_industry_llm_keeps_news_collection(self) -> None:
        calls: list[list[str]] = []

        def fake_run(cmd, **_kwargs):
            calls.append(list(cmd))
            return subprocess.CompletedProcess(cmd, 0, stdout="", stderr="")

        with (
            patch.object(
                sys,
                "argv",
                ["sync_weekly.py", "--skip-stocks", "--skip-dashboard", "--skip-industry-llm"],
            ),
            patch.object(sync_weekly.subprocess, "run", side_effect=fake_run),
            patch("builtins.print"),
        ):
            sync_weekly.main()

        insight = next(cmd for cmd in calls if "scripts/run_industry_weekly_insights.py" in cmd)
        self.assertIn("--execute", insight)
        self.assertIn("--skip-llm", insight)


if __name__ == "__main__":
    unittest.main()
