"""Tests for SettingsManager secure API key management."""

from __future__ import annotations

import types

import pytest

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


def test_save_and_get_api_key(monkeypatch, tmp_path):
    dummy_keyring = DummyKeyring()
    fake_module = types.SimpleNamespace(
        set_password=dummy_keyring.set_password,
        get_password=dummy_keyring.get_password,
        delete_password=dummy_keyring.delete_password,
    )
    monkeypatch.setattr("zoterorag.config.settings_manager.keyring", fake_module)

    manager = SettingsManager(settings_dir=tmp_path, keyring_service="svc")
    manager.set_api_key_securely("secret-key")
    assert manager.get_api_key() == "secret-key"


def test_get_api_key_not_found(monkeypatch, tmp_path):
    dummy_keyring = DummyKeyring()
    fake_module = types.SimpleNamespace(
        set_password=dummy_keyring.set_password,
        get_password=dummy_keyring.get_password,
        delete_password=dummy_keyring.delete_password,
    )
    monkeypatch.setattr("zoterorag.config.settings_manager.keyring", fake_module)

    manager = SettingsManager(settings_dir=tmp_path, keyring_service="svc")
    assert manager.get_api_key() is None


def test_keyring_exception_is_logged_and_returns_none(monkeypatch, tmp_path, caplog):
    class FailingKeyring:
        def set_password(self, *args, **kwargs):
            raise RuntimeError("fail")

        def get_password(self, *args, **kwargs):
            raise RuntimeError("fail")

        def delete_password(self, *args, **kwargs):
            raise RuntimeError("fail")

    monkeypatch.setattr("zoterorag.config.settings_manager.keyring", FailingKeyring())
    manager = SettingsManager(settings_dir=tmp_path, keyring_service="svc")

    manager.set_api_key_securely("anything")
    assert manager.get_api_key() is None
    assert any("Keyring" in rec.message for rec in caplog.records)


def test_api_key_not_leaked_to_plaintext_config_when_using_keyring(monkeypatch, tmp_path):
    """Regression test: API key must NOT be written to disk when keyring is used."""
    import json

    dummy_keyring = DummyKeyring()
    fake_module = types.SimpleNamespace(
        set_password=dummy_keyring.set_password,
        get_password=dummy_keyring.get_password,
        delete_password=dummy_keyring.delete_password,
    )
    monkeypatch.setattr("zoterorag.config.settings_manager.keyring", fake_module)

    manager = SettingsManager(settings_dir=tmp_path, keyring_service="svc")
    
    # Store API key securely in keyring
    manager.set_api_key_securely("secret-key-123")
    
    # Modify another setting (this previously leaked the API key to disk)
    manager.set_enable_ai_analysis(True)
    
    # Verify API key is NOT in plaintext config file
    settings_file = tmp_path / "settings.json"
    if settings_file.exists():
        content = json.loads(settings_file.read_text())
        assert content.get("api_key") is None, "API key leaked to plaintext config file!"
    
    # But API key should still be retrievable from keyring
    assert manager.get_api_key() == "secret-key-123"
