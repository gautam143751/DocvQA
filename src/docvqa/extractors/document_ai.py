from __future__ import annotations

"""Extractor that delegates to Google Document AI or similar services."""

import mimetypes
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

from docvqa.config.models import DocumentAIConfig
from docvqa.extractors.base import BaseExtractor, ExtractionError
from docvqa.pipeline.schemas import ExtractionRequest, ExtractionResult

try:  # pragma: no cover - optional dependency
    from google.cloud import documentai
    from google.oauth2 import service_account
except ImportError:  # pragma: no cover - optional dependency
    documentai = None
    service_account = None


@dataclass
class _DocumentAIResources:
    client: "documentai.DocumentProcessorServiceClient"
    name: str


class DocumentAIExtractor(BaseExtractor):
    """Extraction backend using Google Document AI processors."""

    def __init__(self, config: DocumentAIConfig) -> None:
        if documentai is None:
            msg = (
                "google-cloud-documentai is required for DocumentAIExtractor. Install the "
                "'document-ai' extra: pip install docvqa[document-ai]."
            )
            raise ImportError(msg)
        self._config = config
        self._resources = self._create_resources(config)

    def extract(self, request: ExtractionRequest) -> ExtractionResult:
        raw_document = self._build_raw_document(request.document_path)
        process_request = documentai.ProcessRequest(
            name=self._resources.name,
            raw_document=raw_document,
        )
        try:
            response = self._resources.client.process_document(process_request)
        except Exception as exc:  # pragma: no cover - network/external
            msg = "Document AI processing failed"
            raise ExtractionError(msg) from exc

        content = self._normalize_response(response, request)
        return ExtractionResult(doc_id=request.doc_id, content=content, raw_response=response.to_dict())

    def _create_resources(self, config: DocumentAIConfig) -> _DocumentAIResources:
        credentials = None
        if config.credentials_path:
            if service_account is None:
                msg = "google-auth is required when credentials_path is provided."
                raise ImportError(msg)
            credentials = service_account.Credentials.from_service_account_file(
                str(config.credentials_path)
            )
        client_options = None
        if config.endpoint:
            client_options = {"api_endpoint": config.endpoint}
        client = documentai.DocumentProcessorServiceClient(
            credentials=credentials, client_options=client_options
        )
        name = client.processor_path(config.project_id, config.location, config.processor_id)
        return _DocumentAIResources(client=client, name=name)

    def _build_raw_document(self, path: Path) -> "documentai.RawDocument":
        mime_type, _ = mimetypes.guess_type(path)
        if mime_type is None:
            mime_type = "application/pdf"
        with path.open("rb") as handle:
            content = handle.read()
        return documentai.RawDocument(content=content, mime_type=mime_type)

    @staticmethod
    def _normalize_response(
        response: "documentai.ProcessResponse", request: ExtractionRequest
    ) -> Dict[str, Any]:
        document = response.document
        entities = []
        for entity in getattr(document, "entities", []):
            entities.append(
                {
                    "type": entity.type_,
                    "mention_text": entity.mention_text,
                    "confidence": entity.confidence,
                }
            )
        tables = []
        for page in getattr(document, "pages", []):
            for table in getattr(page, "tables", []):
                tables.append(table.to_dict())

        return {
            "summary": document.text[:5000] if getattr(document, "text", "") else "",
            "fields": entities,
            "tables": tables,
            "answers": [],
            "warnings": [],
            "metadata": request.metadata,
        }


__all__ = ["DocumentAIExtractor"]
