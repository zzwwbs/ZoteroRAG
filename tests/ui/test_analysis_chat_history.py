"""Tests for AnalysisTab conversation history management."""

from __future__ import annotations

import pytest

pytest.importorskip("PySide6")

from PySide6.QtWidgets import QApplication

from zoterorag.ui.analysis_tab import AnalysisTab


@pytest.fixture(scope="module")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app


def test_history_appends_and_truncates(qapp):
    tab = AnalysisTab()
    tab.reset_conversation()
    for i in range(12):
        tab.add_user_message(f"msg {i}")
    assert len(tab.get_history()) == 10
    assert tab.get_history()[0]["content"] == "msg 2"


def test_assistant_messages_recorded(qapp):
    tab = AnalysisTab()
    tab.reset_conversation()
    tab.add_user_message("hi")
    tab.add_assistant_message("hello")
    history = tab.get_history()
    assert history[-1]["role"] == "assistant"
    assert history[-1]["content"] == "hello"
