"""Tests for the IndexingScopeView widget."""

from __future__ import annotations

import pytest
pytest.importorskip("PySide6")

from PySide6.QtTest import QSignalSpy
from PySide6.QtWidgets import QApplication

from zoterorag.core.data.models import Collection
from zoterorag.ui.indexing_scope_view import IndexingScopeView


@pytest.fixture(scope="module")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app


def test_scope_emits_for_entire_library(qapp):
    view = IndexingScopeView()
    spy = QSignalSpy(view.scope_selected)
    view._start_button.click()
    assert spy.count() == 1
    signal_args = spy.at(0)
    assert signal_args[0]["type"] == "all"


def test_scope_emits_for_collection(qapp):
    view = IndexingScopeView()
    collections = [
        Collection(id=1, name="Papers", zotero_collection_key="AAA"),
        Collection(id=2, name="Books", zotero_collection_key="BBB", parent_id=1),
    ]
    view.set_collections(collections)
    view._collection_radio.setChecked(True)
    view._collection_combo.setCurrentIndex(1)

    spy = QSignalSpy(view.scope_selected)
    view._start_button.click()
    assert spy.count() == 1
    signal_args = spy.at(0)
    payload = signal_args[0]
    assert payload["type"] == "collection"
    assert payload["id"] == 2
    assert payload["key"] == "BBB"
