from __future__ import annotations

import subprocess
import sys
import unittest
from datetime import date
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
            "scripts/run_industry_virtual_portfolio.py",
            "scripts/run_industry_weekly_insights.py",
        ]
        positions = [scripts_run.index(name) for name in expected]
        self.assertEqual(positions, sorted(positions))
        self.assertLess(
            scripts_run.index("scripts/run_industry_virtual_portfolio.py"),
            scripts_run.index("scripts/build_dashboard.py"),
        )
        self.assertLess(
            scripts_run.index("scripts/run_research_radar_weekly.py"),
            scripts_run.index("scripts/build_dashboard.py"),
        )

    def test_skip_research_radar_omits_only_radar_step(self) -> None:
        calls: list[list[str]] = []

        def fake_run(cmd, **_kwargs):
            calls.append(list(cmd))
            return subprocess.CompletedProcess(cmd, 0, stdout="", stderr="")

        with (
            patch.object(
                sys,
                "argv",
                ["sync_weekly.py", "--skip-stocks", "--skip-research-radar"],
            ),
            patch.object(sync_weekly.subprocess, "run", side_effect=fake_run),
            patch("builtins.print"),
        ):
            sync_weekly.main()

        self.assertFalse(any("scripts/run_research_radar_weekly.py" in cmd for cmd in calls))
        self.assertTrue(any("scripts/build_dashboard.py" in cmd for cmd in calls))

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

    def test_long_batch_freezes_one_logical_run_date(self) -> None:
        calls: list[list[str]] = []

        class AdvancingDate(date):
            call_count = 0

            @classmethod
            def today(cls):
                cls.call_count += 1
                return date(2026, 7, 25) if cls.call_count == 1 else date(2026, 7, 26)

        def fake_run(cmd, **_kwargs):
            calls.append(list(cmd))
            return subprocess.CompletedProcess(cmd, 0, stdout="", stderr="")

        with (
            patch.object(sys, "argv", ["sync_weekly.py", "--skip-stocks", "--skip-dashboard"]),
            patch.object(sync_weekly, "date", AdvancingDate),
            patch.object(sync_weekly.subprocess, "run", side_effect=fake_run),
            patch("builtins.print"),
        ):
            sync_weekly.main()

        self.assertEqual(AdvancingDate.call_count, 1)
        industry_commands = [
            cmd
            for cmd in calls
            if any(part.startswith("scripts/run_industry_") for part in cmd)
        ]
        self.assertTrue(industry_commands)
        for cmd in industry_commands:
            if "--as-of" in cmd:
                self.assertEqual(cmd[cmd.index("--as-of") + 1], "2026-07-25")

    def test_failed_step_propagates_nonzero_weekly_exit_code(self) -> None:
        def fake_run(cmd, **_kwargs):
            return subprocess.CompletedProcess(
                cmd,
                1 if "scripts/run_industry_weekly_insights.py" in cmd else 0,
                stdout="",
                stderr="",
            )

        with (
            patch.object(sys, "argv", ["sync_weekly.py", "--skip-stocks"]),
            patch.object(sync_weekly.subprocess, "run", side_effect=fake_run),
            patch("builtins.print"),
        ):
            exit_code = sync_weekly.main()

        self.assertEqual(exit_code, 1)


if __name__ == "__main__":
    unittest.main()
