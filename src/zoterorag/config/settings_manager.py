"""Manage persistence for application settings."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class AppSettings:
    """Configuration values stored for the application."""

    zotero_data_path: str | None = None


class SettingsManager:
    """Helper for reading and writing persistent application settings."""

    def __init__(self, settings_dir: Path | None = None) -> None:
        self._settings_dir = (settings_dir or Path.home() / ".zotero_rag").expanduser()
        self._settings_dir.mkdir(parents=True, exist_ok=True)
        self._settings_file = self._settings_dir / "settings.json"
        self._settings = self._load_settings()

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

        return AppSettings(zotero_data_path=raw.get("zotero_data_path"))

    def save_settings(self, settings: AppSettings) -> None:
        """Persist the provided settings to disk."""
        payload: dict[str, Any] = {"zotero_data_path": settings.zotero_data_path}
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
        self.save_settings(AppSettings(zotero_data_path=normalized))

    def refresh(self) -> AppSettings:
        """Reload settings from disk, discarding cached values."""
        self._settings = self.load_settings()
        return self._settings
