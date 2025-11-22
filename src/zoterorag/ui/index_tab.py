"""Tab container for indexing controls and library view."""

from __future__ import annotations

from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from .indexing_scope_view import IndexingScopeView
from .library_view import LibraryView


class IndexTab(QWidget):
    """Encapsulates Zotero library display and indexing scope selection."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.library_view = LibraryView()
        self.indexing_scope_view = IndexingScopeView()

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Zotero Library"))
        layout.addWidget(self.library_view)
        layout.addWidget(self.indexing_scope_view)
        layout.addStretch()
