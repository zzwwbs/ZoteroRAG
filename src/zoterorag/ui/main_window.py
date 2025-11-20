"""Main window implementation for the Zotero RAG desktop application."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QLabel,
    QMainWindow,
    QMessageBox,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from ..config.settings_manager import SettingsManager
from ..core.services.zotero_manager import ZoteroManager
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
        self._stack = QStackedWidget()
        self.setCentralWidget(self._stack)

        self._onboarding_view = OnboardingView(self._zotero_manager)
        self._onboarding_view.path_confirmed.connect(self._handle_path_selected)

        self._main_view = self._build_main_placeholder()

        self._stack.addWidget(self._onboarding_view)
        self._stack.addWidget(self._main_view)

        self._setup_menu_bar()
        self._determine_initial_view()

    def _determine_initial_view(self) -> None:
        saved_path = self._settings_manager.get_zotero_path()

        if saved_path and self._zotero_manager.is_valid_zotero_directory(saved_path):
            self._show_main_view()
            return

        self._show_onboarding_view()

    def _show_main_view(self) -> None:
        self._stack.setCurrentWidget(self._main_view)

    def _show_onboarding_view(self) -> None:
        self._stack.setCurrentWidget(self._onboarding_view)
        self._onboarding_view.start_detection()

    def _build_main_placeholder(self) -> QWidget:
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.addStretch()
        layout.addWidget(QLabel("Zotero RAG is ready to explore your library."))
        layout.addStretch()
        return container

    def _handle_path_selected(self, path: str) -> None:
        self._settings_manager.set_zotero_path(Path(path))
        self._show_main_view()

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
