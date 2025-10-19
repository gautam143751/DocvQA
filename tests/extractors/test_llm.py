from __future__ import annotations

import json
from pathlib import Path

from docvqa.extractors.llm import LLMExtractor
from docvqa.pipeline.schemas import ExtractionRequest


class _StubClient:
    def generate(self, prompt: str):  # pragma: no cover - trivial
        return {
            "choices": [
                {
                    "message": {
                        "content": json.dumps({"summary": "ok", "fields": [], "answers": []})
                    }
                }
            ]
        }


def test_llm_extractor_parses_json():
    extractor = LLMExtractor(_StubClient())
    request = ExtractionRequest(
        doc_id="sample",
        document_path=Path("doc.pdf"),
        questions=["Example"],
        metadata={},
    )
    result = extractor.extract(request)
    assert result.content["summary"] == "ok"
