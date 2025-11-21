"""Service responsible for executing semantic search requests."""

from __future__ import annotations

import logging
from dataclasses import dataclass

from .embedding_client import EmbeddingClient, EmbeddingClientError
from .metadata_db_manager import MetadataDBManager
from .vector_db_manager import VectorDBManager

logger = logging.getLogger(__name__)


class SearchServiceError(RuntimeError):
    """Raised when search operations fail."""


@dataclass
class SearchResult:
    """Container for search outputs."""

    query: str
    query_embedding: list[float]
    distances: list[float] | None = None
    vector_ids: list[int] | None = None


class SearchService:
    """Coordinates query embedding generation and (optionally) vector lookup."""

    def __init__(
        self,
        embedding_client: EmbeddingClient,
        vector_manager: VectorDBManager,
        metadata_manager: MetadataDBManager,
        *,
        top_k: int = 10,
    ) -> None:
        self._embedding_client = embedding_client
        self._vector_manager = vector_manager
        self._metadata_manager = metadata_manager
        self._top_k = top_k

    def search(self, query: str, *, k: int | None = None) -> SearchResult:
        """Generate a query embedding and optionally search the local vector store."""

        normalized = query.strip()
        if not normalized:
            raise SearchServiceError("Search query cannot be empty.")

        try:
            query_embedding = self._embedding_client.get_embedding(normalized)
        except EmbeddingClientError as error:
            raise SearchServiceError(str(error)) from error

        distances: list[float] | None = None
        vector_ids: list[int] | None = None

        # Attempt vector search; if FAISS is unavailable or index empty, surface a clear error.
        try:
            distances, vector_ids = self._vector_manager.search(
                query_embedding, k or self._top_k
            )
        except Exception as error:  # pragma: no cover - dependent on FAISS availability
            logger.exception("Vector search failed.")
            raise SearchServiceError("Unable to search the vector index.") from error

        return SearchResult(
            query=normalized,
            query_embedding=query_embedding,
            distances=distances,
            vector_ids=vector_ids,
        )
