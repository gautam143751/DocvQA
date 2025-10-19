from __future__ import annotations

"""Factory helpers to instantiate extractors based on configuration."""

from docvqa.config.models import ExtractorConfig, ExtractorProvider
from docvqa.extractors.base import BaseExtractor
from docvqa.extractors.document_ai import DocumentAIExtractor
from docvqa.extractors.llm import LLMExtractor
from docvqa.llm.client import LLMClient


def create_extractor(config: ExtractorConfig) -> BaseExtractor:
    """Return an extractor implementation matching the configuration."""

    if config.provider == ExtractorProvider.LLM:
        if config.llm is None:  # pragma: no cover - validated earlier
            msg = "LLM configuration is required for LLM provider"
            raise ValueError(msg)
        client = LLMClient(config.llm)
        return LLMExtractor(client)

    if config.provider == ExtractorProvider.DOCUMENT_AI:
        if config.document_ai is None:  # pragma: no cover - validated earlier
            msg = "Document AI configuration is required for document_ai provider"
            raise ValueError(msg)
        return DocumentAIExtractor(config.document_ai)

    msg = f"Unsupported extractor provider: {config.provider}"
    raise ValueError(msg)


__all__ = ["create_extractor"]
