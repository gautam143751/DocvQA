from __future__ import annotations

"""Local JSON storage backend for development."""

import json
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from docvqa.config.models import LocalJSONConfig
from docvqa.pipeline.schemas import ExtractionResult
from docvqa.storage.base import BaseStorage


class LocalJSONWriter(BaseStorage):
    """Accumulates results and writes them to a JSONL file."""

    def __init__(self, config: LocalJSONConfig, run_id: Optional[str] = None) -> None:
        self._config = config
        self._config.output_dir.mkdir(parents=True, exist_ok=True)
        self._run_id = run_id or datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
        self._buffer: List[ExtractionResult] = []

    def write(self, result: ExtractionResult) -> None:
        self._buffer.append(result)

    def finalize(self) -> None:
        if not self._buffer:
            return
        output_path = self._config.output_dir / f"{self._run_id}.jsonl"
        with output_path.open("w", encoding="utf-8") as handle:
            for result in self._buffer:
                handle.write(json.dumps(result.model_dump(), indent=self._config.indent))
                handle.write("\n")


__all__ = ["LocalJSONWriter"]
