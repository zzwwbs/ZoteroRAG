"""Manage persistence for application settings."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any
import logging

try:
    import keyring  # type: ignore
except ImportError:  # pragma: no cover - optional dependency
    keyring = None  # type: ignore

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class AppSettings:
    """Configuration values stored for the application."""

    zotero_data_path: str | None = None
    api_key: str | None = None  # legacy support only; secure store preferred
    enable_ai_analysis: bool = False
    keyring_service: str = "zoterorag"


class SettingsManager:
    """Helper for reading and writing persistent application settings."""

    def __init__(
        self,
        settings_dir: Path | None = None,
        keyring_service: str = "zoterorag",
    ) -> None:
        self._settings_dir = (settings_dir or Path.home() / ".zotero_rag").expanduser()
        self._settings_dir.mkdir(parents=True, exist_ok=True)
        self._settings_file = self._settings_dir / "settings.json"
        self._settings = self._load_settings()
        self._keyring_service = keyring_service or self._settings.keyring_service

    def load_settings(self) -> AppSettings:
        """Load settings from disk, returning defaults when the file is absent."""

        return self._load_settings()

    def _load_settings(self) -> AppSettings:
        if not self._settings_file.exists():
            return AppSettings()

        try:
            raw = json.loads(self._settings_file.read_text(encoding="utf-8"))
        except ValueError:
            return AppSettings()

        return AppSettings(
            zotero_data_path=raw.get("zotero_data_path"),
            api_key=raw.get("api_key"),
            enable_ai_analysis=bool(raw.get("enable_ai_analysis", False)),
            keyring_service=raw.get("keyring_service", "zoterorag"),
        )

    def save_settings(self, settings: AppSettings) -> None:
        """Persist the provided settings to disk."""
        api_key_to_store = settings.api_key
        if api_key_to_store is None and keyring is None:
            api_key_to_store = self._settings.api_key

        payload: dict[str, Any] = {
            "zotero_data_path": settings.zotero_data_path,
            "api_key": api_key_to_store,
            "enable_ai_analysis": settings.enable_ai_analysis,
            "keyring_service": settings.keyring_service,
        }
        self._settings_file.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        self._settings = settings

    def get_zotero_path(self) -> Path | None:
        """Return the stored Zotero directory path if it still exists."""
        if not self._settings.zotero_data_path:
            return None

        stored = Path(self._settings.zotero_data_path).expanduser()
        return stored if stored.exists() else None

    def set_zotero_path(self, path: Path | str | None) -> None:
        """Update the cached Zotero path and persist it immediately."""
        normalized: str | None = (
            str(Path(path).expanduser()) if path else None
        )
        self.save_settings(
            AppSettings(
                zotero_data_path=normalized,
                api_key=self._settings.api_key,
                enable_ai_analysis=self._settings.enable_ai_analysis,
            )
        )

    def get_api_key(self) -> str | None:
        """Return the stored API key or fallback to environment configuration."""

        if keyring:
            try:
                stored = keyring.get_password(self._keyring_service, "api_key")
                if stored:
                    return stored
            except Exception as error:  # pragma: no cover - backend dependent
                logger.exception("Keyring get_password failed")
                return None

        if self._settings.api_key:
            return self._settings.api_key

        return os.getenv("OPENAI_API_KEY")

    def set_api_key(self, api_key: str | None) -> None:
        """Persist the provided API key."""

        self.save_settings(
            AppSettings(
                zotero_data_path=self._settings.zotero_data_path,
                api_key=api_key,
                enable_ai_analysis=self._settings.enable_ai_analysis,
            )
        )

    def set_api_key_securely(self, api_key: str | None) -> None:
        """Store the API key using the OS keyring when available."""

        if keyring:
            try:
                if api_key:
                    keyring.set_password(self._keyring_service, "api_key", api_key)
                else:
                    keyring.delete_password(self._keyring_service, "api_key")
                # Keep in-memory settings consistent with api_key=None to prevent plaintext leakage
                self._settings = AppSettings(
                    zotero_data_path=self._settings.zotero_data_path,
                    api_key=None,  # Never store plaintext in memory when using keyring
                    enable_ai_analysis=self._settings.enable_ai_analysis,
                    keyring_service=self._keyring_service,
                )
                return
            except Exception as error:
                logger.exception("Keyring set/delete failed")

        # Fallback: store in settings (legacy) if keyring unavailable
        self.set_api_key(api_key)

    def set_enable_ai_analysis(self, enabled: bool) -> None:
        """Toggle AI analysis setting and persist."""
        self.save_settings(
            AppSettings(
                zotero_data_path=self._settings.zotero_data_path,
                api_key=self._settings.api_key,
                enable_ai_analysis=enabled,
                keyring_service=self._keyring_service,
            )
        )

    def refresh(self) -> AppSettings:
        """Reload settings from disk, discarding cached values."""
        self._settings = self.load_settings()
        return self._settings
