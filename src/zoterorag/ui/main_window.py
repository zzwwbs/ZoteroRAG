"""Main window implementation for the Zotero RAG desktop application."""

from __future__ import annotations

from pathlib import Path
import os
import subprocess
import sys
import logging

from PySide6.QtCore import QObject, QRunnable, QThreadPool, Signal
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QMessageBox, QMainWindow, QStackedWidget, QVBoxLayout, QWidget

from ..config.settings_manager import SettingsManager
from ..core.services.embedding_client import EmbeddingClient
from ..core.services.indexing_service import IndexingService
from ..core.services.metadata_db_manager import MetadataDBManager
from ..core.services.search_service import (
    SearchMatch,
    SearchResult,
    SearchService,
    SearchServiceError,
)
from ..core.services.vector_db_manager import VectorDBManager
from ..core.services.zotero_manager import (
    ZoteroDatabaseError,
    ZoteroManager,
)
from .chunk_list_view import ChunkListView
from .indexing_scope_view import IndexingScopeView
from .library_view import LibraryView
from .onboarding_view import OnboardingView
from .paper_list_view import PaperListView
from .search_view import SearchView
from .state import AppState

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """Primary shell window with setup detection and onboarding."""

    def __init__(
        self,
        settings_manager: SettingsManager | None = None,
        zotero_manager: ZoteroManager | None = None,
        search_service: SearchService | None = None,
        thread_pool: QThreadPool | None = None,
        auto_start: bool = True,
    ) -> None:
        super().__init__()
        self.setWindowTitle("Zotero RAG")
        self.resize(1024, 768)

        self._settings_manager = settings_manager or SettingsManager()
        self._zotero_manager = zotero_manager or ZoteroManager()
        self._thread_pool = thread_pool or QThreadPool.globalInstance()
        self._metadata_manager = MetadataDBManager()
        self._vector_manager = VectorDBManager(dimension=1536)
        self._embedding_client = EmbeddingClient(self._settings_manager)
        self._search_service = search_service or SearchService(
            self._embedding_client,
            self._vector_manager,
            self._metadata_manager,
        )
        self._indexing_service = IndexingService(
            self._zotero_manager,
            metadata_manager=self._metadata_manager,
            vector_manager=self._vector_manager,
            embedding_client=self._embedding_client,
        )
        self._state = AppState()

        self._stack = QStackedWidget()
        self.setCentralWidget(self._stack)

        self._onboarding_view = OnboardingView(self._zotero_manager)
        self._onboarding_view.path_confirmed.connect(self._handle_path_selected)

        self._search_view = SearchView()
        self._search_view.search_triggered.connect(self._on_search)

        self._library_view = LibraryView()
        self._indexing_scope_view = IndexingScopeView()
        self._indexing_scope_view.scope_selected.connect(self._start_indexing_task)
        self._paper_list_view = PaperListView()
        self._paper_list_view.paper_selected.connect(self._on_paper_selected)
        self._paper_list_view.clear_filter_requested.connect(self._clear_selection)
        self._paper_list_view.open_pdf_requested.connect(self._open_pdf_for_document)
        self._chunk_list_view = ChunkListView()
        self._chunk_list_view.open_pdf_requested.connect(self._open_pdf_for_document)

        self._main_container = QWidget()
        main_layout = QVBoxLayout(self._main_container)
        main_layout.addWidget(self._search_view)
        main_layout.addWidget(self._library_view)
        main_layout.addWidget(self._indexing_scope_view)
        main_layout.addWidget(self._paper_list_view)
        main_layout.addWidget(self._chunk_list_view)

        self._stack.addWidget(self._onboarding_view)
        self._stack.addWidget(self._main_container)

        self._setup_menu_bar()
        if auto_start:
            self._determine_initial_view()

    def _determine_initial_view(self) -> None:
        saved_path = self._settings_manager.get_zotero_path()

        if saved_path and self._zotero_manager.is_valid_zotero_directory(saved_path):
            self._show_main_view(saved_path)
            return

        self._show_onboarding_view()

    def _show_main_view(self, zotero_path: Path | None = None) -> None:
        self._stack.setCurrentWidget(self._main_container)
        self._refresh_library(zotero_path or self._settings_manager.get_zotero_path())

    def _show_onboarding_view(self) -> None:
        self._stack.setCurrentWidget(self._onboarding_view)
        self._onboarding_view.start_detection()

    def _refresh_library(self, zotero_path: Path | None) -> None:
        if not zotero_path:
            self._library_view.show_error(
                "Zotero directory not configured. Please restart and select it."
            )
            return

        self._zotero_manager.set_zotero_path(zotero_path)
        try:
            items = self._zotero_manager.get_all_items()
            self._library_view.set_items(items)
            collections = self._zotero_manager.get_collections()
            self._indexing_scope_view.set_collections(collections)
        except ZoteroDatabaseError as error:
            self._library_view.show_error(str(error))

    def _handle_path_selected(self, path: str) -> None:
        actual_path = Path(path)
        self._settings_manager.set_zotero_path(actual_path)
        self._show_main_view(actual_path)

    def _setup_menu_bar(self) -> None:
        """Create the basic menu that includes the About dialog."""

        file_menu = self.menuBar().addMenu("&File")
        about_action = QAction("About Zotero RAG", self)
        about_action.triggered.connect(self._show_about_dialog)
        file_menu.addAction(about_action)

    def _show_about_dialog(self) -> None:
        """Present an informational dialog describing the application."""

        QMessageBox.about(
            self,
            "About Zotero RAG",
            "Zotero RAG is a PySide6 desktop shell for exploring Zotero references with embedded AI.",
        )

    def _start_indexing_task(self, scope: dict) -> None:
        worker = _IndexingRunnable(self._indexing_service, scope)
        worker.signals.progress.connect(self._handle_indexing_progress)
        worker.signals.finished.connect(lambda: self._indexing_scope_view.set_busy(False))
        self._indexing_scope_view.set_busy(True)
        self._thread_pool.start(worker)

    def _handle_indexing_progress(self, payload: dict) -> None:
        self._indexing_scope_view.update_progress(payload)

    def _on_search(self, query: str) -> None:
        worker = _SearchRunnable(self._search_service, query)
        worker.signals.result.connect(self._handle_search_result)
        worker.signals.error.connect(self._handle_search_error)
        worker.signals.finished.connect(self._handle_search_finished)
        self._search_view.clear_messages()
        self._search_view.set_busy(True)
        self._search_view.set_status("Searching...")
        self._thread_pool.start(worker)

    def _handle_search_result(self, result: SearchResult) -> None:
        self._state.search_matches = result.matches or []
        self._state.selected_paper = None
        self._refresh_results_views()
        match_count = len(self._state.search_matches)
        self._search_view.set_status(
            f"Found {match_count} results (embedding {len(result.query_embedding)} dims)."
        )

    def _handle_search_error(self, message: str) -> None:
        self._search_view.set_error(message)
        self._search_view.set_status("Search failed.")

    def _handle_search_finished(self) -> None:
        self._search_view.set_busy(False)

    def _refresh_results_views(self) -> None:
        """Update paper and chunk lists from current state."""
        documents: list = []
        seen: set[int] = set()
        for match in self._state.search_matches:
            doc = match.document
            if doc and doc.id is not None and doc.id not in seen:
                seen.add(doc.id)
                documents.append(doc)

        self._paper_list_view.set_papers(documents)
        self._chunk_list_view.update_chunks(
            self._state.search_matches,
            selected_document_id=self._state.selected_paper.id if self._state.selected_paper else None,
        )

    def _on_paper_selected(self, document) -> None:
        if document is None:
            return
        self._state.selected_paper = document
        self._chunk_list_view.update_chunks(
            self._state.search_matches, selected_document_id=document.id
        )

    def _clear_selection(self) -> None:
        self._state.selected_paper = None
        self._chunk_list_view.update_chunks(self._state.search_matches, None)

    def _open_pdf_for_document(self, document) -> None:
        if not document or not document.pdf_file_path:
            QMessageBox.warning(self, "Missing PDF", "This item does not have a PDF path.")
            return

        path = Path(document.pdf_file_path).expanduser()
        if not path.exists():
            QMessageBox.warning(self, "File not found", f"PDF not found: {path}")
            return

        # Launch in background to avoid blocking UI.
        runnable = _OpenPdfRunnable(path)
        self._thread_pool.start(runnable)


