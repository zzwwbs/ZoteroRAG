"""Table-based view that displays Zotero library items."""

from __future__ import annotations

from typing import Iterable

from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex
from PySide6.QtWidgets import QLabel, QTableView, QVBoxLayout, QWidget

from ..core.services.zotero_manager import ZoteroItem


class LibraryTableModel(QAbstractTableModel):
    """Model driving the QTableView used by the library view."""

    HEADERS = ["Title", "Authors", "Year"]

    def __init__(self, items: Iterable[ZoteroItem] | None = None) -> None:
        super().__init__()
        self._items = list(items or [])

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:  # type: ignore[override]
        return len(self._items)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:  # type: ignore[override]
        return len(self.HEADERS)

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole):
        if not index.isValid() or role != Qt.DisplayRole:
            return None
        item = self._items[index.row()]
        return [item.title, item.authors, item.year][index.column()]

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.DisplayRole):
        if role != Qt.DisplayRole or orientation != Qt.Horizontal:
            return None
        return self.HEADERS[section]

    def update_items(self, items: Iterable[ZoteroItem]) -> None:
        self.beginResetModel()
        self._items = list(items)
        self.endResetModel()


class LibraryView(QWidget):
    """Widget responsible for rendering Zotero library data."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._status_label = QLabel("Library information unavailable.")
        self._table = QTableView()
        self._table_model = LibraryTableModel()
        self._table.setModel(self._table_model)
        self._table.horizontalHeader().setStretchLastSection(True)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("<b>Your Zotero Library</b>"))
        layout.addWidget(self._status_label)
        layout.addWidget(self._table)

    def set_items(self, items: Iterable[ZoteroItem]) -> None:
        items_list = list(items)
        self._table_model.update_items(items_list)
        count = len(items_list)
        self._status_label.setText(f"Loaded {count} items.")

    def show_error(self, message: str) -> None:
        self._table_model.update_items([])
        self._status_label.setText(message)
