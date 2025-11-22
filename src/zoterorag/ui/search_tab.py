"""Tab container for search-related UI elements."""

from __future__ import annotations

from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QSpinBox, QVBoxLayout, QWidget

from .chunk_list_view import ChunkListView
from .chunk_detail_dialog import ChunkDetailDialog
from .paper_list_view import PaperListView
from .search_view import SearchView


class SearchTab(QWidget):
    """Encapsulates the search UI, results lists, and analyze controls."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.search_view = SearchView()
        self.paper_list_view = PaperListView()
        self.chunk_list_view = ChunkListView()
        self._chunk_detail_dialog: ChunkDetailDialog | None = None

        self.chunk_count = QSpinBox()
        self.chunk_count.setRange(1, 50)
        self.chunk_count.setValue(10)
        self.chunk_count.setEnabled(False)

        self.analyze_button = QPushButton("Analyze with AI")
        self.analyze_button.setEnabled(False)
        self.analyze_button.setProperty("busy", False)

        chunk_row = QHBoxLayout()
        chunk_row.addWidget(QLabel("Chunks:"))
        chunk_row.addWidget(self.chunk_count)

        layout = QVBoxLayout(self)
        layout.addWidget(self.search_view)
        layout.addWidget(self.paper_list_view)
        layout.addWidget(self.chunk_list_view)
        layout.addLayout(chunk_row)
        layout.addWidget(self.analyze_button)
        layout.addStretch()

        self.chunk_list_view.chunk_activated.connect(self._on_chunk_activated)

    def _on_chunk_activated(self, match, matches) -> None:
        """Show chunk detail dialog on double click."""

        if self._chunk_detail_dialog is None:
            self._chunk_detail_dialog = ChunkDetailDialog(self)
        self._chunk_detail_dialog.show_chunk(match, matches)
        self._chunk_detail_dialog.show()
        self._chunk_detail_dialog.raise_()
        self._chunk_detail_dialog.activateWindow()
