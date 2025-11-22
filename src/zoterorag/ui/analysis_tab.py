"""Tab container for AI analysis output."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QPushButton, QVBoxLayout, QWidget

class AnalysisTab(QWidget):
    """Holds placeholders for AI-generated analysis and token usage data."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.analyze_button = QPushButton("Analyze Selected Papers")
        self.analyze_button.setEnabled(False)
        self.analyze_button.setProperty("busy", False)
        self.analyze_button.setToolTip("Run a search and select papers to enable analysis.")

        self.loading_label = QLabel()
        self.loading_label.setVisible(False)

        self.analysis_label = QLabel()
        self.analysis_label.setWordWrap(True)
        self.analysis_label.setMinimumHeight(80)
        self.analysis_label.setTextInteractionFlags(
            self.analysis_label.textInteractionFlags() | Qt.TextSelectableByMouse
        )

        layout = QVBoxLayout(self)
        layout.addWidget(self.analyze_button)
        layout.addWidget(self.loading_label)
        layout.addWidget(self.analysis_label)
        layout.addStretch()
