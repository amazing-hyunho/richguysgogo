from __future__ import annotations

# Default placeholder provider for snapshot data.

from datetime import date
from typing import Dict, List

from committee.tools.providers import SnapshotDataProvider


class MockProvider(SnapshotDataProvider):
    """Return safe placeholder data without external dependencies."""

    def get_market_summary(self, market_date: date) -> Dict:
        """Return placeholder market summary."""
        return {
            "note": f"{market_date.isoformat()} market opens stable.",
            "kospi_change_pct": 0.2,
            "usdkrw": 1340.5,
        }

    def get_flow_summary(self, market_date: date) -> Dict:
        """Return placeholder flow summary."""
        return {
            "note": "Flows show balanced demand and supply.",
            "foreign_net": 120.0,
            "institution_net": -80.0,
            "retail_net": -40.0,
        }

    def get_news_headlines(self, market_date: date) -> List[str]:
        """Return placeholder headlines list."""
        return [
            "Macro data in line",
            "Earnings season ongoing",
            "Policy outlook steady",
            "FX volatility muted",
            "Energy prices mixed",
        ]

    def get_sector_moves(self, market_date: date) -> List[str]:
        """Return placeholder sector moves list."""
        return [
            "Tech steady",
            "Energy mixed",
            "Healthcare firm",
        ]

    def get_watchlist(self, market_date: date) -> List[str]:
        """Return placeholder watchlist."""
        return ["SPY", "QQQ", "XLK"]
