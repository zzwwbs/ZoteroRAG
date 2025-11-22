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
    usage1 = TokenUsage(operation="embedding", tokens_used=10, model="m", prompt_tokens=6, completion_tokens=4)
    usage2 = TokenUsage(operation="chat_completion", tokens_used=5, model="m2", prompt_tokens=3, completion_tokens=2)

    widget.update_usage(usage1)
    widget.update_usage(usage2)

    totals = widget.get_session_totals()
    # Updated for v1.1 API: get_session_totals() returns separate embedding_tokens and analysis_tokens
    assert totals["embedding_tokens"] == 10
    assert totals["analysis_tokens"] == 5
    assert totals["embedding_tokens"] + totals["analysis_tokens"] == 15
    assert totals["embedding_calls"] == 1
    assert totals["analysis_calls"] == 1
    assert totals["embedding_prompt_tokens"] == 6
    assert totals["analysis_completion_tokens"] == 2
    # Check that labels are updated (widget displays prompt tokens for embedding, prompt+completion for AI)
    assert "6 tokens (prompt only)" in widget._embedding_label.text()  # Embedding shows prompt tokens only
    assert "prompt 3 / completion 2" in widget._analysis_label.text()  # AI shows both
