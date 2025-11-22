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

    # New split configuration
    embedding_provider: str = "openai"
    embedding_api_key: str | None = None
    embedding_base_url: str = "https://api.openai.com/v1"
    embedding_model: str = "text-embedding-ada-002"

    chat_provider: str = "openai"
    chat_api_key: str | None = None
    chat_base_url: str = "https://api.openai.com/v1"
    chat_model: str = "gpt-4o-mini"

    # Legacy (deprecated) single-provider fields retained for migration/back-compat
    api_provider: str | None = None
    api_model: str | None = None
    api_key: str | None = None  # legacy support only; secure store preferred
    api_base_url: str = "https://api.openai.com/v1"

    enable_ai_analysis: bool = False
    chunk_size: int = 600
    chunk_overlap: int = 100
    default_search_results: int = 10
    theme: str = "auto"
    keyring_service: str = "zoterorag"
    onboarding_completed: bool = False


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

        # Migrate legacy API fields into split embedding/chat config when missing.
        default_base = "https://api.openai.com/v1"
        legacy_api_key = raw.get("api_key")
        legacy_base_url = raw.get("api_base_url") or raw.get("base_url") or default_base
        legacy_provider = raw.get("api_provider") or "openai"
        legacy_model = raw.get("api_model")

        embedding_api_key = raw.get("embedding_api_key") or legacy_api_key
        chat_api_key = raw.get("chat_api_key") or legacy_api_key

        embedding_base_url = raw.get("embedding_base_url") or legacy_base_url
        chat_base_url = raw.get("chat_base_url") or legacy_base_url

        embedding_provider = raw.get("embedding_provider") or legacy_provider
        chat_provider = raw.get("chat_provider") or legacy_provider

        migrated = any(
            key not in raw
            for key in ("embedding_api_key", "chat_api_key", "embedding_base_url", "chat_base_url")
        )
        if migrated:
            logger.info("Migrated legacy API settings into split embedding/chat configuration.")

        return AppSettings(
            zotero_data_path=raw.get("zotero_data_path"),
            embedding_provider=embedding_provider,
            embedding_api_key=embedding_api_key,
            embedding_base_url=embedding_base_url,
            embedding_model=raw.get("embedding_model", "text-embedding-ada-002"),
            chat_provider=chat_provider,
            chat_api_key=chat_api_key,
            chat_base_url=chat_base_url,
            chat_model=raw.get("chat_model", "gpt-4o-mini"),
            api_provider=legacy_provider,
            api_model=legacy_model,
            api_key=legacy_api_key,
            api_base_url=legacy_base_url,
            enable_ai_analysis=bool(raw.get("enable_ai_analysis", False)),
            chunk_size=int(raw.get("chunk_size", 600)),
            chunk_overlap=int(raw.get("chunk_overlap", 100)),
            default_search_results=int(raw.get("default_search_results", 10)),
            theme=raw.get("theme", "auto"),
            keyring_service=raw.get("keyring_service", "zoterorag"),
            onboarding_completed=bool(raw.get("onboarding_completed", False)),
        )

    def save_settings(self, settings: AppSettings) -> None:
        """Persist the provided settings to disk."""
        # Preserve legacy api_key for backward compatibility, but prefer storing securely per-scope.
        legacy_api_key = settings.api_key
        if legacy_api_key is None and keyring is None:
            legacy_api_key = self._settings.api_key

        payload: dict[str, Any] = {
            "zotero_data_path": settings.zotero_data_path,
            # Split configuration
            "embedding_provider": settings.embedding_provider,
            "embedding_api_key": settings.embedding_api_key,
            "embedding_base_url": settings.embedding_base_url,
            "embedding_model": settings.embedding_model,
            "chat_provider": settings.chat_provider,
            "chat_api_key": settings.chat_api_key,
            "chat_base_url": settings.chat_base_url,
            "chat_model": settings.chat_model,
            # Legacy (deprecated)
            "api_provider": settings.api_provider,
            "api_model": settings.api_model,
            "api_key": legacy_api_key,
            "api_base_url": settings.api_base_url,
            # General app settings
            "enable_ai_analysis": settings.enable_ai_analysis,
            "chunk_size": settings.chunk_size,
            "chunk_overlap": settings.chunk_overlap,
            "default_search_results": settings.default_search_results,
            "theme": settings.theme,
            "keyring_service": settings.keyring_service,
            "onboarding_completed": settings.onboarding_completed,
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
        self.save_settings(self._current_settings(zotero_data_path=normalized))

    def _get_key_from_keyring(self, name: str) -> str | None:
        if not keyring:
            return None
        try:
            stored = keyring.get_password(self._keyring_service, name)
            if stored:
                return stored
        except Exception as error:  # pragma: no cover - backend dependent
            logger.exception("Keyring get_password failed for %s", name)
        return None

    def _set_key_in_keyring(self, name: str, api_key: str | None) -> None:
        if not keyring:
            return
        try:
            if api_key:
                keyring.set_password(self._keyring_service, name, api_key)
            else:
                keyring.delete_password(self._keyring_service, name)
        except Exception as error:
            logger.exception("Keyring set/delete failed for %s", name)

    def get_api_key(self) -> str | None:
        """Return the legacy API key (deprecated) or fallback to environment configuration."""

        stored = self._get_key_from_keyring("api_key")
        if stored:
            return stored

        if self._settings.api_key:
            return self._settings.api_key

        return os.getenv("OPENAI_API_KEY")

    def get_embedding_api_key(self) -> str | None:
        """Return the embedding API key with fallback to legacy key."""

        stored = self._get_key_from_keyring("embedding_api_key")
        if stored:
            return stored
        if self._settings.embedding_api_key:
            return self._settings.embedding_api_key
        # Fallback to legacy
        return self.get_api_key()

    def get_chat_api_key(self) -> str | None:
        """Return the chat API key with fallback to legacy key."""

        stored = self._get_key_from_keyring("chat_api_key")
        if stored:
            return stored
        if self._settings.chat_api_key:
            return self._settings.chat_api_key
        # Fallback to legacy
        return self.get_api_key()

    def set_api_key(self, api_key: str | None) -> None:
        """Persist the legacy API key (deprecated)."""

        self.save_settings(self._current_settings(api_key=api_key))

    def set_api_key_securely(self, api_key: str | None) -> None:
        """Store the legacy API key using the OS keyring when available."""

        if keyring:
            self._set_key_in_keyring("api_key", api_key)
            # Keep in-memory settings consistent with api_key=None to prevent plaintext leakage
            self._settings = self._current_settings(api_key=None)
            return

        # Fallback: store in settings (legacy) if keyring unavailable
        self.set_api_key(api_key)

    def set_embedding_api_key_securely(self, api_key: str | None) -> None:
        """Store the embedding API key using the OS keyring when available."""

        if keyring:
            self._set_key_in_keyring("embedding_api_key", api_key)
            self._settings = self._current_settings(embedding_api_key=None)
            return

        self.save_settings(self._current_settings(embedding_api_key=api_key))

    def set_chat_api_key_securely(self, api_key: str | None) -> None:
        """Store the chat API key using the OS keyring when available."""

        if keyring:
            self._set_key_in_keyring("chat_api_key", api_key)
            self._settings = self._current_settings(chat_api_key=None)
            return

        self.save_settings(self._current_settings(chat_api_key=api_key))

    def supports_secure_storage(self) -> bool:
        """Return True when keyring-backed secure storage is available."""

        return keyring is not None

    def set_enable_ai_analysis(self, enabled: bool) -> None:
        """Toggle AI analysis setting and persist."""
        self.save_settings(self._current_settings(enable_ai_analysis=enabled))

    def refresh(self) -> AppSettings:
        """Reload settings from disk, discarding cached values."""
        self._settings = self.load_settings()
        return self._settings

    def _current_settings(self, **overrides: Any) -> AppSettings:
        """Return a copy of current settings with overrides."""
        data = {
            "zotero_data_path": self._settings.zotero_data_path,
            "embedding_provider": self._settings.embedding_provider,
            "embedding_api_key": self._settings.embedding_api_key,
            "embedding_base_url": self._settings.embedding_base_url,
            "embedding_model": self._settings.embedding_model,
            "chat_provider": self._settings.chat_provider,
            "chat_api_key": self._settings.chat_api_key,
            "chat_base_url": self._settings.chat_base_url,
            "chat_model": self._settings.chat_model,
            "api_provider": self._settings.api_provider,
            "api_model": self._settings.api_model,
            "api_key": self._settings.api_key,
            "enable_ai_analysis": self._settings.enable_ai_analysis,
            "api_base_url": self._settings.api_base_url,
            "chunk_size": self._settings.chunk_size,
            "chunk_overlap": self._settings.chunk_overlap,
            "default_search_results": self._settings.default_search_results,
            "theme": self._settings.theme,
            "keyring_service": self._settings.keyring_service,
            "onboarding_completed": self._settings.onboarding_completed,
        }
        data.update(overrides)
        return AppSettings(**data)
