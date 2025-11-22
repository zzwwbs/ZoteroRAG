"""SQLite-backed repositories for documents and chunks."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime

from .models import Chunk, Document, TokenUsage


class DocumentRepository:
    """CRUD helpers for the documents table."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = connection

    def insert(self, document: Document) -> Document:
        authors_json = json.dumps(document.authors)
        indexed_at = document.indexed_at.isoformat()
        cursor = self._connection.execute(
            """
            INSERT INTO documents (zotero_item_key, title, authors, year, pdf_file_path, indexed_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                document.zotero_item_key,
                document.title,
                authors_json,
                document.year,
                document.pdf_file_path,
                indexed_at,
            ),
        )
        self._connection.commit()
        document.id = cursor.lastrowid
        return document

    def get_by_id(self, document_id: int) -> Document | None:
        row = self._connection.execute(
            "SELECT * FROM documents WHERE id = ?",
            (document_id,),
        ).fetchone()
        return self._row_to_document(row) if row else None

    def get_by_zotero_key(self, zotero_key: str) -> Document | None:
        row = self._connection.execute(
            "SELECT * FROM documents WHERE zotero_item_key = ?",
            (zotero_key,),
        ).fetchone()
        return self._row_to_document(row) if row else None

    def get_by_ids(self, document_ids: list[int]) -> list[Document]:
        """Return documents for the provided IDs."""

        if not document_ids:
            return []

        placeholders = ",".join("?" for _ in document_ids)
        rows = self._connection.execute(
            f"SELECT * FROM documents WHERE id IN ({placeholders})",
            tuple(document_ids),
        ).fetchall()
        return [self._row_to_document(row) for row in rows]

    def _row_to_document(self, row: sqlite3.Row) -> Document:
        authors = json.loads(row["authors"]) if row["authors"] else []
        indexed_at = datetime.fromisoformat(row["indexed_at"])
        return Document(
            id=row["id"],
            zotero_item_key=row["zotero_item_key"],
            title=row["title"],
            authors=authors,
            year=row["year"],
            pdf_file_path=row["pdf_file_path"],
            indexed_at=indexed_at,
        )


class ChunkRepository:
    """CRUD helpers for chunk rows."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = connection

    def insert(self, chunk: Chunk) -> Chunk:
        cursor = self._connection.execute(
            """
            INSERT INTO chunks (document_id, content, page_number, vector_id)
            VALUES (?, ?, ?, ?)
            """,
            (chunk.document_id, chunk.content, chunk.page_number, chunk.vector_id),
        )
        self._connection.commit()
        chunk.id = cursor.lastrowid
        return chunk

    def get_by_id(self, chunk_id: int) -> Chunk | None:
        row = self._connection.execute(
            "SELECT * FROM chunks WHERE id = ?",
            (chunk_id,),
        ).fetchone()
        if not row:
            return None

        return Chunk(
            id=row["id"],
            document_id=row["document_id"],
            content=row["content"],
            page_number=row["page_number"],
            vector_id=row["vector_id"],
        )

    def get_chunks_by_vector_ids(self, vector_ids: list[int]) -> list[Chunk]:
        """Return chunks matching the provided vector IDs."""

        if not vector_ids:
            return []

        placeholders = ",".join("?" for _ in vector_ids)
        rows = self._connection.execute(
            f"SELECT * FROM chunks WHERE vector_id IN ({placeholders})",
            tuple(vector_ids),
        ).fetchall()
        return [
            Chunk(
                id=row["id"],
                document_id=row["document_id"],
                content=row["content"],
                page_number=row["page_number"],
                vector_id=row["vector_id"],
            )
            for row in rows
        ]


class TokenUsageRepository:
    """CRUD helpers for tracking token usage."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = connection

    def insert(self, usage: TokenUsage) -> TokenUsage:
        cursor = self._connection.execute(
            """
            INSERT INTO token_usage (timestamp, operation, tokens_used, model)
            VALUES (?, ?, ?, ?)
            """,
            (
                usage.timestamp.isoformat(),
                usage.operation,
                usage.tokens_used,
                usage.model,
            ),
        )
        self._connection.commit()
        usage.id = cursor.lastrowid
        return usage

    def get_session_totals(self) -> dict:
        row = self._connection.execute(
            """
            SELECT
                COALESCE(SUM(tokens_used), 0) AS tokens,
                SUM(CASE WHEN operation = 'embedding' THEN 1 ELSE 0 END) AS embedding_calls,
                SUM(CASE WHEN operation = 'chat_completion' THEN 1 ELSE 0 END) AS analysis_calls
            FROM token_usage
            """
        ).fetchone()
        return {
            "tokens": int(row["tokens"] or 0),
            "embedding_calls": int(row["embedding_calls"] or 0),
            "analysis_calls": int(row["analysis_calls"] or 0),
        }
