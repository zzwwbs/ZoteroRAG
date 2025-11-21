"""SQLite-backed repositories for documents and chunks."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime

from .models import Chunk, Document


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
