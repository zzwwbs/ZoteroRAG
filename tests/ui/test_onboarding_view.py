"""Tests for onboarding view flow."""

from __future__ import annotations

import pytest

pytest.importorskip("PySide6")

from PySide6.QtWidgets import QApplication

from zoterorag.ui.onboarding_view import OnboardingView


class DummyZoteroManager:
    def __init__(self, valid_path: str | None = None) -> None:
        self._valid_path = valid_path

    def detect_zotero_directory(self):
        return self._valid_path

    def is_valid_zotero_directory(self, path):
        return bool(path)


@pytest.fixture(scope="module")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app


def test_privacy_ack_required_for_path_step(qapp):
    view = OnboardingView(DummyZoteroManager("/tmp/z"))
    assert view._stack.currentWidget() == view._welcome
    # Move to privacy
    view._stack.setCurrentWidget(view._privacy)
    view._go_to_path_step()
    # Without checking, it stays
    assert view._stack.currentWidget() == view._privacy
    view._privacy_ack.setChecked(True)
    view._go_to_path_step()
    assert view._stack.currentWidget() == view._path_step


def test_done_signal_emitted(qapp, qtbot):
    view = OnboardingView(DummyZoteroManager("/tmp/z"))
    view._stack.setCurrentWidget(view._path_step)
    view._path_label.setText("Selected: /tmp/z")
    with qtbot.waitSignal(view.done, timeout=1000) as blocker:
        view._finish("/tmp/z")
    assert blocker.args[0] == "/tmp/z"
