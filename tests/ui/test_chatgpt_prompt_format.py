"""Tests for ChatGPT prompt formatting."""

from __future__ import annotations

from datetime import datetime

import pytest

pytest.importorskip("PySide6")

from zoterorag.core.data.models import Chunk, Document
from zoterorag.core.services.search_service import SearchMatch
from zoterorag.ui.main_window import format_chatgpt_prompt


def _match(doc_id: int, content: str) -> SearchMatch:
    doc = Document(
        id=doc_id,
        zotero_item_key=f"key-{doc_id}",
        title=f"Doc {doc_id}",
        authors=["Author"],
        year=2023,
        pdf_file_path="/tmp/doc.pdf",
        indexed_at=datetime.utcnow(),
    )
    chunk = Chunk(
        id=doc_id,
        document_id=doc_id,
        content=content,
        page_number=2,
        vector_id=doc_id,
    )
    return SearchMatch(chunk=chunk, document=doc, distance=0.1)


def test_prompt_limits_chunks_and_formats():
    matches = [
        _match(1, "first chunk"),
        _match(2, "second chunk"),
        _match(3, "third chunk"),
    ]
    prompt = format_chatgpt_prompt("query text", matches, limit=2)
    assert "query text" in prompt
    assert "1." in prompt and "2." in prompt
    assert "three" not in prompt.lower()


def test_prompt_filters_by_document():
    matches = [_match(1, "first chunk"), _match(2, "second chunk")]
    prompt = format_chatgpt_prompt("filter", matches, limit=10, selected_document_id=2)
    assert "Doc 1" not in prompt
    assert "Doc 2" in prompt
