"""Tests for repository lookups used in search."""

from __future__ import annotations

import sqlite3
from datetime import datetime

from zoterorag.core.data.models import Chunk, Document
from zoterorag.core.data.repositories import ChunkRepository, DocumentRepository
from zoterorag.core.services.metadata_db_manager import SCHEMA_SQL


def _setup_connection() -> sqlite3.Connection:
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    connection.executescript(SCHEMA_SQL)
    return connection


def test_document_repository_get_by_ids_returns_matches():
    conn = _setup_connection()
    docs_repo = DocumentRepository(conn)
    inserted = docs_repo.insert(
        Document(
            zotero_item_key="abc",
            title="Title",
            authors=["A"],
            year=2020,
            pdf_file_path="/tmp/file.pdf",
            indexed_at=datetime.utcnow(),
        )
    )
    results = docs_repo.get_by_ids([inserted.id or -1])
    assert len(results) == 1
    assert results[0].zotero_item_key == "abc"


def test_chunk_repository_get_chunks_by_vector_ids_returns_matches():
    conn = _setup_connection()
    docs_repo = DocumentRepository(conn)
    chunks_repo = ChunkRepository(conn)
    doc = docs_repo.insert(
        Document(
            zotero_item_key="abc",
            title="Title",
            authors=["A"],
            year=2020,
            pdf_file_path="/tmp/file.pdf",
            indexed_at=datetime.utcnow(),
        )
    )
    chunk = chunks_repo.insert(
        Chunk(
            document_id=doc.id or -1,
            content="chunk content",
            page_number=1,
            vector_id=42,
        )
    )

    results = chunks_repo.get_chunks_by_vector_ids([42])
    assert len(results) == 1
    assert results[0].id == chunk.id
    assert results[0].vector_id == 42
