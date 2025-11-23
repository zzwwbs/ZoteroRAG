"""Tab container for indexing controls and library view."""

from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from .indexing_scope_view import IndexingScopeView
from .library_view import LibraryView


class IndexTab(QWidget):
    """Encapsulates Zotero library display and indexing scope selection."""

    start_indexing = Signal(dict)
    cancel_indexing = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.library_view = LibraryView()
        self.indexing_scope_view = IndexingScopeView()
        self.indexing_scope_view.scope_selected.connect(self._emit_start_indexing)
        self.indexing_scope_view.cancel_requested.connect(self.cancel_indexing.emit)

        self.summary_label = QLabel("")
        self.summary_label.setVisible(False)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Zotero Library"))
        layout.addWidget(self.library_view)
        layout.addWidget(self.indexing_scope_view)
        layout.addWidget(self.summary_label)
        layout.addStretch()

    def _emit_start_indexing(self, scope: dict) -> None:
        self.indexing_scope_view.set_cancel_mode()
        self.start_indexing.emit(scope)

    def show_indexing_active(self) -> None:
        self.indexing_scope_view.set_cancel_mode()

    def show_cancelling(self) -> None:
        self.indexing_scope_view.set_cancelling_mode()

    def show_idle(self) -> None:
        self.indexing_scope_view.set_idle_mode()

    def update_summary(self, summary_text: str) -> None:
        self.summary_label.setText(summary_text)
        self.summary_label.setVisible(bool(summary_text))
