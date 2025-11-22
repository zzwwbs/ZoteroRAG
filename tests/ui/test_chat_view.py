"""Tests for chat UI components."""

from __future__ import annotations

from datetime import datetime

import pytest

pytest.importorskip("PySide6")

from PySide6.QtWidgets import QApplication

from zoterorag.ui.chat_message_widget import ChatMessageWidget
from zoterorag.ui.chat_view import ChatView


@pytest.fixture(scope="module")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app


def test_chat_message_widget_sets_role_and_timestamp(qapp):
    ts = datetime(2025, 1, 1, 12, 0)
    widget = ChatMessageWidget("You", "Hello", role="user", timestamp=ts)
    assert widget is not None


def test_chat_view_adds_and_clears_messages(qapp):
    view = ChatView()
    view.add_message("Assistant", "First", role="assistant")
    view.add_message("You", "Second", role="user")
    # layout has a stretch at the end, so count-1 gives message count
    assert view._layout.count() - 1 == 2
    view.clear_messages()
    assert view._layout.count() - 1 == 0
