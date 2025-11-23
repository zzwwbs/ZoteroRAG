"""Tests for indexing summary display in IndexTab."""

from __future__ import annotations

import pytest

pytest.importorskip("PySide6")

from PySide6.QtWidgets import QApplication

from zoterorag.ui.index_tab import IndexTab


@pytest.fixture(scope="module")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app


def test_summary_label_updates(qapp):
    tab = IndexTab()
    tab.show()  # Need to show the tab for visibility to work properly
    qapp.processEvents()  # Process Qt events
    assert tab.summary_label.isVisible() is False
    tab.update_summary("Processed: 2 | ✅ Indexed: 1")
    qapp.processEvents()  # Process Qt events
    assert tab.summary_label.isVisible() is True
    assert "Processed" in tab.summary_label.text()
