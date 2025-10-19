from __future__ import annotations

"""Abstract base classes for extraction backends."""

from abc import ABC, abstractmethod

from docvqa.data.dataset import DocumentExample
from docvqa.pipeline.schemas import ExtractionRequest, ExtractionResult


class ExtractionError(RuntimeError):
    """Raised when an extractor fails to process a document."""


class BaseExtractor(ABC):
    """Interface implemented by all extractors."""

    @abstractmethod
    def extract(self, request: ExtractionRequest) -> ExtractionResult:
        """Perform extraction for a document and return structured results."""

    def from_example(self, example: DocumentExample) -> ExtractionResult:
        """Helper to convert dataset examples into extractor requests."""

        request = ExtractionRequest(
            doc_id=example.doc_id,
            document_path=example.document_path,
            questions=example.questions,
            metadata=example.metadata or {},
        )
        return self.extract(request)


__all__ = ["BaseExtractor", "ExtractionError"]
