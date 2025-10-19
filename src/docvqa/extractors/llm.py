from __future__ import annotations

"""Extractor that relies on LLM completions."""

import json

from docvqa.extractors.base import BaseExtractor, ExtractionError
from docvqa.llm.client import LLMClient
from docvqa.pipeline.prompts import build_prompt
from docvqa.pipeline.schemas import ExtractionRequest, ExtractionResult


class LLMExtractor(BaseExtractor):
    """Extraction backend that prompts an LLM for structured JSON output."""

    def __init__(self, client: LLMClient) -> None:
        self._client = client

    def extract(self, request: ExtractionRequest) -> ExtractionResult:
        prompt = build_prompt(request)
        response = self._client.generate(prompt)
        try:
            message = response["choices"][0]["message"]["content"]
        except (KeyError, IndexError) as exc:  # pragma: no cover - depends on provider
            msg = "Unexpected LLM response format"
            raise ExtractionError(msg) from exc

        try:
            content = json.loads(message)
        except json.JSONDecodeError as exc:
            msg = "LLM response is not valid JSON"
            raise ExtractionError(msg) from exc

        return ExtractionResult(doc_id=request.doc_id, content=content, raw_response=response)


__all__ = ["LLMExtractor"]
