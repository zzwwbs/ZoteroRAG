"""Main window implementation for the Zotero RAG desktop application."""

from __future__ import annotations

from PySide6.QtGui import QAction
from PySide6.QtWidgets import QMainWindow, QMessageBox


class MainWindow(QMainWindow):
    """Primary shell window with a minimal menu and About dialog."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Zotero RAG")
        self.resize(1024, 768)
        self._setup_menu_bar()

    def _setup_menu_bar(self) -> None:
        """Create the menu structure required by the acceptance criteria."""

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
