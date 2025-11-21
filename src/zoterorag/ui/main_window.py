"""Main window implementation for the Zotero RAG desktop application."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QRunnable, QThreadPool
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QMessageBox,
    QMainWindow,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from ..config.settings_manager import SettingsManager
from ..core.services.indexing_service import IndexingService
from ..core.services.zotero_manager import (
    ZoteroDatabaseError,
    ZoteroManager,
)
from .indexing_scope_view import IndexingScopeView
from .library_view import LibraryView
from .onboarding_view import OnboardingView


class MainWindow(QMainWindow):
    """Primary shell window with setup detection and onboarding."""

    def __init__(
        self,
        settings_manager: SettingsManager | None = None,
        zotero_manager: ZoteroManager | None = None,
    ) -> None:
        super().__init__()
        self.setWindowTitle("Zotero RAG")
        self.resize(1024, 768)

        self._settings_manager = settings_manager or SettingsManager()
        self._zotero_manager = zotero_manager or ZoteroManager()
        self._thread_pool = QThreadPool.globalInstance()
        self._indexing_service = IndexingService(self._zotero_manager)

        self._stack = QStackedWidget()
        self.setCentralWidget(self._stack)

        self._onboarding_view = OnboardingView(self._zotero_manager)
        self._onboarding_view.path_confirmed.connect(self._handle_path_selected)

        self._library_view = LibraryView()
        self._indexing_scope_view = IndexingScopeView()
        self._indexing_scope_view.scope_selected.connect(self._start_indexing_task)

        self._main_container = QWidget()
        main_layout = QVBoxLayout(self._main_container)
        main_layout.addWidget(self._library_view)
        main_layout.addWidget(self._indexing_scope_view)

        self._stack.addWidget(self._onboarding_view)
        self._stack.addWidget(self._main_container)

        self._setup_menu_bar()
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
        task = _IndexingRunnable(self._indexing_service, scope)
        self._thread_pool.start(task)


class _IndexingRunnable(QRunnable):
    """Background task runner for indexing requests."""

    def __init__(self, service: IndexingService, scope: dict) -> None:
        super().__init__()
        self._service = service
        self._scope = scope

    def run(self) -> None:
        self._service.start_indexing(self._scope)
