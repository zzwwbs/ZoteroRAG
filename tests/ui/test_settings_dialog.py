"""Tests for SettingsDialog interactions."""

from __future__ import annotations

import pytest

pytest.importorskip("PySide6")

from PySide6.QtWidgets import QApplication

from zoterorag.config.settings_manager import AppSettings
from zoterorag.ui.settings_dialog import SettingsDialog


class FakeSettingsManager:
    def __init__(self):
        self.saved = None
        self.secure_key = None

    def load_settings(self):
        return AppSettings()

    def save_settings(self, settings: AppSettings):
        self.saved = settings

    def set_api_key_securely(self, key: str | None):
        self.secure_key = key

    def get_api_key(self):
        return None

    def get_zotero_path(self):
        return None


@pytest.fixture(scope="module")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app


def test_save_updates_settings_and_key(qapp):
    manager = FakeSettingsManager()
    dialog = SettingsDialog(manager, validator=None)

    dialog._api_key_input.setText("abc123")
    dialog._ai_toggle.setChecked(True)

    dialog._handle_save()

    assert manager.secure_key == "abc123"
    assert manager.saved is not None
    assert manager.saved.enable_ai_analysis is True
