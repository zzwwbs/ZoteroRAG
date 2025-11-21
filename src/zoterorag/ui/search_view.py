"""Search bar widget that emits search triggers."""

from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class SearchView(QWidget):
    """Simple search input with keyboard and button activation."""

    search_triggered = Signal(str)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._is_busy = False

        self._input = QLineEdit()
        self._input.setPlaceholderText("Ask a question...")
        self._input.setAccessibleName("Search query input")
        self._input.returnPressed.connect(self._emit_search)

        self._start_button = QPushButton("Search")
        self._start_button.setAccessibleName("Start search")
        self._start_button.clicked.connect(self._emit_search)

        self._status_label = QLabel()
        self._status_label.setAccessibleName("Search status")

        self._error_label = QLabel()
        self._error_label.setAccessibleName("Search error")
        self._error_label.setStyleSheet("color: red;")

        row = QHBoxLayout()
        row.addWidget(self._input, stretch=1)
        row.addWidget(self._start_button)

        layout = QVBoxLayout(self)
        layout.addLayout(row)
        layout.addWidget(self._status_label)
        layout.addWidget(self._error_label)
        layout.addStretch()

    def _emit_search(self) -> None:
        text = self._input.text().strip()
        self._error_label.clear()
        if not text:
            self._status_label.setText("Enter a query to search.")
            return
        self.search_triggered.emit(text)

    def set_busy(self, busy: bool) -> None:
        """Toggle busy state and update UI affordances."""

        self._is_busy = busy
        self._input.setDisabled(busy)
        self._start_button.setDisabled(busy)
        if busy:
            self._status_label.setText("Searching...")
        elif self._status_label.text() == "Searching...":
            self._status_label.setText("")

    def set_status(self, message: str) -> None:
        """Display a non-error status message."""
        self._status_label.setText(message)

    def set_error(self, message: str) -> None:
        """Display an error message."""
        self._error_label.setText(message)

    def clear_messages(self) -> None:
        """Reset any status or error messages."""
        self._status_label.clear()
        self._error_label.clear()

    def is_busy(self) -> bool:
        """Return whether the view is currently busy."""
        return self._is_busy
