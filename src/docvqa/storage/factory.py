from __future__ import annotations

"""Factory helpers for storage backends."""

from typing import Optional

from docvqa.config.models import StorageConfig, StorageProvider
from docvqa.storage.base import BaseStorage
from docvqa.storage.firestore import FirestoreWriter
from docvqa.storage.local import LocalJSONWriter


def create_storage(config: StorageConfig, *, run_id: Optional[str] = None) -> BaseStorage:
    """Instantiate a storage backend based on configuration."""

    if config.provider == StorageProvider.FIRESTORE:
        if config.firestore is None:  # pragma: no cover - validated earlier
            msg = "Firestore configuration is required for firestore provider"
            raise ValueError(msg)
        return FirestoreWriter(config.firestore, run_id=run_id)

    if config.provider == StorageProvider.LOCAL_JSON:
        target_config = config.local_json or config.model_fields["local_json"].default
        return LocalJSONWriter(target_config, run_id=run_id)

    msg = f"Unsupported storage provider: {config.provider}"
    raise ValueError(msg)


__all__ = ["create_storage"]
