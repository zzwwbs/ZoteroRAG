"""Tests for the SearchView widget."""

from __future__ import annotations

import pytest

pytest.importorskip("PySide6")

from PySide6.QtCore import Qt
from PySide6.QtTest import QSignalSpy, QTest
from PySide6.QtWidgets import QApplication

from zoterorag.ui.search_view import SearchView


@pytest.fixture(scope="module")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app


def test_emits_on_button_click(qapp):
    view = SearchView()
    view._input.setText("test query")
    spy = QSignalSpy(view.search_triggered)

    view._start_button.click()

    assert spy.count() == 1
    assert spy.at(0)[0] == "test query"


def test_emits_on_enter_key(qapp):
    view = SearchView()
    view._input.setText("enter trigger")
    spy = QSignalSpy(view.search_triggered)

    QTest.keyClick(view._input, Qt.Key_Return)

    assert spy.count() == 1
    assert spy.at(0)[0] == "enter trigger"


def test_busy_state_disables_inputs(qapp):
    view = SearchView()
    view.set_busy(True)

    assert view.is_busy() is True
    assert view._input.isEnabled() is False
    assert view._start_button.isEnabled() is False

    view.set_busy(False)
    assert view.is_busy() is False
