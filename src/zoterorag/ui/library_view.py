"""Table-based view that displays Zotero library items."""

from __future__ import annotations

from typing import Iterable

from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex
from PySide6.QtGui import QColor, QBrush
from PySide6.QtWidgets import QLabel, QTableView, QVBoxLayout, QWidget

from ..core.services.zotero_manager import ZoteroItem


class LibraryTableModel(QAbstractTableModel):
    """Model driving the QTableView used by the library view."""

    HEADERS = ["Title", "Authors", "Year", "Status"]
    STATUS_ORDER = ["PDF Error", "No PDF", "Not Indexed", "Indexed"]

    def __init__(self, items: Iterable[ZoteroItem] | None = None, statuses: dict[str, str] | None = None) -> None:
        super().__init__()
        self._items = list(items or [])
        self._statuses = statuses or {}
        self._key_to_row: dict[str, int] = {it.item_key: idx for idx, it in enumerate(self._items)}

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:  # type: ignore[override]
        return len(self._items)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:  # type: ignore[override]
        return len(self.HEADERS)

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole):
        if not index.isValid():
            return None
        item = self._items[index.row()]
        status_text = self._statuses.get(item.item_key, "Not Indexed")
        display_status = self._format_status(status_text)
        if role == Qt.DisplayRole:
            return [item.title, item.authors, item.year, display_status["text"]][index.column()]
        if role == Qt.ForegroundRole and index.column() == 3:
            return QBrush(display_status["color"])
        return None

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.DisplayRole):
        if role != Qt.DisplayRole or orientation != Qt.Horizontal:
            return None
        return self.HEADERS[section]

    def update_items(self, items: Iterable[ZoteroItem], statuses: dict[str, str] | None = None) -> None:
        self.beginResetModel()
        self._items = list(items)
        self._statuses = statuses or {}
        self._key_to_row = {it.item_key: idx for idx, it in enumerate(self._items)}
        self.endResetModel()

    def sort(self, column: int, order: Qt.SortOrder = Qt.AscendingOrder) -> None:  # type: ignore[override]
        reverse = order == Qt.DescendingOrder
        if column == 3:
            priority = {name: idx for idx, name in enumerate(self.STATUS_ORDER)}
            self._items.sort(
                key=lambda it: priority.get(self._statuses.get(it.item_key, "Not Indexed"), len(priority)),
                reverse=reverse,
            )
        elif column == 0:
            self._items.sort(key=lambda it: (it.title or "").lower(), reverse=reverse)
        elif column == 1:
            self._items.sort(key=lambda it: (it.authors or "").lower(), reverse=reverse)
        elif column == 2:
            self._items.sort(key=lambda it: it.year or 0, reverse=reverse)
        self.layoutChanged.emit()

    def _format_status(self, status: str) -> dict:
        mapping = {
            "Not Indexed": {"text": "⚪ Not Indexed", "color": QColor("#666666")},
            "Indexed": {"text": "✅ Indexed", "color": QColor("#2e7d32")},
            "No PDF": {"text": "⚠️ No PDF", "color": QColor("#b8860b")},
            "PDF Error": {"text": "❌ PDF Error", "color": QColor("#c62828")},
        }
        return mapping.get(status, mapping["Not Indexed"])

    def update_status(self, zotero_key: str, status: str) -> None:
        """Update a single item's status if present."""
        row = self._key_to_row.get(zotero_key)
        if row is None:
            return
        self._statuses[zotero_key] = status
        index = self.index(row, 3)
        self.dataChanged.emit(index, index, [Qt.DisplayRole, Qt.ForegroundRole])


class LibraryView(QWidget):
    """Widget responsible for rendering Zotero library data."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._status_label = QLabel("Library information unavailable.")
        self._table = QTableView()
        self._table_model = LibraryTableModel()
        self._table.setModel(self._table_model)
        self._table.horizontalHeader().setStretchLastSection(True)
        self._table.setSortingEnabled(True)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("<b>Your Zotero Library</b>"))
        layout.addWidget(self._status_label)
        layout.addWidget(self._table)

    def set_items(self, items: Iterable[ZoteroItem], statuses: dict[str, str] | None = None) -> None:
        items_list = list(items)
        self._table_model.update_items(items_list, statuses)
        count = len(items_list)
        self._status_label.setText(f"Loaded {count} items.")

    def show_error(self, message: str) -> None:
        self._table_model.update_items([])
        self._status_label.setText(message)
