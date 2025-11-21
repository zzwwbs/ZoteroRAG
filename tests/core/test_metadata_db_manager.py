"""Tests for metadata storage management."""

import sqlite3
from datetime import datetime
from pathlib import Path

from zoterorag.core.data.models import Chunk, Document
from zoterorag.core.services.metadata_db_manager import MetadataDBManager


def test_initialize_database_creates_tables(tmp_path: Path) -> None:
    manager = MetadataDBManager(data_dir=tmp_path)
    manager.initialize_database()

    assert manager.database_path.exists()
    with sqlite3.connect(manager.database_path) as connection:
        tables = connection.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name IN ('documents', 'chunks')"
        ).fetchall()
    assert set(row[0] for row in tables) == {"documents", "chunks"}


def test_insert_document_and_chunk_round_trip(tmp_path: Path) -> None:
    manager = MetadataDBManager(data_dir=tmp_path)
    manager.initialize_database()

    doc = Document(
        zotero_item_key="ABC123",
        title="Sample",
        authors=["Jane Doe"],
        year=2023,
        pdf_file_path="/tmp/sample.pdf",
        indexed_at=datetime.utcnow(),
    )
    saved_doc = manager.document_repository.insert(doc)
    fetched_doc = manager.document_repository.get_by_id(saved_doc.id)
    assert fetched_doc is not None
    assert fetched_doc.title == "Sample"
    assert fetched_doc.authors == ["Jane Doe"]

    chunk = Chunk(
        document_id=saved_doc.id,
        content="Chunk text",
        page_number=1,
        vector_id=42,
    )
    saved_chunk = manager.chunk_repository.insert(chunk)
    fetched_chunk = manager.chunk_repository.get_by_id(saved_chunk.id)
    assert fetched_chunk is not None
    assert fetched_chunk.content == "Chunk text"

    fetched_by_key = manager.get_document_by_key("ABC123")
    assert fetched_by_key is not None
    assert fetched_by_key.id == saved_doc.id

    next_vector_id = manager.get_next_vector_id()
    assert next_vector_id >= 43  # 42 in use above
