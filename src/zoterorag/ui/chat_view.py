"""Scrollable chat view for displaying conversation messages."""

from __future__ import annotations

from datetime import datetime

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QScrollArea, QVBoxLayout, QWidget

from .chat_message_widget import ChatMessageWidget


class ChatView(QWidget):
    """Container that renders chat messages in a scrollable list."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._scroll_area = QScrollArea()
        self._scroll_area.setWidgetResizable(True)
        self._content = QWidget()
        self._layout = QVBoxLayout(self._content)
        self._layout.setSpacing(8)
        self._layout.addStretch()
        self._scroll_area.setWidget(self._content)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(self._scroll_area)

    def add_message(
        self,
        sender: str,
        content: str,
        *,
        role: str = "assistant",
        timestamp: datetime | None = None,
        is_error: bool = False,
    ) -> None:
        """Append a message and auto-scroll to the bottom."""
        widget = ChatMessageWidget(sender, content, role=role, timestamp=timestamp, is_error=is_error)
        # Insert above the stretch at the end.
        self._layout.insertWidget(self._layout.count() - 1, widget)
        QTimer.singleShot(0, self._scroll_to_bottom)

    def clear_messages(self) -> None:
        """Remove all chat messages."""
        # Leave the final stretch.
        for i in reversed(range(self._layout.count() - 1)):
            item = self._layout.itemAt(i)
            widget = item.widget()
            if widget:
                widget.setParent(None)

    def _scroll_to_bottom(self) -> None:
        try:
            bar = self._scroll_area.verticalScrollBar()
            if bar:
                bar.setValue(bar.maximum())
        except RuntimeError:
            # Widget may have been deleted if called from deferred QTimer
            pass
