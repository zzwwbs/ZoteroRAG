"""Tests for retrieval toggle and chunk count controls in AnalysisTab."""

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


def test_retrieval_toggle_enables_spinbox(qapp):
    tab = AnalysisTab()
    tab.include_context_checkbox.setChecked(True)
    assert tab.chunk_spinbox.isEnabled() is True
    tab.include_context_checkbox.setChecked(False)
    assert tab.chunk_spinbox.isEnabled() is False
    assert tab.chunk_spinbox.minimum() == 1
    assert tab.chunk_spinbox.maximum() == 20
    assert tab.chunk_spinbox.value() == 5
