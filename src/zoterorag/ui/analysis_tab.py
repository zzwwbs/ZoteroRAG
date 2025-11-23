"""Tab container for AI analysis output."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QHBoxLayout,
    QTextEdit,
    QCheckBox,
    QSpinBox,
    QSizePolicy,
)

from .chat_view import ChatView

class AnalysisTab(QWidget):
    """Holds placeholders for AI-generated analysis and token usage data."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.conversation_history: list[dict] = []
        self.analyze_button = QPushButton("Analyze Selected Papers")
        self.analyze_button.setEnabled(False)
        self.analyze_button.setProperty("busy", False)
        self.analyze_button.setToolTip("Run a search and select papers to enable analysis.")

        self.loading_label = QLabel()
        self.loading_label.setVisible(False)

        self.chat_view = ChatView()
        self.chat_view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.chat_input = QTextEdit()
        self.chat_input.setPlaceholderText("Type a follow-up question…")
        self.chat_input.setMinimumHeight(70)  # roughly 3 lines
        self.chat_input.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.chat_input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.MinimumExpanding)
        self.send_button = QPushButton("Send")
        self.send_button.setToolTip("Send a new question based on current search results.")

        self.include_context_checkbox = QCheckBox("Also search database for chat")
        self.include_context_checkbox.setChecked(True)
        self.include_context_checkbox.setToolTip("Include relevant paper excerpts in AI analysis.")
        self.chunk_spinbox = QSpinBox()
        self.chunk_spinbox.setRange(1, 20)
        self.chunk_spinbox.setValue(5)
        self.chunk_spinbox.setEnabled(True)

        self.history_spinbox = QSpinBox()
        self.history_spinbox.setRange(1, 50)
        self.history_spinbox.setValue(10)
        self.history_spinbox.setToolTip("Number of recent chat messages to include in the next request.")

        def _toggle_chunks(checked: bool) -> None:
            self.chunk_spinbox.setEnabled(checked)

        self.include_context_checkbox.toggled.connect(_toggle_chunks)

        controls_row = QHBoxLayout()
        controls_row.addWidget(self.include_context_checkbox)
        controls_row.addWidget(QLabel("Chunks:"))
        controls_row.addWidget(self.chunk_spinbox)
        controls_row.addWidget(QLabel("Messages:"))
        controls_row.addWidget(self.history_spinbox)
        controls_row.addStretch()

        input_row = QHBoxLayout()
        input_row.addWidget(self.chat_input, stretch=3)
        input_row.addWidget(self.send_button)

        layout = QVBoxLayout(self)
        layout.addWidget(self.analyze_button)
        layout.addWidget(self.loading_label)
        layout.addWidget(self.chat_view)
        layout.addLayout(controls_row)
        layout.addLayout(input_row)
        layout.addStretch()

    def reset_conversation(self) -> None:
        """Clear chat view and history."""
        self.chat_view.clear_messages()
        self.conversation_history.clear()
        self.include_context_checkbox.setChecked(True)
        self.chunk_spinbox.setValue(5)
        self.history_spinbox.setValue(10)

    def add_user_message(self, content: str) -> None:
        self.conversation_history.append({"role": "user", "content": content})
        self._truncate_history()
        self.chat_view.add_message("You", content, role="user")

    def add_assistant_message(self, content: str) -> None:
        self.conversation_history.append({"role": "assistant", "content": content})
        self._truncate_history()
        self.chat_view.add_message("Assistant", content, role="assistant")

    def add_error_message(self, content: str) -> None:
        self.chat_view.add_message("Error", content, role="error", is_error=True)

    def get_history(self) -> list[dict]:
        return list(self.conversation_history)

    def _truncate_history(self, limit: int = 10) -> None:
        effective_limit = self.history_spinbox.value() if hasattr(self, "history_spinbox") else limit
        if len(self.conversation_history) > effective_limit:
            self.conversation_history = self.conversation_history[-effective_limit:]
