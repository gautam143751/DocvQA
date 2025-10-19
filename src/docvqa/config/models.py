from __future__ import annotations

"""Configuration models for the DocVQA pipeline."""

from enum import Enum
from pathlib import Path
from typing import Literal, Optional

from pydantic import BaseModel, Field, field_validator


class ExtractorProvider(str, Enum):
    """Supported extraction backends."""

    LLM = "llm"
    DOCUMENT_AI = "document_ai"


class DatasetConfig(BaseModel):
    """Configuration for dataset ingestion."""

    path: Path = Field(..., description="Directory containing DocVQA samples.")
    limit: Optional[int] = Field(None, ge=1, description="Optional max number of documents to process.")


class LLMConfig(BaseModel):
    """Parameters for LLM-backed extraction."""

    provider: str = Field("openai", description="Identifier for the LLM provider.")
    api_base: str = Field(..., description="Base URL for the LLM API endpoint.")
    api_key: str = Field(..., description="Authentication token for the LLM provider.")
    model: str = Field(..., description="Model identifier to query.")
    temperature: float = Field(0.0, ge=0.0, le=2.0)
    max_output_tokens: int = Field(1024, gt=0)
    timeout_seconds: float = Field(60.0, gt=0)


class DocumentAIConfig(BaseModel):
    """Parameters for specialized document extraction API providers."""

    project_id: str = Field(..., description="GCP project hosting Document AI processors.")
    location: str = Field(..., description="Document AI processor location, e.g. 'us' or 'eu'.")
    processor_id: str = Field(..., description="Document AI processor ID.")
    credentials_path: Optional[Path] = Field(
        None, description="Optional path to service account JSON credentials."
    )
    endpoint: Optional[str] = Field(None, description="Override endpoint for Document AI API.")
    timeout_seconds: float = Field(60.0, gt=0)


class ExtractorConfig(BaseModel):
    """Top-level extractor configuration block."""

    provider: ExtractorProvider = Field(default=ExtractorProvider.LLM)
    llm: Optional[LLMConfig] = None
    document_ai: Optional[DocumentAIConfig] = Field(None, alias="documentAI")

    @field_validator("llm")
    @classmethod
    def require_llm_config(cls, value: Optional[LLMConfig], info):
        provider = info.data.get("provider")
        if provider == ExtractorProvider.LLM and value is None:
            msg = "LLM extractor selected but 'llm' configuration is missing."
            raise ValueError(msg)
        return value

    @field_validator("document_ai")
    @classmethod
    def require_document_ai_config(cls, value: Optional[DocumentAIConfig], info):
        provider = info.data.get("provider")
        if provider == ExtractorProvider.DOCUMENT_AI and value is None:
            msg = "Document AI extractor selected but 'document_ai' configuration is missing."
            raise ValueError(msg)
        return value


class FirestoreConfig(BaseModel):
    """Firestore persistence settings."""

    project_id: str = Field(..., description="GCP project for Firestore.")
    collection: str = Field(
        "docvqa_runs",
        description="Root collection name for storing extraction results.",
    )
    batch_size: int = Field(20, ge=1, le=500)
    credentials_path: Optional[Path] = Field(
        None, description="Optional path to service account JSON credentials."
    )


class LocalJSONConfig(BaseModel):
    """Local JSON persistence for offline development."""

    output_dir: Path = Field(
        Path("artifacts/results"), description="Directory to store JSON output files."
    )
    indent: int = Field(2, ge=0, le=4)


class StorageProvider(str, Enum):
    """Supported persistence backends."""

    FIRESTORE = "firestore"
    LOCAL_JSON = "local_json"


class StorageConfig(BaseModel):
    """Top-level storage configuration block."""

    provider: StorageProvider = Field(default=StorageProvider.LOCAL_JSON)
    firestore: Optional[FirestoreConfig] = None
    local_json: Optional[LocalJSONConfig] = None

    @field_validator("firestore")
    @classmethod
    def require_firestore(cls, value: Optional[FirestoreConfig], info):
        provider = info.data.get("provider")
        if provider == StorageProvider.FIRESTORE and value is None:
            msg = "Firestore storage selected but 'firestore' configuration is missing."
            raise ValueError(msg)
        return value

    @field_validator("local_json")
    @classmethod
    def require_local(cls, value: Optional[LocalJSONConfig], info):
        provider = info.data.get("provider")
        if provider == StorageProvider.LOCAL_JSON and value is None:
            return LocalJSONConfig()
        return value


class LoggingConfig(BaseModel):
    """Logging-related configuration."""

    level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"


class PipelineConfig(BaseModel):
    """Configuration for pipeline-specific options."""

    concurrency: int = Field(1, ge=1, le=16, description="Number of concurrent workers.")
    retry_attempts: int = Field(3, ge=0, le=5)
    retry_backoff_seconds: float = Field(2.0, ge=0.1)


class AppConfig(BaseModel):
    """Root configuration model for the DocVQA CLI."""

    dataset: DatasetConfig
    extractor: ExtractorConfig
    storage: StorageConfig
    pipeline: PipelineConfig = PipelineConfig()
    logging: LoggingConfig = LoggingConfig()

    @classmethod
    def from_dict(cls, data: dict) -> "AppConfig":
        return cls.model_validate(data)
