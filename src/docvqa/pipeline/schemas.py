from __future__ import annotations

"""Shared pipeline schemas."""

from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ExtractionRequest(BaseModel):
    """Input payload passed to extractors."""

    doc_id: str
    document_path: Path
    questions: Optional[List[str]] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ExtractionResult(BaseModel):
    """Normalized extraction output stored downstream."""

    doc_id: str
    content: Dict[str, Any]
    raw_response: Optional[Dict[str, Any]] = None


__all__ = ["ExtractionRequest", "ExtractionResult"]
