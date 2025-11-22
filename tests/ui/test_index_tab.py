"""UI tests for the Index tab start/cancel interactions."""

from __future__ import annotations

import pytest

pytest.importorskip("PySide6")

from PySide6.QtCore import Qt
from PySide6.QtTest import QSignalSpy
from PySide6.QtWidgets import QApplication

from zoterorag.ui.index_tab import IndexTab


@pytest.fixture(scope="module")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app


def test_index_tab_switches_button_to_cancel_and_emits_signals(qapp, qtbot):
    tab = IndexTab()
    qtbot.addWidget(tab)

    start_spy = QSignalSpy(tab.start_indexing)
    cancel_spy = QSignalSpy(tab.cancel_indexing)

    qtbot.mouseClick(tab.indexing_scope_view._start_button, Qt.LeftButton)
    assert start_spy.count() == 1
    assert tab.indexing_scope_view._start_button.text() == "Cancel Indexing"

    qtbot.mouseClick(tab.indexing_scope_view._start_button, Qt.LeftButton)
    assert cancel_spy.count() == 1
    assert "Cancelling" in tab.indexing_scope_view._start_button.text()
