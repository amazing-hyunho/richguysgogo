from __future__ import annotations

# Fallback provider that always returns defaults.

from typing import Dict, List, Tuple

from committee.tools.providers import IDataProvider


class FallbackProvider(IDataProvider):
    """Always-available provider returning safe defaults."""

    def get_usdkrw(self) -> Tuple[float | None, str | None]:
        """Return default USD/KRW."""
        return 0.0, "fallback used"

    def get_kospi_change_pct(self) -> Tuple[float | None, str | None]:
        """Return default KOSPI change percent."""
        return 0.0, "fallback used"

    def get_flows(self) -> Tuple[Dict | None, str | None]:
        """Return default flow totals."""
        return {"foreign_net": 0.0, "institution_net": 0.0, "retail_net": 0.0}, "fallback used"

    def get_headlines(self, limit: int) -> Tuple[List[str] | None, str | None]:
        """Return empty headline list."""
        return [], "fallback used"
