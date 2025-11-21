"""List view for papers with selection and PDF open actions."""

from __future__ import annotations

from typing import Iterable

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QPushButton,
    QListWidget,
    QListWidgetItem,
    QVBoxLayout,
    QWidget,
)

from ..core.data.models import Document


class PaperListView(QWidget):
    """Displays papers and emits selection / open events."""

    paper_selected = Signal(object)  # Document
    clear_filter_requested = Signal()
    open_pdf_requested = Signal(object)  # Document

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._list = QListWidget()
        self._clear_button = QPushButton("Clear Filter")
        self._open_pdf_button = QPushButton("Open PDF")

        layout = QVBoxLayout(self)
        layout.addWidget(self._list)
        layout.addWidget(self._clear_button)
        layout.addWidget(self._open_pdf_button)

        self._list.itemClicked.connect(self._handle_item_clicked)
        self._clear_button.clicked.connect(self._handle_clear)
        self._open_pdf_button.clicked.connect(self._handle_open_pdf)

    def set_papers(self, papers: Iterable[Document]) -> None:
        """Populate list with the provided documents."""
        self._list.clear()
        for doc in papers:
            item = QListWidgetItem(f"{doc.title} ({doc.year or 'n/a'})")
            item.setData(Qt.UserRole, doc)
            self._list.addItem(item)

    def _handle_item_clicked(self, item: QListWidgetItem) -> None:
        doc = item.data(Qt.UserRole)
        if isinstance(doc, Document):
            self.paper_selected.emit(doc)

    def _handle_clear(self) -> None:
        self._list.clearSelection()
        self.clear_filter_requested.emit()

    def _handle_open_pdf(self) -> None:
        item = self._list.currentItem()
        if not item:
            return
        doc = item.data(Qt.UserRole)
        if isinstance(doc, Document):
            self.open_pdf_requested.emit(doc)
