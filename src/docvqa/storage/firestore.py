from __future__ import annotations

"""Firestore storage backend."""

from datetime import datetime
from typing import Optional

from docvqa.config.models import FirestoreConfig
from docvqa.pipeline.schemas import ExtractionResult
from docvqa.storage.base import BaseStorage

try:  # pragma: no cover - optional dependency
    from google.cloud import firestore
    from google.oauth2 import service_account
except ImportError:  # pragma: no cover - optional dependency
    firestore = None
    service_account = None


class FirestoreWriter(BaseStorage):
    """Writes results to a Firestore collection with batched commits."""

    def __init__(self, config: FirestoreConfig, run_id: Optional[str] = None) -> None:
        if firestore is None:
            msg = (
                "google-cloud-firestore is required for FirestoreWriter. Install dependency or "
                "switch storage provider."
            )
            raise ImportError(msg)

        credentials = None
        if config.credentials_path:
            if service_account is None:
                msg = "google-auth is required when credentials_path is provided."
                raise ImportError(msg)
            credentials = service_account.Credentials.from_service_account_file(
                str(config.credentials_path)
            )

        self._client = firestore.Client(project=config.project_id, credentials=credentials)
        self._collection_name = config.collection
        self._batch_size = config.batch_size
        self._batch = self._client.batch()
        self._pending = 0
        self._run_id = run_id or datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")

    def write(self, result: ExtractionResult) -> None:
        doc_ref = (
            self._client.collection(self._collection_name)
            .document(self._run_id)
            .collection("results")
            .document(result.doc_id)
        )
        self._batch.set(doc_ref, result.model_dump())
        self._pending += 1
        if self._pending >= self._batch_size:
            self._commit()

    def finalize(self) -> None:
        self._commit()

    def _commit(self) -> None:
        if self._pending == 0:
            return
        self._batch.commit()
        self._batch = self._client.batch()
        self._pending = 0


__all__ = ["FirestoreWriter"]
