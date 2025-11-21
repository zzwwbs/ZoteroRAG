"""Tests for PaperListView interactions."""

from __future__ import annotations

from datetime import datetime

import pytest

pytest.importorskip("PySide6")

from PySide6.QtTest import QSignalSpy, QTest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from zoterorag.core.data.models import Document
from zoterorag.ui.paper_list_view import PaperListView


@pytest.fixture(scope="module")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app


def _sample_doc(doc_id: int) -> Document:
    return Document(
        id=doc_id,
        zotero_item_key=f"key-{doc_id}",
        title=f"Doc {doc_id}",
        authors=["Author"],
        year=2024,
        pdf_file_path=f"/tmp/doc{doc_id}.pdf",
        indexed_at=datetime.utcnow(),
    )


def test_emits_paper_selected_on_click(qapp):
    view = PaperListView()
    doc = _sample_doc(1)
    view.set_papers([doc])

    spy = QSignalSpy(view.paper_selected)
    view._list.setCurrentRow(0)
    item = view._list.currentItem()
    # Trigger the itemClicked signal directly since mouse click doesn't always work in tests
    view._list.itemClicked.emit(item)

    assert spy.count() == 1
    assert isinstance(spy.at(0)[0], Document)


def test_clear_filter_signal(qapp):
    view = PaperListView()
    spy = QSignalSpy(view.clear_filter_requested)
    QTest.mouseClick(view._clear_button, Qt.LeftButton)
    assert spy.count() == 1


def test_open_pdf_signal(qapp):
    view = PaperListView()
    doc = _sample_doc(2)
    view.set_papers([doc])
    view._list.setCurrentRow(0)

    spy = QSignalSpy(view.open_pdf_requested)
    QTest.mouseClick(view._open_pdf_button, Qt.LeftButton)
    assert spy.count() == 1
    assert isinstance(spy.at(0)[0], Document)
