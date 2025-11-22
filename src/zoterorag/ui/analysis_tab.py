"""Tab container for AI analysis output."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QPushButton, QVBoxLayout, QWidget, QHBoxLayout, QTextEdit

from .chat_view import ChatView

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

        self.chat_view = ChatView()
        self.chat_input = QTextEdit()
        self.chat_input.setPlaceholderText("Type a follow-up question…")
        self.chat_input.setFixedHeight(80)
        self.send_button = QPushButton("Send")
        self.send_button.setToolTip("Send a new question based on current search results.")

        input_row = QHBoxLayout()
        input_row.addWidget(self.chat_input, stretch=1)
        input_row.addWidget(self.send_button)

        layout = QVBoxLayout(self)
        layout.addWidget(self.analyze_button)
        layout.addWidget(self.loading_label)
        layout.addWidget(self.chat_view)
        layout.addLayout(input_row)
        layout.addStretch()
