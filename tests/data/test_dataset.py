from __future__ import annotations

import json
from pathlib import Path

from docvqa.data.dataset import DEFAULT_MANIFEST, DocVQADataset


def test_dataset_reads_manifest(tmp_path):
    (tmp_path / "sample_document.txt").write_text("sample", encoding="utf-8")
    manifest_entry = {
        "id": "doc-1",
        "document_path": "sample_document.txt",
        "questions": ["What is inside?"],
        "metadata": {"split": "test"},
    }
    manifest_path = tmp_path / DEFAULT_MANIFEST
    manifest_path.write_text(json.dumps(manifest_entry) + "\n", encoding="utf-8")

    dataset = DocVQADataset(tmp_path)
    samples = list(dataset)
    assert len(samples) == 1
    sample = samples[0]
    assert sample.doc_id == "doc-1"
    assert sample.document_path == Path(tmp_path / "sample_document.txt")
    assert sample.questions == ["What is inside?"]
