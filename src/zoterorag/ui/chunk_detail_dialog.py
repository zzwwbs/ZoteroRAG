"""Non-modal dialog for displaying chunk details with navigation."""

from __future__ import annotations

from typing import List

from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QKeyEvent, QDesktopServices
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from ..core.data.models import Chunk, Document
from ..core.services.search_service import SearchMatch


class ChunkDetailDialog(QDialog):
    """Displays full chunk text with navigation and actions."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowModality(Qt.NonModal)
        self.setWindowTitle("Chunk Details")
        self.resize(640, 480)

        self._matches: List[SearchMatch] = []
        self._current_index: int = 0

        self._title_label = QLabel("")
        self._meta_label = QLabel("")
        self._content = QTextEdit()
        self._content.setReadOnly(True)
        self._content.setAcceptRichText(False)
        self._content.setLineWrapMode(QTextEdit.WidgetWidth)

        self._prev_button = QPushButton("Previous")
        self._next_button = QPushButton("Next")
        self._copy_button = QPushButton("Copy Text")
        self._open_pdf_button = QPushButton("Open PDF")

        nav_row = QHBoxLayout()
        nav_row.addWidget(self._prev_button)
        nav_row.addWidget(self._next_button)
        nav_row.addStretch()
        nav_row.addWidget(self._copy_button)
        nav_row.addWidget(self._open_pdf_button)

        layout = QVBoxLayout(self)
        layout.addWidget(self._title_label)
        layout.addWidget(self._meta_label)
        layout.addWidget(self._content)
        layout.addLayout(nav_row)

        self._prev_button.clicked.connect(self._show_previous)
        self._next_button.clicked.connect(self._show_next)
        self._copy_button.clicked.connect(self._copy_text)
        self._open_pdf_button.clicked.connect(self._open_pdf)

    def show_chunk(self, match: SearchMatch, matches: List[SearchMatch]) -> None:
        """Populate dialog from the provided match and surrounding list."""

        self._matches = list(matches)
        try:
            self._current_index = self._matches.index(match)
        except ValueError:
            self._matches.insert(0, match)
            self._current_index = 0

        self._apply_current()

    def keyPressEvent(self, event: QKeyEvent) -> None:  # pragma: no cover - Qt dispatch
        if event.key() == Qt.Key_Left:
            self._show_previous()
            event.accept()
            return
        if event.key() == Qt.Key_Right:
            self._show_next()
            event.accept()
            return
        super().keyPressEvent(event)

    def _apply_current(self) -> None:
        if not self._matches or not (0 <= self._current_index < len(self._matches)):
            return

        current = self._matches[self._current_index]
        chunk: Chunk = current.chunk
        doc: Document | None = current.document
        title = doc.title if doc else "Unknown document"
        page = chunk.page_number
        score = current.distance if current.distance is not None else "n/a"

        self._title_label.setText(f"<b>{title}</b>")
        self._meta_label.setText(f"Page: {page} | Score: {score}")
        self._content.setPlainText(chunk.content)
        self._update_nav_buttons()

    def _update_nav_buttons(self) -> None:
        has_matches = bool(self._matches)
        self._prev_button.setEnabled(has_matches and len(self._matches) > 1)
        self._next_button.setEnabled(has_matches and len(self._matches) > 1)
        self._open_pdf_button.setEnabled(self._has_pdf())

    def _show_previous(self) -> None:
        if not self._matches:
            return
        self._current_index = (self._current_index - 1) % len(self._matches)
        self._apply_current()

    def _show_next(self) -> None:
        if not self._matches:
            return
        self._current_index = (self._current_index + 1) % len(self._matches)
        self._apply_current()

    def _copy_text(self) -> None:
        QApplication.clipboard().setText(self._content.toPlainText())

    def _open_pdf(self) -> None:
        doc = self._matches[self._current_index].document if self._matches else None
        if not doc or not doc.pdf_file_path:
            return
        QDesktopServices.openUrl(QUrl.fromLocalFile(doc.pdf_file_path))

    def _has_pdf(self) -> bool:
        doc = self._matches[self._current_index].document if self._matches else None
        return bool(doc and doc.pdf_file_path)
