from __future__ import annotations

"""Pipeline orchestration."""

from concurrent.futures import Future, ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from typing import Iterable, Optional

from docvqa.config.models import PipelineConfig
from docvqa.data.dataset import DocVQADataset
from docvqa.extractors.base import BaseExtractor, ExtractionError
from docvqa.pipeline.schemas import ExtractionResult
from docvqa.storage.base import BaseStorage
from docvqa.utils.logging import get_logger


@dataclass
class PipelineStats:
    """Aggregated statistics for a pipeline run."""

    processed: int = 0
    succeeded: int = 0
    failed: int = 0


class PipelineRunner:
    """Coordinates dataset iteration, extraction, and persistence."""

    def __init__(
        self,
        dataset: DocVQADataset,
        extractor: BaseExtractor,
        storage: BaseStorage,
        config: PipelineConfig,
    ) -> None:
        self._dataset = dataset
        self._extractor = extractor
        self._storage = storage
        self._config = config
        self._logger = get_logger(__name__)

    def run(self) -> PipelineStats:
        stats = PipelineStats()
        if self._config.concurrency <= 1:
            for example in self._dataset:
                stats.processed += 1
                try:
                    result = self._extractor.from_example(example)
                except ExtractionError as exc:
                    stats.failed += 1
                    self._logger.error("extraction_failed", doc_id=example.doc_id, error=str(exc))
                    continue
                self._storage.write(result)
                stats.succeeded += 1
        else:
            stats = self._run_concurrent()

        self._storage.finalize()
        self._logger.info(
            "pipeline_completed",
            processed=stats.processed,
            succeeded=stats.succeeded,
            failed=stats.failed,
        )
        return stats

    def _run_concurrent(self) -> PipelineStats:
        stats = PipelineStats()
        with ThreadPoolExecutor(max_workers=self._config.concurrency) as executor:
            futures: dict[Future[ExtractionResult], str] = {}
            for example in self._dataset:
                stats.processed += 1

                def _task(ex=example):
                    return self._extractor.from_example(ex)

                futures[executor.submit(_task)] = example.doc_id

            for future in as_completed(futures):
                doc_id = futures[future]
                try:
                    result = future.result()
                except ExtractionError as exc:
                    stats.failed += 1
                    self._logger.error("extraction_failed", doc_id=doc_id, error=str(exc))
                    continue
                except Exception as exc:  # pragma: no cover - unexpected
                    stats.failed += 1
                    self._logger.error("unexpected_failure", doc_id=doc_id, error=str(exc))
                    continue
                self._storage.write(result)
                stats.succeeded += 1
        return stats


__all__ = ["PipelineRunner", "PipelineStats"]
