# DocVQA CLI

CLI-driven pipeline for extracting structured information from DocVQA datasets using either large language models or specialized document understanding APIs, with results persisted to Google Cloud Firestore or local JSON artifacts.

## Features
- Typer-based CLI with environment-aware configuration loading.
- Pluggable extractors: LLM completions or Google Document AI.
- Storage abstraction supporting Firestore (default) and local JSON output for offline tests.
- Dataset utilities that consume `manifest.jsonl` manifests or iterate over document directories.
- Evaluation tooling to compare outputs across multiple providers.
- Lightweight pytest suite covering configuration, dataset iteration, extractor normalization, evaluation, and pipeline orchestration.

## Getting Started
1. Create a virtual environment and install dependencies:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -e .[dev]
   ```
2. Copy the sample dataset manifest from `assets/samples/` or prepare your own subset (see `docs/datasets.md`).
3. Define a configuration file or `.env` with connection details (see `docs/configuration.md`).

## Running the Pipeline
```bash
docvqa-cli run --config configs/pipeline.yaml
```

Override inputs via flags when needed:
```bash
docvqa-cli run --dataset-path assets/samples --limit 5 --storage-provider local_json
```

## Evaluating Multiple Providers
After running extractions with different providers, compare their outputs:

```bash
docvqa-cli evaluate \
  --run openai=artifacts/results/openai.jsonl \
  --run document_ai=artifacts/results/document-ai.jsonl
```

The command reports average field, answer, table counts, summary coverage, and document overlap across providers.

## Tests & Quality Checks
Run the test suite with:
```bash
pytest
```

Before pushing, execute formatters and lint via your configured `pre-commit` hooks.

## Recent Changes
- Lowered the minimum supported Python version to 3.9 and aligned formatter targets so editable installs succeed on systems without Python 3.10+.
- Replaced usage of Python 3.10-style union type hints with `Optional[...]` for compatibility with Python 3.9 runtime type checking.

## Next Steps
- Extend `src/docvqa/extractors/` with provider-specific logic (Azure Form Recognizer, AWS Textract).
- Incorporate ground-truth annotations to score answer accuracy and field precision/recall.
- Wire up CI to run `pytest --cov=docvqa` and enforce coverage thresholds.
