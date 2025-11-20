"""Zotero-specific filesystem helpers."""

from __future__ import annotations

import os
from pathlib import Path
from platform import system


class ZoteroManager:
    """Manage Zotero directory discovery logic."""

    def detect_zotero_directory(self) -> Path | None:
        """Return a detected Zotero directory or None when detection fails."""

        env_path = os.getenv("ZOTERO_DATA_DIR")
        if env_path:
            candidate = Path(env_path).expanduser()
            if self.is_valid_zotero_directory(candidate):
                return candidate

        for candidate in self._candidate_paths():
            if self.is_valid_zotero_directory(candidate):
                return candidate

        return None

    def _candidate_paths(self) -> list[Path]:
        """Return default directories to probe based on the current platform."""

        home = Path.home()
        paths: list[Path] = [
            home / "Zotero",
            home / "Documents" / "Zotero",
        ]

        if system() == "Windows":
            appdata = os.getenv("APPDATA")
            if appdata:
                paths.append(Path(appdata) / "Zotero")

        return paths

    @staticmethod
    def is_valid_zotero_directory(candidate: Path) -> bool:
        """Ensure the directory contains the expected Zotero sqlite payload."""

        return (candidate / "zotero.sqlite").is_file()
