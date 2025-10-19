# Configuration Guide

Configure the DocVQA CLI via a combination of configuration files, environment variables, and CLI flags. The precedence order is CLI flags → environment variables → config file defaults.

## Environment Variables

Set values in a `.env` file at the repository root or export them in your shell. Supported keys:

- `DOCVQA_DATASET_PATH` – folder containing prepared DocVQA documents and `manifest.jsonl`.
- `DOCVQA_DATASET_LIMIT` – optional integer cap for processed documents.
- `DOCVQA_EXTRACTOR_PROVIDER` – `llm` or `document_ai`.
- `DOCVQA_LLM_API_BASE`, `DOCVQA_LLM_API_KEY`, `DOCVQA_LLM_MODEL` – core LLM connection details.
- `DOCVQA_DOCUMENT_AI_PROJECT_ID`, `DOCVQA_DOCUMENT_AI_PROCESSOR_ID`, `DOCVQA_DOCUMENT_AI_LOCATION` – Google Document AI identifiers.
- `DOCVQA_STORAGE_PROVIDER` – `local_json` or `firestore`.
- `DOCVQA_FIRESTORE_PROJECT_ID`, `DOCVQA_FIRESTORE_COLLECTION` – Firestore persistence settings.
- `DOCVQA_LOG_LEVEL` – logging verbosity (`DEBUG`, `INFO`, `WARNING`, `ERROR`).

Provider-specific overrides exist for temperature, batch settings, credentials, and timeouts; consult `docvqa/config/models.py` for the complete list.

## Config Files

Create a YAML or JSON file and pass it with `--config`:

```yaml
# configs/pipeline.yaml
dataset:
  path: assets/samples
extractor:
  provider: llm
  llm:
    api_base: https://api.openai.com/v1/chat/completions
    api_key: ${LLM_API_KEY}
    model: gpt-4o
storage:
  provider: firestore
  firestore:
    project_id: my-gcp-project
    collection: docvqa_runs
pipeline:
  concurrency: 2
  retry_attempts: 2
```

Inline shell expansions (e.g. `${LLM_API_KEY}`) are not resolved automatically; prefer using `.env` for secrets.