class _IndexingWorkerSignals(QObject):
    progress = Signal(dict)
    finished = Signal()


class _IndexingRunnable(QRunnable):
    """Background task runner for indexing requests."""

    def __init__(self, service: IndexingService, scope: dict) -> None:
        super().__init__()
        self._service = service
        self._scope = scope
        self.signals = _IndexingWorkerSignals()

    def run(self) -> None:
        try:
            self._service.set_progress_callback(self.signals.progress.emit)
            self._service.start_indexing(self._scope)
        finally:
            self._service.set_progress_callback(None)
            self.signals.finished.emit()


class _SearchWorkerSignals(QObject):
    result = Signal(SearchResult)
    error = Signal(str)
    finished = Signal()


class _SearchRunnable(QRunnable):
    """Background task runner for search requests."""

    def __init__(self, service: SearchService, query: str) -> None:
        super().__init__()
        self._service = service
        self._query = query
        self.signals = _SearchWorkerSignals()

    def run(self) -> None:
        try:
            result = self._service.search(self._query)
            self.signals.result.emit(result)
        except SearchServiceError as error:
            self.signals.error.emit(str(error))
        except Exception as error:  # pragma: no cover - safeguard
            self.signals.error.emit(str(error))
        finally:
            self.signals.finished.emit()


class _OpenPdfRunnable(QRunnable):
    """Open a PDF using the system default viewer without blocking the UI."""

    def __init__(self, pdf_path: Path) -> None:
        super().__init__()
        self._pdf_path = pdf_path

    def run(self) -> None:
        try:
            if sys.platform.startswith("darwin"):
                subprocess.Popen(["open", str(self._pdf_path)])
            elif os.name == "nt":
                os.startfile(self._pdf_path)  # type: ignore[attr-defined]
            else:
                subprocess.Popen(["xdg-open", str(self._pdf_path)])
        except Exception:
            logger.exception("Failed to open PDF: %s", self._pdf_path)
