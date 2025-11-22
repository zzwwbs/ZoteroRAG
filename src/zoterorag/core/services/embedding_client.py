"""Client for retrieving embeddings from an OpenAI-compatible API."""

from __future__ import annotations

import logging
from typing import Any, Callable, Tuple

import requests
from requests import Response, Session

from ...config.settings_manager import SettingsManager
from ..data.models import TokenUsage

logger = logging.getLogger(__name__)


class EmbeddingClientError(RuntimeError):
    """Base exception for embedding-related failures."""


class UnauthorizedEmbeddingError(EmbeddingClientError):
    """Raised when the API key is invalid or missing."""


class RateLimitEmbeddingError(EmbeddingClientError):
    """Raised when the API rejects requests due to rate limits."""


class EmbeddingClient:
    """Encapsulates calls to an OpenAI-compatible embeddings endpoint."""

    def __init__(
        self,
        settings_manager: SettingsManager,
        *,
        base_url: str = "https://api.openai.com/v1",
        model: str = "text-embedding-ada-002",
        session_factory: Callable[[], Session] = requests.Session,
    ) -> None:
        self._settings_manager = settings_manager
        self._base_url = base_url.rstrip("/")
        self._model = model
        self._session_factory = session_factory
        self._session = self._session_factory()

    def get_embedding(self, text: str) -> tuple[list[float], TokenUsage]:
        """Send text to the embeddings endpoint and return the vector plus token usage."""

        api_key = self._settings_manager.get_api_key()
        if not api_key:
            raise UnauthorizedEmbeddingError("API key is not configured.")

        url = f"{self._base_url}/embeddings"
        payload = {"input": [text], "model": self._model}
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

        try:
            response = self._session.post(url, json=payload, headers=headers, timeout=30)
        except requests.exceptions.RequestException as error:
            logger.exception("Embedding request failed due to network error.")
            raise EmbeddingClientError("Network error while requesting embeddings.") from error

        self._handle_errors(response)
        data = response.json()
        try:
            vector = data["data"][0]["embedding"]
            usage = self._build_usage(data.get("usage") or {}, model=self._model)
            return vector, usage
        except (KeyError, IndexError, TypeError) as error:
            logger.exception("Unexpected embedding response format.")
            raise EmbeddingClientError("Invalid response format from embeddings API.") from error

    def _handle_errors(self, response: Response) -> None:
        if response.ok:
            return

        status = response.status_code
        message = self._extract_error_message(response)

        if status == 401:
            raise UnauthorizedEmbeddingError(message or "Unauthorized")
        if status == 429:
            raise RateLimitEmbeddingError(message or "Rate limit exceeded")

        logger.error("Embedding API returned %s: %s", status, message)
        raise EmbeddingClientError(message or f"Embedding API error ({status})")

    @staticmethod
    def _extract_error_message(response: Response) -> str | None:
        try:
            payload = response.json()
        except ValueError:
            return response.text

        error_info = payload.get("error")
        if isinstance(error_info, dict):
            return error_info.get("message")
        if isinstance(error_info, str):
            return error_info
        return None

    def _build_usage(self, usage_payload: dict[str, Any], *, model: str) -> TokenUsage:
        tokens = int(usage_payload.get("total_tokens") or 0)
        prompt = int(usage_payload.get("prompt_tokens") or usage_payload.get("input_tokens") or 0)
        completion = int(usage_payload.get("completion_tokens") or usage_payload.get("output_tokens") or 0)
        return TokenUsage(
            operation="embedding",
            tokens_used=tokens,
            model=model,
            prompt_tokens=prompt,
            completion_tokens=completion,
        )
