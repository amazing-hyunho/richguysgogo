from __future__ import annotations

# Provider interface for real-data snapshot v1.

from abc import ABC, abstractmethod
from typing import List, Dict, Tuple


class IDataProvider(ABC):
    """Minimal data provider interface for snapshot inputs."""

    @abstractmethod
    def get_usdkrw(self) -> Tuple[float | None, str | None]:
        """Return USD/KRW spot rate and failure reason."""

    @abstractmethod
    def get_kospi_change_pct(self) -> Tuple[float | None, str | None]:
        """Return KOSPI daily change percent and failure reason."""

    @abstractmethod
    def get_flows(self) -> Tuple[Dict | None, str | None]:
        """Return flow totals and failure reason."""

    @abstractmethod
    def get_headlines(self, limit: int) -> Tuple[List[str] | None, str | None]:
        """Return headline list and failure reason."""
