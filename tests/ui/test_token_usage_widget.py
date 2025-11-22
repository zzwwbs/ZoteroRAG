"""Tests for TokenUsageWidget."""

from __future__ import annotations

import pytest

pytest.importorskip("PySide6")

from PySide6.QtWidgets import QApplication

from zoterorag.core.data.models import TokenUsage
from zoterorag.ui.token_usage_widget import TokenUsageWidget


@pytest.fixture(scope="module")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app


def test_usage_updates_labels(qapp):
    widget = TokenUsageWidget()
    usage1 = TokenUsage(operation="embedding", tokens_used=10, model="m")
    usage2 = TokenUsage(operation="chat_completion", tokens_used=5, model="m")

    widget.update_usage(usage1)
    widget.update_usage(usage2)

    totals = widget.get_session_totals()
    assert totals["tokens"] == 15
    assert totals["embedding_calls"] == 1
    assert totals["analysis_calls"] == 1
    assert "15" in widget._total_label.text()
