"""Tab container for search-related UI elements."""

from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QVBoxLayout, QWidget

from .chunk_list_view import ChunkListView
from .chunk_detail_dialog import ChunkDetailDialog
from .paper_list_view import PaperListView
from .search_view import SearchView


class SearchTab(QWidget):
    """Encapsulates the search UI, results lists, and analyze controls."""

    selection_changed = Signal(bool)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.search_view = SearchView()
        self.paper_list_view = PaperListView()
        self.chunk_list_view = ChunkListView()
        self._chunk_detail_dialog: ChunkDetailDialog | None = None

        self.chunk_count = self.search_view.result_count

        layout = QVBoxLayout(self)
        layout.addWidget(self.search_view)
        layout.addWidget(self.paper_list_view)
        layout.addWidget(self.chunk_list_view)
        layout.addStretch()

        self.chunk_list_view.chunk_activated.connect(self._on_chunk_activated)
        self.paper_list_view.paper_selected.connect(self._emit_selection_present)
        self.paper_list_view.clear_filter_requested.connect(self._emit_selection_absent)

    def _emit_selection_present(self, *_args) -> None:
        self.selection_changed.emit(True)

    def _emit_selection_absent(self) -> None:
        self.selection_changed.emit(False)

    def _on_chunk_activated(self, match, matches) -> None:
        """Show chunk detail dialog on double click."""

        if self._chunk_detail_dialog is None:
            self._chunk_detail_dialog = ChunkDetailDialog(self)
        self._chunk_detail_dialog.show_chunk(match, matches)
        self._chunk_detail_dialog.show()
        self._chunk_detail_dialog.raise_()
        self._chunk_detail_dialog.activateWindow()
