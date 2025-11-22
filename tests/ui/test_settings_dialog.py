"""Tests for SettingsDialog loading and saving."""

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
        self._settings = AppSettings(
            zotero_data_path="/tmp/zotero",
            embedding_base_url="https://api.example.com/v1",
            chat_base_url="https://api.example.com/v1",
            embedding_provider="openai",
            chat_provider="openai",
            embedding_model="embed-1",
            chat_model="chat-1",
            chunk_size=700,
            chunk_overlap=50,
            default_search_results=15,
            theme="dark",
            enable_ai_analysis=True,
        )

    def load_settings(self):
        return self._settings

    def save_settings(self, settings: AppSettings):
        self.saved = settings

    def set_embedding_api_key_securely(self, key: str | None):
        self.secure_key = ("embedding", key)

    def set_chat_api_key_securely(self, key: str | None):
        self.secure_key = ("chat", key)

    def get_api_key(self):
        return None

    def get_embedding_api_key(self):
        return None

    def get_chat_api_key(self):
        return None

    def supports_secure_storage(self):
        return False

    @property
    def _keyring_service(self):
        return "svc"

    def refresh(self):
        return self._settings


@pytest.fixture(scope="module")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app


def test_dialog_loads_settings_into_fields(qapp):
    manager = FakeSettingsManager()
    dialog = SettingsDialog(manager, validator=None)

    assert dialog._zotero_path.text() == "/tmp/zotero"
    assert dialog._embedding_base_url.text() == "https://api.example.com/v1"
    assert dialog._embedding_model.text() == "embed-1"
    assert dialog._chat_base_url.text() == "https://api.example.com/v1"
    assert dialog._chat_model.text() == "chat-1"
    assert dialog._chunk_size.value() == 700
    assert dialog._chunk_overlap.value() == 50
    assert dialog._default_search_results.value() == 15
    assert dialog._theme.currentText() == "dark"
    assert dialog._ai_toggle.isChecked() is True


def test_dialog_save_calls_settings_manager(qapp):
    manager = FakeSettingsManager()
    dialog = SettingsDialog(manager, validator=None)
    dialog._embedding_key.setText("secret-emb")
    dialog._chat_key.setText("secret-chat")
    dialog._zotero_path.setText("/new/path")
    dialog._chunk_size.setValue(800)
    dialog._handle_save()

    # Last secure key set (chat)
    assert manager.secure_key == ("chat", "secret-chat")
    assert manager.saved is not None
    assert manager.saved.zotero_data_path == "/new/path"
    assert manager.saved.chunk_size == 800
