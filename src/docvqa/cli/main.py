from __future__ import annotations

"""Command line entrypoint for DocVQA pipeline."""

from pathlib import Path
from typing import Dict, List, Optional

import typer

from docvqa.config.loader import load_config
from docvqa.config.models import ExtractorProvider, StorageProvider
from docvqa.data.dataset import DocVQADataset
from docvqa.extractors.factory import create_extractor
from docvqa.evaluation.loader import load_results
from docvqa.evaluation.metrics import compare_runs
from docvqa.pipeline.schemas import ExtractionResult
from docvqa.storage.factory import create_storage
from docvqa.pipeline.run import PipelineRunner
from docvqa.utils.logging import configure_logging, get_logger

app = typer.Typer(help="Run document extraction pipelines against DocVQA datasets.")


def _build_overrides(
    dataset_path: Optional[Path],
    limit: Optional[int],
    extractor_provider: Optional[str],
    storage_provider: Optional[str],
) -> dict:
    overrides: dict[str, object] = {}
    if dataset_path is not None:
        overrides.setdefault("dataset", {})["path"] = str(dataset_path)
    if limit is not None:
        overrides.setdefault("dataset", {})["limit"] = limit
    if extractor_provider is not None:
        overrides.setdefault("extractor", {})["provider"] = extractor_provider
    if storage_provider is not None:
        overrides.setdefault("storage", {})["provider"] = storage_provider
    return overrides


@app.command()
def run(
    config: Optional[Path] = typer.Option(
        None,
        "--config",
        "-c",
        help="Path to YAML/JSON configuration file.",
    ),
    dataset_path: Optional[Path] = typer.Option(
        None,
        help="Override dataset path from configuration/environment.",
    ),
    limit: Optional[int] = typer.Option(
        None,
        min=1,
        help="Maximum number of documents to process.",
    ),
    extractor_provider: Optional[ExtractorProvider] = typer.Option(
        None,
        case_sensitive=False,
        help="Extraction backend to use (llm or document_ai).",
    ),
    storage_provider: Optional[StorageProvider] = typer.Option(
        None,
        case_sensitive=False,
        help="Storage backend to use (firestore or local_json).",
    ),
    run_id: Optional[str] = typer.Option(
        None,
        help="Optional identifier for this pipeline run.",
    ),
) -> None:
    """Execute the DocVQA extraction pipeline."""

    overrides = _build_overrides(
        dataset_path,
        limit,
        extractor_provider.value if extractor_provider else None,
        storage_provider.value if storage_provider else None,
    )

    try:
        app_config = load_config(config, overrides)
    except Exception as exc:  # pragma: no cover - configuration errors
        typer.echo(f"Failed to load configuration: {exc}", err=True)
        raise typer.Exit(code=1) from exc

    configure_logging(app_config.logging.level)
    logger = get_logger(__name__)

    dataset = DocVQADataset(
        app_config.dataset.path,
        limit=app_config.dataset.limit,
    )

    try:
        extractor = create_extractor(app_config.extractor)
    except Exception as exc:
        logger.error("extractor_init_failed", error=str(exc))
        raise typer.Exit(code=2) from exc

    try:
        storage = create_storage(app_config.storage, run_id=run_id)
    except Exception as exc:
        logger.error("storage_init_failed", error=str(exc))
        raise typer.Exit(code=3) from exc

    runner = PipelineRunner(dataset, extractor, storage, app_config.pipeline)
    stats = runner.run()
    logger.info(
        "run_complete",
        processed=stats.processed,
        succeeded=stats.succeeded,
        failed=stats.failed,
    )


@app.command()
def evaluate(
    run: List[str] = typer.Option(
        ...,  # type: ignore[arg-type]
        "--run",
        "-r",
        help="Labelled run definition of the form provider=path/to/results.jsonl. Repeat for multiple runs.",
    )
) -> None:
    """Compare extraction outputs across providers using aggregated metrics."""

    runs: Dict[str, List[ExtractionResult]] = {}
    for entry in run:
        if "=" not in entry:
            raise typer.BadParameter(
                "Run definition must match provider=path/to/results.jsonl", param_hint="--run"
            )
        provider, path_str = entry.split("=", 1)
        provider = provider.strip()
        if not provider:
            raise typer.BadParameter("Provider label cannot be empty.", param_hint="--run")
        path = Path(path_str.strip())
        try:
            runs[provider] = load_results(path)
        except FileNotFoundError as exc:
            raise typer.BadParameter(str(exc), param_hint="--run") from exc

    if len(runs) < 2:
        raise typer.BadParameter("Provide at least two runs to compare.", param_hint="--run")

    report = compare_runs(runs)

    typer.echo("Provider Metrics:")
    for metrics in report.providers:
        typer.echo(
            f"- {metrics.provider}: docs={metrics.documents}, avg_fields={metrics.avg_field_count:.2f}, "
            f"avg_answers={metrics.avg_answer_count:.2f}, avg_tables={metrics.avg_table_count:.2f}, "
            f"avg_summary_words={metrics.avg_summary_word_count:.2f}, empty_summary_rate={metrics.empty_summary_rate:.2%}"
        )

    typer.echo(
        "\nDocument Coverage: union={union} shared={shared}".format(
            union=report.union_documents, shared=report.shared_documents
        )
    )
    for provider, count in report.provider_document_counts.items():
        typer.echo(f"  - {provider}: {count}")


if __name__ == "__main__":
    app()
