"""List view for chunks with optional PDF opening support."""

from __future__ import annotations

from typing import Iterable, Optional, List

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QListWidget, QListWidgetItem, QPushButton, QVBoxLayout, QWidget

from ..core.data.models import Document
from ..core.services.search_service import SearchMatch


class ChunkListView(QWidget):
    """Displays search result chunks and allows opening their PDFs."""

    open_pdf_requested = Signal(object)  # Document
    chunk_activated = Signal(object, list)  # SearchMatch, list[SearchMatch]

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._list = QListWidget()
        self._open_pdf_button = QPushButton("Open PDF for Selected Chunk")
        self._matches: List[SearchMatch] = []

        layout = QVBoxLayout(self)
        layout.addWidget(self._list)
        layout.addWidget(self._open_pdf_button)

        self._open_pdf_button.clicked.connect(self._handle_open_pdf)
        self._list.itemDoubleClicked.connect(self._handle_item_double_clicked)

    def update_chunks(
        self,
        matches: Iterable[SearchMatch],
        selected_document_id: Optional[int] = None,
    ) -> None:
        """Refresh chunk list based on matches and optional document filter."""
        self._list.clear()
        self._matches = []
        for match in matches:
            doc = match.document
            if selected_document_id is not None and (not doc or doc.id != selected_document_id):
                continue

            preview = match.chunk.content[:120].replace("\n", " ")
            title = doc.title if doc else "Unknown document"
            item_text = f"{title}: {preview}"

            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, (match.chunk, doc))
            self._list.addItem(item)
            self._matches.append(match)

    def _handle_open_pdf(self) -> None:
        item = self._list.currentItem()
        if not item:
            return
        payload = item.data(Qt.UserRole)
        if not payload:
            return
        _, doc = payload
        if isinstance(doc, Document) and doc.pdf_file_path:
            self.open_pdf_requested.emit(doc)

    def _handle_item_double_clicked(self, item: QListWidgetItem) -> None:
        index = self._list.row(item)
        if 0 <= index < len(self._matches):
            self.chunk_activated.emit(self._matches[index], self._matches)
