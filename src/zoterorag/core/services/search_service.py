"""Service responsible for executing semantic search requests."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING, Sequence

if TYPE_CHECKING:
    from ..data.models import Chunk, Document, TokenUsage

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
    matches: list["SearchMatch"] | None = None
    token_usage: "TokenUsage | None" = None


@dataclass
class SearchMatch:
    """Represents a chunk result with associated document info."""

    chunk: "Chunk"
    document: "Document | None"
    distance: float | None = None


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
            query_embedding, usage = self._embedding_client.get_embedding(normalized)
            if usage.tokens_used > 0:
                self._metadata_manager.token_usage_repository.insert(usage)
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

        matches = self._build_matches(vector_ids or [], distances or [])

        return SearchResult(
            query=normalized,
            query_embedding=query_embedding,
            distances=distances,
            vector_ids=vector_ids,
            matches=matches,
            token_usage=usage if "usage" in locals() else None,
        )

    def _build_matches(
        self, vector_ids: Sequence[int], distances: Sequence[float]
    ) -> list["SearchMatch"]:
        """Hydrate chunk and document info for returned vector IDs."""

        if not vector_ids:
            return []

        chunk_repo = self._metadata_manager.chunk_repository
        document_repo = self._metadata_manager.document_repository

        chunks = chunk_repo.get_chunks_by_vector_ids(list(vector_ids))
        chunks_by_vector = {chunk.vector_id: chunk for chunk in chunks}
        doc_ids = {chunk.document_id for chunk in chunks}
        documents = document_repo.get_by_ids(list(doc_ids))
        docs_by_id = {doc.id: doc for doc in documents if doc.id is not None}

        matches: list[SearchMatch] = []
        for idx, vector_id in enumerate(vector_ids):
            chunk = chunks_by_vector.get(vector_id)
            if not chunk:
                continue

            distance = distances[idx] if idx < len(distances) else None
            matches.append(
                SearchMatch(
                    chunk=chunk,
                    document=docs_by_id.get(chunk.document_id),
                    distance=distance,
                )
            )

        return matches
