"""Dataclasses representing metadata persisted in SQLite."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import List


@dataclass
class Document:
    """Represents a Zotero document we have indexed."""

    zotero_item_key: str
    title: str
    authors: List[str] = field(default_factory=list)
    year: int | None = None
    pdf_file_path: str = ""
    indexed_at: datetime = field(default_factory=datetime.utcnow)
    id: int | None = None


@dataclass
class Chunk:
    """Represents a chunk of text extracted from a document."""

    document_id: int
    content: str
    page_number: int
    vector_id: int
    id: int | None = None
