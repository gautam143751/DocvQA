from __future__ import annotations

"""Dataset loading utilities for DocVQA samples."""

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterator, List, Optional

import json


DEFAULT_MANIFEST = "manifest.jsonl"


@dataclass
class DocumentExample:
    """Single DocVQA example used by the extraction pipeline."""

    doc_id: str
    document_path: Path
    questions: Optional[List[str]] = None
    metadata: Optional[Dict[str, object]] = None


class DocVQADataset:
    """Iterates over DocVQA samples defined in a manifest file or directory listing."""

    def __init__(self, root: Path, *, limit: Optional[int] = None) -> None:
        self.root = root
        self.limit = limit

    def __iter__(self) -> Iterator[DocumentExample]:
        if not self.root.exists():
            msg = f"Dataset path does not exist: {self.root}"
            raise FileNotFoundError(msg)

        manifest_path = self.root / DEFAULT_MANIFEST
        if manifest_path.exists():
            yield from self._from_manifest(manifest_path)
        else:
            yield from self._from_directory()

    def _from_manifest(self, manifest_path: Path) -> Iterator[DocumentExample]:
        count = 0
        with manifest_path.open("r", encoding="utf-8") as handle:
            for line in handle:
                if self.limit is not None and count >= self.limit:
                    break
                if not line.strip():
                    continue
                sample = json.loads(line)
                document_path = self.root / sample["document_path"]
                questions = sample.get("questions")
                metadata = sample.get("metadata")
                doc_id = sample.get("id") or document_path.stem
                yield DocumentExample(doc_id=doc_id, document_path=document_path, questions=questions, metadata=metadata)
                count += 1

    def _from_directory(self) -> Iterator[DocumentExample]:
        supported_suffixes = {".pdf", ".png", ".jpg", ".jpeg", ".tiff"}
        files = sorted(
            path for path in self.root.iterdir() if path.suffix.lower() in supported_suffixes
        )
        for index, document_path in enumerate(files):
            if self.limit is not None and index >= self.limit:
                break
            doc_id = document_path.stem
            yield DocumentExample(doc_id=doc_id, document_path=document_path)


__all__ = ["DocVQADataset", "DocumentExample", "DEFAULT_MANIFEST"]
