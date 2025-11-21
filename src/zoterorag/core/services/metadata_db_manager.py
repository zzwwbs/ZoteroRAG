"""Manage the lifecycle of the metadata SQLite database."""

from __future__ import annotations

import sqlite3
from pathlib import Path

from ..data.repositories import ChunkRepository, DocumentRepository

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    zotero_item_key TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL,
    authors TEXT,
    year INTEGER,
    pdf_file_path TEXT NOT NULL,
    indexed_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_documents_zotero_item_key ON documents (zotero_item_key);

CREATE TABLE IF NOT EXISTS chunks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id INTEGER NOT NULL,
    content TEXT NOT NULL,
    page_number INTEGER NOT NULL,
    vector_id INTEGER NOT NULL UNIQUE,
    FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_chunks_document_id ON chunks (document_id);
CREATE INDEX IF NOT EXISTS idx_chunks_vector_id ON chunks (vector_id);
"""


class MetadataDBManager:
    """Initializes and provides access to the metadata database."""

    def __init__(self, data_dir: Path | None = None, db_filename: str = "zoterorag.db") -> None:
        self._data_dir = (data_dir or Path.home() / ".zotero_rag").expanduser()
        self._data_dir.mkdir(parents=True, exist_ok=True)
        self._db_path = self._data_dir / db_filename
        self._connection: sqlite3.Connection | None = None
        self._document_repo: DocumentRepository | None = None
        self._chunk_repo: ChunkRepository | None = None

    @property
    def database_path(self) -> Path:
        return self._db_path

    def initialize_database(self) -> None:
        connection = self._connect()
        connection.executescript(SCHEMA_SQL)
        connection.commit()

    def _connect(self) -> sqlite3.Connection:
        if self._connection is None:
            self._connection = sqlite3.connect(self._db_path)
            self._connection.row_factory = sqlite3.Row
            self._connection.execute("PRAGMA foreign_keys = ON")
        return self._connection

    def close(self) -> None:
        if self._connection:
            self._connection.close()
            self._connection = None
            self._document_repo = None
            self._chunk_repo = None

    @property
    def document_repository(self) -> DocumentRepository:
        if self._document_repo is None:
            self._document_repo = DocumentRepository(self._connect())
        return self._document_repo

    @property
    def chunk_repository(self) -> ChunkRepository:
        if self._chunk_repo is None:
            self._chunk_repo = ChunkRepository(self._connect())
        return self._chunk_repo
