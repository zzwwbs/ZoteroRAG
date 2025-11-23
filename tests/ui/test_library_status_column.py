"""Tests for library view status column rendering."""

from __future__ import annotations

import pytest

pytest.importorskip("PySide6")

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

from zoterorag.ui.library_view import LibraryTableModel
from zoterorag.core.services.zotero_manager import ZoteroItem


@pytest.fixture(scope="module")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app


def _item(key: str, title: str, authors: str, year: int) -> ZoteroItem:
    return ZoteroItem(
        item_id=1,
        item_key=key,
        title=title,
        authors=authors,
        year=str(year)
    )


def test_status_column_display(qapp):
    items = [_item("a", "Doc", "Auth", 2020)]
    statuses = {"a": "Indexed"}
    model = LibraryTableModel(items, statuses)

    index = model.index(0, 3)
    assert model.data(index, Qt.DisplayRole).startswith("✅")
    assert model.columnCount() == 4
    assert model.headerData(3, Qt.Horizontal, Qt.DisplayRole) == "Status"
