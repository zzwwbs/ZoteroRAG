"""Widget representing a single chat message with sender, content, and timestamp."""

from __future__ import annotations

from datetime import datetime

from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget
from PySide6.QtCore import Qt


class ChatMessageWidget(QWidget):
    """Display a chat message with basic styling for role and errors."""

    def __init__(
        self,
        sender: str,
        content: str,
        *,
        role: str = "assistant",
        timestamp: datetime | None = None,
        is_error: bool = False,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        ts = timestamp or datetime.now()
        header = QLabel(f"{sender} • {ts.strftime('%Y-%m-%d %H:%M')}")
        header.setObjectName("chatHeader")
        header.setAlignment(Qt.AlignLeft if role != "user" else Qt.AlignRight)

        body = QLabel(content)
        body.setWordWrap(True)
        body.setTextInteractionFlags(body.textInteractionFlags() | Qt.TextSelectableByMouse)
        body.setObjectName("chatBody")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 6, 8, 6)
        if role == "user":
            layout.setAlignment(Qt.AlignRight | Qt.AlignTop)
        else:
            layout.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        layout.addWidget(header)
        layout.addWidget(body)

        if is_error:
            self.setStyleSheet(
                "#chatHeader { color: #a00; } "
                "#chatBody { background: #ffe6e6; border-radius: 6px; padding: 6px; }"
            )
        elif role == "user":
            self.setStyleSheet(
                "#chatHeader { color: #666; } "
                "#chatBody { background: #e8f2ff; border-radius: 6px; padding: 6px; }"
            )
        else:
            self.setStyleSheet(
                "#chatHeader { color: #666; } "
                "#chatBody { background: #f5f5f5; border-radius: 6px; padding: 6px; }"
            )
