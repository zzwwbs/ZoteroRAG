"""Tests for the ChunkDetailDialog UI component."""

from __future__ import annotations

import pytest

pytest.importorskip("PySide6")

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from zoterorag.core.data.models import Chunk, Document
from zoterorag.core.services.search_service import SearchMatch
from zoterorag.ui.chunk_detail_dialog import ChunkDetailDialog


@pytest.fixture(scope="module")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app


def _build_matches():
    doc = Document(zotero_item_key="k1", title="Doc 1", pdf_file_path="/tmp/doc1.pdf", id=1)
    doc2 = Document(zotero_item_key="k2", title="Doc 2", pdf_file_path="/tmp/doc2.pdf", id=2)
    match1 = SearchMatch(chunk=Chunk(document_id=1, content="First chunk text", page_number=1), document=doc, distance=0.1)
    match2 = SearchMatch(chunk=Chunk(document_id=2, content="Second chunk text", page_number=2), document=doc2, distance=0.2)
    return [match1, match2]


def test_dialog_displays_chunk_and_navigates(qapp, qtbot):
    dialog = ChunkDetailDialog()
    qtbot.addWidget(dialog)
    matches = _build_matches()

    dialog.show_chunk(matches[0], matches)
    assert "Doc 1" in dialog._title_label.text()
    assert "Page: 1" in dialog._meta_label.text()
    assert "First chunk text" in dialog._content.toPlainText()

    qtbot.mouseClick(dialog._next_button, Qt.LeftButton)
    assert "Doc 2" in dialog._title_label.text()
    assert "Page: 2" in dialog._meta_label.text()
    assert "Second chunk text" in dialog._content.toPlainText()

    qtbot.keyClick(dialog, Qt.Key_Left)
    assert "Doc 1" in dialog._title_label.text()


def test_copy_button_copies_content(qapp, qtbot):
    dialog = ChunkDetailDialog()
    qtbot.addWidget(dialog)
    matches = _build_matches()
    dialog.show_chunk(matches[1], matches)

    QApplication.clipboard().clear()
    qtbot.mouseClick(dialog._copy_button, Qt.LeftButton)
    assert QApplication.clipboard().text() == "Second chunk text"
