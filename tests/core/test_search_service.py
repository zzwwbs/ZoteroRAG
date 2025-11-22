"""Unit tests for SearchService vector retrieval."""

from __future__ import annotations

import sqlite3
from datetime import datetime

import pytest

from zoterorag.core.data.models import Chunk, Document, TokenUsage
from zoterorag.core.data.repositories import ChunkRepository, DocumentRepository
from zoterorag.core.services.metadata_db_manager import SCHEMA_SQL
from zoterorag.core.services.search_service import SearchService, SearchServiceError


class FakeEmbeddingClient:
    def __init__(self, embedding: list[float]) -> None:
        self._embedding = embedding

    def get_embedding(self, text: str) -> tuple[list[float], TokenUsage]:
        return self._embedding, TokenUsage(
            operation="embedding",
            tokens_used=5,
            model="text-embedding-ada-002",
        )


class FakeVectorManager:
    def __init__(self, distances, ids):
        self._distances = distances
        self._ids = ids

    def search(self, query_vector, k):
        return self._distances, self._ids


class StubMetadataManager:
    def __init__(self, doc_repo: DocumentRepository, chunk_repo: ChunkRepository) -> None:
        self.document_repository = doc_repo
        self.chunk_repository = chunk_repo
        self.token_usage_repository = _DummyUsageRepo()


class _DummyUsageRepo:
    def __init__(self) -> None:
        self.inserted: list[TokenUsage] = []

    def insert(self, usage: TokenUsage) -> TokenUsage:
        self.inserted.append(usage)
        return usage


def _setup_repos():
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript(SCHEMA_SQL)

    doc_repo = DocumentRepository(conn)
    chunk_repo = ChunkRepository(conn)

    doc = doc_repo.insert(
        Document(
            zotero_item_key="abc",
            title="Doc1",
            authors=["Author"],
            year=2021,
            pdf_file_path="/tmp/doc.pdf",
            indexed_at=datetime.utcnow(),
        )
    )
    chunk = chunk_repo.insert(
        Chunk(
            document_id=doc.id or -1,
            content="chunk content",
            page_number=1,
            vector_id=5,
        )
    )
    return doc_repo, chunk_repo, doc, chunk


def test_search_service_builds_matches():
    doc_repo, chunk_repo, doc, chunk = _setup_repos()
    service = SearchService(
        embedding_client=FakeEmbeddingClient([0.1, 0.2]),
        vector_manager=FakeVectorManager([0.01], [5]),
        metadata_manager=StubMetadataManager(doc_repo, chunk_repo),
    )

    result = service.search("query")

    assert result.vector_ids == [5]
    assert result.matches is not None
    assert len(result.matches) == 1
    match = result.matches[0]
    assert match.chunk.id == chunk.id
    assert match.document.id == doc.id
    assert match.distance == 0.01


def test_search_service_rejects_empty_query():
    doc_repo, chunk_repo, *_ = _setup_repos()
    service = SearchService(
        embedding_client=FakeEmbeddingClient([0.1]),
        vector_manager=FakeVectorManager([], []),
        metadata_manager=StubMetadataManager(doc_repo, chunk_repo),
    )

    with pytest.raises(SearchServiceError):
        service.search("   ")
