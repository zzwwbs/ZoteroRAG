"""Tests for secure API key handling in SettingsManager."""

from __future__ import annotations

import types
from pathlib import Path

from zoterorag.config.settings_manager import SettingsManager


class DummyKeyring:
    def __init__(self):
        self.store = {}

    def set_password(self, service, account, password):
        self.store[(service, account)] = password

    def get_password(self, service, account):
        return self.store.get((service, account))

    def delete_password(self, service, account):
        self.store.pop((service, account), None)


def test_secure_api_key_storage(monkeypatch, tmp_path: Path):
    dummy_keyring = DummyKeyring()
    fake_module = types.SimpleNamespace(
        set_password=dummy_keyring.set_password,
        get_password=dummy_keyring.get_password,
        delete_password=dummy_keyring.delete_password,
    )
    monkeypatch.setattr("zoterorag.config.settings_manager.keyring", fake_module)

    manager = SettingsManager(settings_dir=tmp_path, keyring_service="test-service")
    manager.set_api_key_securely("secret123")

    assert dummy_keyring.get_password("test-service", "api_key") == "secret123"
    assert manager.get_api_key() == "secret123"
