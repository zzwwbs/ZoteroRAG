"""Placeholder tab for future settings UI."""

from __future__ import annotations

from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget


class SettingsTab(QWidget):
    """Simple placeholder until settings UI is built."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Settings will be available in a future update."))
        layout.addStretch()
