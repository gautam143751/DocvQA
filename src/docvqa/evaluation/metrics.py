from __future__ import annotations

"""Simple evaluation metrics for comparing extraction outputs across providers."""

from statistics import mean
from typing import Dict, List, Mapping, Optional, Sequence

from pydantic import BaseModel, Field

from docvqa.pipeline.schemas import ExtractionResult


class ProviderMetrics(BaseModel):
    """Aggregate metrics for a single extractor provider."""

    provider: str
    documents: int
    avg_field_count: float = Field(0.0, description="Average number of structured fields extracted.")
    avg_answer_count: float = Field(0.0, description="Average number of answers returned.")
    avg_table_count: float = Field(0.0, description="Average number of tables captured.")
    avg_summary_word_count: float = Field(
        0.0, description="Average word count of the summary field."
    )
    empty_summary_rate: float = Field(
        0.0, description="Proportion of documents whose summary field is empty."
    )


class EvaluationReport(BaseModel):
    """Comparison report across multiple extraction providers."""

    providers: List[ProviderMetrics]
    union_documents: int
    shared_documents: int
    provider_document_counts: Dict[str, int]


def _safe_mean(values: Sequence[float]) -> float:
    return float(mean(values)) if values else 0.0


def _word_count(text: Optional[str]) -> int:
    if not text:
        return 0
    return len(text.split())


def compute_provider_metrics(provider: str, results: Sequence[ExtractionResult]) -> ProviderMetrics:
    documents = len(results)
    if documents == 0:
        return ProviderMetrics(provider=provider, documents=0)

    field_counts: List[int] = []
    answer_counts: List[int] = []
    table_counts: List[int] = []
    summary_word_counts: List[int] = []
    empty_summary = 0

    for result in results:
        content = result.content
        fields = content.get("fields") or []
        answers = content.get("answers") or []
        tables = content.get("tables") or []
        summary = content.get("summary") or ""

        field_counts.append(len(fields))
        answer_counts.append(len(answers))
        table_counts.append(len(tables))
        summary_word_counts.append(_word_count(summary))
        if not summary.strip():
            empty_summary += 1

    return ProviderMetrics(
        provider=provider,
        documents=documents,
        avg_field_count=_safe_mean(field_counts),
        avg_answer_count=_safe_mean(answer_counts),
        avg_table_count=_safe_mean(table_counts),
        avg_summary_word_count=_safe_mean(summary_word_counts),
        empty_summary_rate=empty_summary / documents,
    )


def compare_runs(runs: Mapping[str, Sequence[ExtractionResult]]) -> EvaluationReport:
    """Compute aggregate metrics for multiple extractor runs."""

    provider_metrics: List[ProviderMetrics] = []
    document_sets: Dict[str, set[str]] = {}

    for provider, results in runs.items():
        provider_metrics.append(compute_provider_metrics(provider, results))
        document_sets[provider] = {result.doc_id for result in results}

    if document_sets:
        union_documents = len(set().union(*document_sets.values()))
        shared_documents = len(set.intersection(*document_sets.values()))
    else:
        union_documents = 0
        shared_documents = 0

    provider_document_counts = {provider: len(doc_ids) for provider, doc_ids in document_sets.items()}

    provider_metrics.sort(key=lambda metric: metric.provider)

    return EvaluationReport(
        providers=provider_metrics,
        union_documents=union_documents,
        shared_documents=shared_documents,
        provider_document_counts=provider_document_counts,
    )


__all__ = ["ProviderMetrics", "EvaluationReport", "compare_runs", "compute_provider_metrics"]
