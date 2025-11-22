"""Tab container for search-related UI elements."""

from __future__ import annotations

from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QSpinBox, QVBoxLayout, QWidget

from .chunk_list_view import ChunkListView
from .paper_list_view import PaperListView
from .search_view import SearchView


class SearchTab(QWidget):
    """Encapsulates the search UI, results lists, and analyze controls."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.search_view = SearchView()
        self.paper_list_view = PaperListView()
        self.chunk_list_view = ChunkListView()

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
