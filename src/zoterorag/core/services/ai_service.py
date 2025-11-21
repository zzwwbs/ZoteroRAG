"""AI synthesis service for generating answers with inline citations."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Iterable, Sequence, Callable

import requests
from requests import Session

from ...config.settings_manager import SettingsManager
from .search_service import SearchMatch

logger = logging.getLogger(__name__)


class AIServiceError(RuntimeError):
    """Raised when AI analysis fails."""


class UnauthorizedAIServiceError(AIServiceError):
    """Raised when API key is missing or invalid."""


@dataclass(frozen=True)
class Citation:
    """Mapping between chunk placeholder and display index."""

    placeholder: str
    display: str


class AIService:
    """Encapsulates calls to OpenAI-compatible chat completion for analysis."""

    def __init__(
        self,
        settings_manager: SettingsManager,
        *,
        base_url: str = "https://api.openai.com/v1",
        model: str = "gpt-4o-mini",
        session_factory: Callable[[], Session] = requests.Session,
    ) -> None:
        self._settings_manager = settings_manager
        self._base_url = base_url.rstrip("/")
        self._model = model
        self._session_factory = session_factory
        self._session = self._session_factory()

    def analyze_chunks(self, query: str, matches: Sequence[SearchMatch], top_n: int = 10) -> str:
        """Send query and top N chunks to LLM and return synthesized answer with citations."""

        api_key = self._settings_manager.get_api_key()
        if not api_key:
            raise UnauthorizedAIServiceError("API key is not configured.")

        truncated = list(matches)[: max(1, min(top_n, 50))]
        citations = self._build_citations(truncated)
        prompt = self._build_prompt(query, truncated, citations)

        url = f"{self._base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self._model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are a scholarly assistant. Use the provided chunks to answer the query. "
                        "Cite chunks using their placeholders (e.g., [CHUNK_1]) exactly as provided."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.2,
        }

        try:
            response = self._session.post(url, json=payload, headers=headers, timeout=30)
        except requests.exceptions.RequestException as error:
            logger.exception("AI request failed due to network error.")
            raise AIServiceError("Network error while requesting AI analysis.") from error

        if response.status_code == 401:
            raise UnauthorizedAIServiceError("Invalid API key.")
        if not response.ok:
            raise AIServiceError(f"AI API error ({response.status_code}): {response.text}")

        data = response.json()
        try:
            content = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as error:
            raise AIServiceError("Invalid response format from AI API.") from error

        return self._apply_citations(content, citations)

    @staticmethod
    def _build_citations(matches: Sequence[SearchMatch]) -> list[Citation]:
        citations: list[Citation] = []
        for idx, _ in enumerate(matches, start=1):
            citations.append(Citation(placeholder=f"[CHUNK_{idx}]", display=f"[{idx}]"))
        return citations

    @staticmethod
    def _build_prompt(query: str, matches: Sequence[SearchMatch], citations: Sequence[Citation]) -> str:
        blocks: list[str] = [
            "Based on the following text chunks, provide a synthesized answer to the user's query. "
            "Reference the chunks using their identifiers (e.g., [CHUNK_1]).",
            f"User Query: {query}",
        ]
        for match, citation in zip(matches, citations):
            blocks.append(f"{citation.placeholder}\n{match.chunk.content}")
        return "\n\n".join(blocks)

    @staticmethod
    def _apply_citations(content: str, citations: Iterable[Citation]) -> str:
        updated = content
        for citation in citations:
            updated = updated.replace(citation.placeholder, citation.display)
        return updated
