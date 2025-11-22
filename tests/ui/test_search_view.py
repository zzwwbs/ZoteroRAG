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
    view.result_count.setValue(7)
    spy = QSignalSpy(view.search_triggered)

    view._start_button.click()

    assert spy.count() == 1
    args = spy.at(0)
    assert args[0] == "test query"
    assert args[1] == 7


def test_emits_on_enter_key(qapp):
    view = SearchView()
    view._input.setText("enter trigger")
    view.result_count.setValue(5)
    spy = QSignalSpy(view.search_triggered)

    QTest.keyClick(view._input, Qt.Key_Return)

    assert spy.count() == 1
    args = spy.at(0)
    assert args[0] == "enter trigger"
    assert args[1] == 5


def test_busy_state_disables_inputs(qapp):
    view = SearchView()
    view.set_busy(True)

    assert view.is_busy() is True
    assert view._input.isEnabled() is False
    assert view.result_count.isEnabled() is False
    assert view._start_button.isEnabled() is False

    view.set_busy(False)
    assert view.is_busy() is False
