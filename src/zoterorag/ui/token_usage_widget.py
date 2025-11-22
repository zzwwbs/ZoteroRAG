"""Widget to display session token usage and breakdown."""

from __future__ import annotations

from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget, QHBoxLayout, QGroupBox, QGridLayout

from ..core.data.models import TokenUsage


class TokenUsageWidget(QWidget):
    """Shows session token totals and breakdown by operation."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._total_tokens = 0
        self._embedding_calls = 0
        self._analysis_calls = 0

        self._total_label = QLabel("Session Tokens: 0")
        self._breakdown_label = QLabel("Embedding Calls: 0 | AI Analysis Calls: 0")
        self._disclaimer = QLabel(
            "Token counts are estimates for this session and may differ from provider billing."
        )
        self._disclaimer.setWordWrap(True)

        box = QGroupBox("Token Usage")
        grid = QGridLayout(box)
        grid.addWidget(self._total_label, 0, 0, 1, 2)
        grid.addWidget(self._breakdown_label, 1, 0, 1, 2)

        layout = QVBoxLayout(self)
        layout.addWidget(box)
        layout.addWidget(self._disclaimer)
        layout.addStretch()

    def update_usage(self, usage: TokenUsage) -> None:
        """Update totals based on a new usage record."""
        self._total_tokens += max(0, usage.tokens_used)
        if usage.operation == "embedding":
            self._embedding_calls += 1
        elif usage.operation == "chat_completion":
            self._analysis_calls += 1
        self._refresh_labels()

    def get_session_totals(self) -> dict:
        return {
            "tokens": self._total_tokens,
            "embedding_calls": self._embedding_calls,
            "analysis_calls": self._analysis_calls,
        }

    def _refresh_labels(self) -> None:
        self._total_label.setText(f"Session Tokens: {self._total_tokens}")
        self._breakdown_label.setText(
            f"Embedding Calls: {self._embedding_calls} | AI Analysis Calls: {self._analysis_calls}"
        )
