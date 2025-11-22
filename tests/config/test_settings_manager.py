"""Tests for SettingsManager migration and key handling."""

from __future__ import annotations

import json
from pathlib import Path

from zoterorag.config.settings_manager import AppSettings, SettingsManager


def test_migrates_legacy_settings_into_split_fields(tmp_path):
    settings_dir = tmp_path / "settings"
    settings_dir.mkdir()
    payload = {
        "api_key": "legacy-key",
        "api_base_url": "https://legacy.example.com/v1",
        "embedding_model": "legacy-embed",
        "chat_model": "legacy-chat",
    }
    (settings_dir / "settings.json").write_text(json.dumps(payload))

    manager = SettingsManager(settings_dir=settings_dir)
    settings = manager.load_settings()

    assert settings.embedding_api_key == "legacy-key"
    assert settings.chat_api_key == "legacy-key"
    assert settings.embedding_base_url == "https://legacy.example.com/v1"
    assert settings.chat_base_url == "https://legacy.example.com/v1"
    assert settings.embedding_model == "legacy-embed"
    assert settings.chat_model == "legacy-chat"


def test_chat_key_falls_back_to_legacy_key_when_split_missing(tmp_path):
    manager = SettingsManager(settings_dir=tmp_path)
    manager._settings = AppSettings(api_key="legacy-only")  # type: ignore[assignment]

    assert manager.get_chat_api_key() == "legacy-only"
