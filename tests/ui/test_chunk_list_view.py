"""Tests for ChunkListView filtering and PDF emission."""

from __future__ import annotations

from datetime import datetime

import pytest

pytest.importorskip("PySide6")

from PySide6.QtTest import QSignalSpy, QTest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from zoterorag.core.data.models import Chunk, Document
from zoterorag.core.services.search_service import SearchMatch
from zoterorag.ui.chunk_list_view import ChunkListView


@pytest.fixture(scope="module")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app


def _make_match(doc_id: int, vector_id: int) -> SearchMatch:
    doc = Document(
        id=doc_id,
        zotero_item_key=f"key-{doc_id}",
        title=f"Doc {doc_id}",
        authors=["A"],
        year=2024,
        pdf_file_path=f"/tmp/doc{doc_id}.pdf",
        indexed_at=datetime.utcnow(),
    )
    chunk = Chunk(
        id=vector_id,
        document_id=doc_id,
        content="lorem ipsum dolor sit amet",
        page_number=1,
        vector_id=vector_id,
    )
    return SearchMatch(chunk=chunk, document=doc, distance=0.1)


def test_filters_by_selected_document(qapp):
    view = ChunkListView()
    matches = [_make_match(1, 1), _make_match(2, 2)]

    view.update_chunks(matches, selected_document_id=1)
    assert view._list.count() == 1
    assert "Doc 1" in view._list.item(0).text()


def test_emits_open_pdf(qapp):
    view = ChunkListView()
    matches = [_make_match(3, 3)]
    view.update_chunks(matches)
    view._list.setCurrentRow(0)

    spy = QSignalSpy(view.open_pdf_requested)
    QTest.mouseClick(view._open_pdf_button, Qt.LeftButton)
    assert spy.count() == 1
