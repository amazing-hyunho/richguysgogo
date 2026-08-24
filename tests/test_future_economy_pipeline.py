from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class FutureEconomyPipelineTests(unittest.TestCase):
    def test_daily_pipeline_no_longer_generates_daily_greed_pot(self) -> None:
        source = (ROOT / "committee" / "core" / "pipeline.py").read_text(encoding="utf-8")
        self.assertNotIn("GreedPotAgent", source)
        self.assertNotIn("run greed pot", source)
        self.assertIn("stage 6/6: persist artifacts", source)


if __name__ == "__main__":
    unittest.main()
