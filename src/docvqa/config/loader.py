from __future__ import annotations

"""Configuration loading utilities."""

from pathlib import Path
from typing import Callable, Dict, Iterable, Mapping, MutableMapping, Optional

import yaml
from dotenv import load_dotenv

from .models import AppConfig


# Mapping of environment variables to config paths and optional converters.
ENV_VAR_MAPPING: Dict[str, tuple[tuple[str, ...], Callable[[str], object]]] = {
    "DOCVQA_DATASET_PATH": (("dataset", "path"), lambda v: Path(v).expanduser()),
    "DOCVQA_DATASET_LIMIT": (("dataset", "limit"), int),
    "DOCVQA_EXTRACTOR_PROVIDER": (("extractor", "provider"), str.lower),
    "DOCVQA_LLM_PROVIDER": (("extractor", "llm", "provider"), str),
    "DOCVQA_LLM_API_BASE": (("extractor", "llm", "api_base"), str),
    "DOCVQA_LLM_API_KEY": (("extractor", "llm", "api_key"), str),
    "DOCVQA_LLM_MODEL": (("extractor", "llm", "model"), str),
    "DOCVQA_LLM_TEMPERATURE": (("extractor", "llm", "temperature"), float),
    "DOCVQA_LLM_MAX_OUTPUT_TOKENS": (("extractor", "llm", "max_output_tokens"), int),
    "DOCVQA_LLM_TIMEOUT_SECONDS": (("extractor", "llm", "timeout_seconds"), float),
    "DOCVQA_DOCUMENT_AI_PROJECT_ID": (("extractor", "document_ai", "project_id"), str),
    "DOCVQA_DOCUMENT_AI_LOCATION": (("extractor", "document_ai", "location"), str),
    "DOCVQA_DOCUMENT_AI_PROCESSOR_ID": (("extractor", "document_ai", "processor_id"), str),
    "DOCVQA_DOCUMENT_AI_CREDENTIALS": (
        ("extractor", "document_ai", "credentials_path"),
        lambda v: Path(v).expanduser(),
    ),
    "DOCVQA_DOCUMENT_AI_ENDPOINT": (("extractor", "document_ai", "endpoint"), str),
    "DOCVQA_DOCUMENT_AI_TIMEOUT_SECONDS": (
        ("extractor", "document_ai", "timeout_seconds"),
        float,
    ),
    "DOCVQA_STORAGE_PROVIDER": (("storage", "provider"), str.lower),
    "DOCVQA_FIRESTORE_PROJECT_ID": (("storage", "firestore", "project_id"), str),
    "DOCVQA_FIRESTORE_COLLECTION": (("storage", "firestore", "collection"), str),
    "DOCVQA_FIRESTORE_BATCH_SIZE": (("storage", "firestore", "batch_size"), int),
    "DOCVQA_FIRESTORE_CREDENTIALS": (
        ("storage", "firestore", "credentials_path"),
        lambda v: Path(v).expanduser(),
    ),
    "DOCVQA_LOCAL_JSON_OUTPUT_DIR": (
        ("storage", "local_json", "output_dir"),
        lambda v: Path(v).expanduser(),
    ),
    "DOCVQA_PIPELINE_CONCURRENCY": (("pipeline", "concurrency"), int),
    "DOCVQA_PIPELINE_RETRY_ATTEMPTS": (("pipeline", "retry_attempts"), int),
    "DOCVQA_PIPELINE_RETRY_BACKOFF_SECONDS": (("pipeline", "retry_backoff_seconds"), float),
    "DOCVQA_LOG_LEVEL": (("logging", "level"), str.upper),
}


def deep_update(base: MutableMapping, updates: Mapping) -> MutableMapping:
    """Recursively update ``base`` with ``updates`` and return the modified mapping."""

    for key, value in updates.items():
        if isinstance(value, Mapping) and isinstance(base.get(key), MutableMapping):
            deep_update(base[key], value)
        else:
            base[key] = value
    return base


def apply_env_overrides(config_dict: MutableMapping) -> MutableMapping:
    """Merge environment variable overrides into the config dictionary."""

    from os import environ

    for env_key, (path, converter) in ENV_VAR_MAPPING.items():
        if env_key not in environ or environ[env_key] == "":
            continue
        value = converter(environ[env_key])
        cursor = config_dict
        for part in path[:-1]:
            cursor = cursor.setdefault(part, {})
        cursor[path[-1]] = value
    return config_dict


def load_config(
    config_path: Optional[Path] = None,
    overrides: Optional[Mapping[str, object]] = None,
) -> AppConfig:
    """Load application configuration from file, environment variables, and overrides."""

    load_dotenv()

    data: MutableMapping[str, object] = {}

    if config_path is not None:
        if not config_path.exists():
            msg = f"Configuration file not found: {config_path}"
            raise FileNotFoundError(msg)
        with config_path.open("r", encoding="utf-8") as handle:
            file_data = yaml.safe_load(handle) or {}
        if not isinstance(file_data, Mapping):
            msg = "Configuration file must define a mapping at the top level."
            raise ValueError(msg)
        data.update(file_data)

    apply_env_overrides(data)

    if overrides:
        deep_update(data, overrides)

    return AppConfig.from_dict(data)


__all__ = ["load_config"]
