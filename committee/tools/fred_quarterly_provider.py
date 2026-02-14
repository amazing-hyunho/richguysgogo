from __future__ import annotations

"""
Phase 3: Quarterly macro providers (FRED-based).

Economic meaning
----------------
- Real GDP (GDPC1): inflation-adjusted output level.
- GDP growth QoQ annualized (A191RL1Q225SBEA): commonly quoted quarterly growth rate.

Failure handling
----------------
- Returns None on any error (caller stores NULL, status=FAIL).
"""

from committee.tools.fred_common import fetch_fred_latest


def fetch_real_gdp() -> float | None:
    """Fetch latest real GDP level (FRED: GDPC1)."""
    return fetch_fred_latest("GDPC1")


def fetch_gdp_growth() -> float | None:
    """Fetch latest GDP growth QoQ annualized % (FRED: A191RL1Q225SBEA)."""
    return fetch_fred_latest("A191RL1Q225SBEA")

