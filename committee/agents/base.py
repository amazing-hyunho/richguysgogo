from __future__ import annotations

# Base class for stateless pre-analysis agents.

from abc import ABC, abstractmethod

from committee.schemas.snapshot import Snapshot
from committee.schemas.stance import Stance


class PreAnalysisAgent(ABC):
    """Stateless base class for pre-analysis agents."""

    @abstractmethod
    def run(self, snapshot: Snapshot) -> Stance:
        """Return a stance based on the snapshot."""
        raise NotImplementedError
