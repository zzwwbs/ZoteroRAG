"""Application launcher helpers."""

from __future__ import annotations

from PySide6.QtWidgets import QApplication

from .ui.main_window import MainWindow


def main() -> int:
    """Create and run the QApplication loop."""

    app = QApplication([])
    window = MainWindow()
    window.show()
    return app.exec()
