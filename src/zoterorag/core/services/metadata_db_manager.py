"""Manage the lifecycle of the metadata SQLite database."""

from __future__ import annotations

import sqlite3
import threading
from pathlib import Path

from ..data.repositories import ChunkRepository, DocumentRepository, TokenUsageRepository

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    zotero_item_key TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL,
    authors TEXT,
    year INTEGER,
    pdf_file_path TEXT NOT NULL,
    indexed_at TEXT NOT NULL,
    indexing_status TEXT DEFAULT 'Not Indexed'
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

CREATE TABLE IF NOT EXISTS token_usage (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    operation TEXT NOT NULL,
    tokens_used INTEGER NOT NULL,
    model TEXT NOT NULL,
    prompt_tokens INTEGER DEFAULT 0,
    completion_tokens INTEGER DEFAULT 0
);
"""


class MetadataDBManager:
    """Initializes and provides access to the metadata database with thread-safe connections."""

    def __init__(self, data_dir: Path | None = None, db_filename: str = "zoterorag.db") -> None:
        self._data_dir = (data_dir or Path.home() / ".zotero_rag").expanduser()
        self._data_dir.mkdir(parents=True, exist_ok=True)
        self._db_path = self._data_dir / db_filename
        self._local = threading.local()  # Thread-local storage for connections and repositories

    @property
    def database_path(self) -> Path:
        return self._db_path

    def initialize_database(self) -> None:
        connection = self._get_connection()
        connection.executescript(SCHEMA_SQL)
        connection.commit()
        self._ensure_additional_columns(connection)

    def _ensure_additional_columns(self, connection: sqlite3.Connection) -> None:
        """Add missing columns for existing installs."""

        # Check if token_usage table exists first
        table_exists = connection.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='token_usage'"
        ).fetchone()
        
        if not table_exists:
            return  # Table doesn't exist yet, skip migration

        columns = {
            row["name"]: True
            for row in connection.execute("PRAGMA table_info(token_usage)").fetchall()
        }
        if "prompt_tokens" not in columns:
            connection.execute("ALTER TABLE token_usage ADD COLUMN prompt_tokens INTEGER DEFAULT 0")
        if "completion_tokens" not in columns:
            connection.execute("ALTER TABLE token_usage ADD COLUMN completion_tokens INTEGER DEFAULT 0")
        # Documents indexing_status
        doc_columns = {
            row["name"]: True
            for row in connection.execute("PRAGMA table_info(documents)").fetchall()
        }
        if "indexing_status" not in doc_columns:
            connection.execute(
                "ALTER TABLE documents ADD COLUMN indexing_status TEXT DEFAULT 'Not Indexed'"
            )
        connection.commit()

    def _get_connection(self) -> sqlite3.Connection:
        """Get or create a connection for the current thread."""
        if not hasattr(self._local, "connection") or self._local.connection is None:
            self._local.connection = sqlite3.connect(self._db_path)
            self._local.connection.row_factory = sqlite3.Row
            self._local.connection.execute("PRAGMA foreign_keys = ON")
            # Ensure latest schema for new thread connections
            self._ensure_additional_columns(self._local.connection)
        return self._local.connection

    def close(self) -> None:
        """Close the connection for the current thread."""
        if hasattr(self._local, "connection") and self._local.connection:
            self._local.connection.close()
            self._local.connection = None
            self._local.document_repo = None
            self._local.chunk_repo = None
            self._local.token_usage_repo = None

    @property
    def document_repository(self) -> DocumentRepository:
        """Get or create a DocumentRepository for the current thread."""
        if not hasattr(self._local, "document_repo") or self._local.document_repo is None:
            self._local.document_repo = DocumentRepository(self._get_connection())
        return self._local.document_repo

    @property
    def chunk_repository(self) -> ChunkRepository:
        """Get or create a ChunkRepository for the current thread."""
        if not hasattr(self._local, "chunk_repo") or self._local.chunk_repo is None:
            self._local.chunk_repo = ChunkRepository(self._get_connection())
        return self._local.chunk_repo

    @property
    def token_usage_repository(self) -> TokenUsageRepository:
        """Get or create a TokenUsageRepository for the current thread."""
        if not hasattr(self._local, "token_usage_repo") or self._local.token_usage_repo is None:
            self._local.token_usage_repo = TokenUsageRepository(self._get_connection())
        return self._local.token_usage_repo

    def get_document_by_key(self, zotero_key: str) -> Document | None:
        return self.document_repository.get_by_zotero_key(zotero_key)

    def get_next_vector_id(self) -> int:
        row = self._get_connection().execute("SELECT IFNULL(MAX(vector_id), 0) AS max_id FROM chunks").fetchone()
        current_max = row["max_id"] if row and row["max_id"] is not None else 0
        return int(current_max) + 1

    def has_documents(self) -> bool:
        """Return True if at least one document is already indexed."""

        row = self._get_connection().execute("SELECT 1 FROM documents LIMIT 1").fetchone()
        return row is not None
