from __future__ import annotations

"""Prompt generation utilities."""

from typing import List

from docvqa.pipeline.schemas import ExtractionRequest


def build_prompt(request: ExtractionRequest) -> str:
    """Create a prompt instructing the LLM to extract document data."""

    instructions: List[str] = [
        "You receive a document and optional questions from the DocVQA dataset.",
        "Return a JSON object with keys: summary, fields, tables, answers, warnings.",
        "Use empty lists when information is missing.",
    ]
    if request.questions:
        instructions.append("Answer the provided questions and include them in the answers array.")
    instructions.append("Document path: {path}".format(path=request.document_path))
    if request.metadata:
        instructions.append(f"Metadata: {request.metadata}")
    if request.questions:
        instructions.append(f"Questions: {request.questions}")

    return "\n".join(instructions)


__all__ = ["build_prompt"]
