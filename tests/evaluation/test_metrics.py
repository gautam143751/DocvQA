from __future__ import annotations

import pytest

import json

from docvqa.evaluation.loader import load_results
from docvqa.evaluation.metrics import compare_runs, compute_provider_metrics


@pytest.fixture
def sample_results(tmp_path):
    data = [
        {
            "doc_id": "doc-1",
            "content": {
                "summary": "Invoice total is 123",
                "fields": [{"name": "total", "value": "123"}],
                "answers": ["123"],
                "tables": [],
            },
        },
        {
            "doc_id": "doc-2",
            "content": {
                "summary": "",
                "fields": [],
                "answers": [],
                "tables": [{"rows": []}],
            },
        },
    ]
    path = tmp_path / "results.jsonl"
    with path.open("w", encoding="utf-8") as handle:
        for row in data:
            handle.write(json.dumps(row))
            handle.write("\n")
    return path


def test_load_and_metrics(sample_results):
    results = load_results(sample_results)
    metrics = compute_provider_metrics("provider-a", results)
    assert metrics.documents == 2
    assert pytest.approx(metrics.avg_field_count, rel=1e-6) == 0.5
    assert pytest.approx(metrics.empty_summary_rate, rel=1e-6) == 0.5


def test_compare_runs(sample_results, tmp_path):
    alt_data = [
        {
            "doc_id": "doc-1",
            "content": {
                "summary": "Invoice total is 120",
                "fields": [
                    {"name": "total", "value": "120"},
                    {"name": "date", "value": "2024-01-01"},
                ],
                "answers": ["120", "2024-01-01"],
                "tables": [],
            },
        }
    ]
    alt_path = tmp_path / "alt.jsonl"
    with alt_path.open("w", encoding="utf-8") as handle:
        for row in alt_data:
            handle.write(json.dumps(row))
            handle.write("\n")

    runs = {
        "provider-a": load_results(sample_results),
        "provider-b": load_results(alt_path),
    }
    report = compare_runs(runs)
    assert report.union_documents == 2
    assert report.shared_documents == 1
    assert report.provider_document_counts["provider-b"] == 1
