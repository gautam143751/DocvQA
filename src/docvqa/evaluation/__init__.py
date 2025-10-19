"""Evaluation utilities for DocVQA extraction outputs."""

from .metrics import EvaluationReport, ProviderMetrics, compare_runs
from .loader import load_results

__all__ = [
    "EvaluationReport",
    "ProviderMetrics",
    "compare_runs",
    "load_results",
]
