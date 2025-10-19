from __future__ import annotations

import json

from docvqa.config.models import LocalJSONConfig, PipelineConfig
from docvqa.data.dataset import DocumentExample
from docvqa.extractors.base import BaseExtractor
from docvqa.pipeline.schemas import ExtractionRequest, ExtractionResult
from docvqa.pipeline.run import PipelineRunner
from docvqa.storage.local import LocalJSONWriter


class _FakeExtractor(BaseExtractor):
    def extract(self, request: ExtractionRequest) -> ExtractionResult:  # pragma: no cover - simple
        return ExtractionResult(
            doc_id=request.doc_id,
            content={"doc": request.doc_id, "questions": request.questions or []},
            raw_response={"status": "ok"},
        )


def test_pipeline_runner_writes_results(tmp_path):
    dataset = [
        DocumentExample(doc_id="doc-1", document_path=tmp_path / "doc-1.txt"),
        DocumentExample(doc_id="doc-2", document_path=tmp_path / "doc-2.txt"),
    ]
    storage = LocalJSONWriter(LocalJSONConfig(output_dir=tmp_path / "out"), run_id="test-run")
    runner = PipelineRunner(dataset, _FakeExtractor(), storage, PipelineConfig())

    stats = runner.run()

    assert stats.processed == 2
    assert stats.succeeded == 2
    output_file = tmp_path / "out" / "test-run.jsonl"
    contents = output_file.read_text(encoding="utf-8").strip().splitlines()
    assert len(contents) == 2
    for line in contents:
        payload = json.loads(line)
        assert payload["raw_response"]["status"] == "ok"
