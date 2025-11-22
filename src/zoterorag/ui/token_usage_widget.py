"""Widget to display session token usage and breakdown."""

from __future__ import annotations

from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget, QGroupBox, QGridLayout

from ..core.data.models import TokenUsage


class TokenUsageWidget(QWidget):
    """Shows session token totals and breakdown by operation."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._embedding_calls = 0
        self._analysis_calls = 0
        self._embedding_tokens = 0
        self._analysis_tokens = 0
        self._embedding_prompt_tokens = 0
        self._analysis_prompt_tokens = 0
        self._analysis_completion_tokens = 0
        self._embedding_model: str | None = None
        self._analysis_model: str | None = None

        self._embedding_label = QLabel("Embedding: –")
        self._analysis_label = QLabel("AI Analysis: –")
        self._disclaimer = QLabel(
            "Token counts are estimates for this session and may differ from provider billing."
        )
        self._disclaimer.setWordWrap(True)

        box = QGroupBox("Token Usage")
        grid = QGridLayout(box)
        grid.addWidget(self._embedding_label, 0, 0, 1, 2)
        grid.addWidget(self._analysis_label, 1, 0, 1, 2)

        layout = QVBoxLayout(self)
        layout.addWidget(box)
        layout.addWidget(self._disclaimer)
        layout.addStretch()

    def update_usage(self, usage: TokenUsage) -> None:
        """Update totals based on a new usage record."""
        if usage.operation == "embedding":
            self._embedding_calls += 1
            self._embedding_tokens += max(0, usage.tokens_used)
            self._embedding_prompt_tokens += max(0, usage.prompt_tokens)
            self._embedding_model = usage.model
        elif usage.operation == "chat_completion":
            self._analysis_calls += 1
            self._analysis_tokens += max(0, usage.tokens_used)
            self._analysis_prompt_tokens += max(0, usage.prompt_tokens)
            self._analysis_completion_tokens += max(0, usage.completion_tokens)
            self._analysis_model = usage.model
        self._refresh_labels()

    def get_session_totals(self) -> dict:
        return {
            "embedding_calls": self._embedding_calls,
            "analysis_calls": self._analysis_calls,
            "embedding_tokens": self._embedding_tokens,
            "analysis_tokens": self._analysis_tokens,
            "embedding_prompt_tokens": self._embedding_prompt_tokens,
            "analysis_prompt_tokens": self._analysis_prompt_tokens,
            "analysis_completion_tokens": self._analysis_completion_tokens,
            "embedding_model": self._embedding_model,
            "analysis_model": self._analysis_model,
        }

    def _refresh_labels(self) -> None:
        embed_model = self._embedding_model or "-"
        self._embedding_label.setText(
            f"Embedding ({embed_model}): {self._embedding_prompt_tokens} tokens (prompt only) | Calls: {self._embedding_calls}"
        )
        analysis_model = self._analysis_model or "-"
        self._analysis_label.setText(
            f"AI Analysis ({analysis_model}): prompt {self._analysis_prompt_tokens} / "
            f"completion {self._analysis_completion_tokens} tokens | Calls: {self._analysis_calls}"
        )
