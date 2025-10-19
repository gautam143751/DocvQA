from __future__ import annotations

"""Helpers for loading ExtractionResult payloads from JSONL artifacts."""

import json
from pathlib import Path
from typing import Dict, List

from docvqa.pipeline.schemas import ExtractionResult


def load_results(path: Path) -> List[ExtractionResult]:
    """Load extraction results from a JSONL file saved by the pipeline."""

    if not path.exists():
        msg = f"Results file not found: {path}"
        raise FileNotFoundError(msg)

    results: List[ExtractionResult] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            payload: Dict[str, object] = json.loads(line)
            results.append(ExtractionResult.model_validate(payload))
    return results


__all__ = ["load_results"]
