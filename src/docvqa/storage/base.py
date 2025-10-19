from __future__ import annotations

"""Abstract storage writers for pipeline outputs."""

from abc import ABC, abstractmethod

from docvqa.pipeline.schemas import ExtractionResult


class BaseStorage(ABC):
    """Interface implemented by storage backends."""

    @abstractmethod
    def write(self, result: ExtractionResult) -> None:
        """Persist a single extraction result."""

    def finalize(self) -> None:
        """Hook invoked once the pipeline completes."""


__all__ = ["BaseStorage"]
