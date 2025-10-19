from __future__ import annotations

"""HTTP client used by LLM extractors."""

from typing import Any, Dict

import requests
from requests import Response

from docvqa.config.models import LLMConfig
from docvqa.extractors.base import ExtractionError


class LLMClient:
    """Minimal client compatible with OpenAI-style chat completion APIs."""

    def __init__(self, config: LLMConfig) -> None:
        self._config = config

    def generate(self, prompt: str) -> Dict[str, Any]:
        """Send a prompt to the LLM and return the JSON response."""

        payload = {
            "model": self._config.model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are a helpful assistant that extracts structured information from "
                        "documents. Respond strictly with JSON."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            "temperature": self._config.temperature,
            "max_tokens": self._config.max_output_tokens,
            "response_format": {"type": "json_object"},
        }
        headers = {
            "Authorization": f"Bearer {self._config.api_key}",
            "Content-Type": "application/json",
        }

        try:
            response = requests.post(
                self._config.api_base,
                json=payload,
                headers=headers,
                timeout=self._config.timeout_seconds,
            )
        except requests.RequestException as exc:  # pragma: no cover - network failures
            msg = "LLM request failed"
            raise ExtractionError(msg) from exc

        self._raise_for_status(response)

        return response.json()

    @staticmethod
    def _raise_for_status(response: Response) -> None:
        try:
            response.raise_for_status()
        except requests.HTTPError as exc:  # pragma: no cover - network failures
            msg = f"LLM API returned {response.status_code}: {response.text}"
            raise ExtractionError(msg) from exc


__all__ = ["LLMClient"]
