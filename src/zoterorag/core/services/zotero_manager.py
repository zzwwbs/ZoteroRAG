"""Zotero-specific filesystem helpers."""

from __future__ import annotations

import logging
import os
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from platform import system
from typing import Iterable, List

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ZoteroItem:
    """Lightweight representation of a Zotero library item."""

    item_id: int
    title: str
    authors: str
    year: str


class ZoteroDatabaseError(RuntimeError):
    """Raised when an unrecoverable database issue occurs."""


class ZoteroManager:
    """Manage Zotero directory discovery and read-only data access."""

    def __init__(self, zotero_path: Path | None = None) -> None:
        self._zotero_path = zotero_path

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

    def set_zotero_path(self, path: Path | None) -> None:
        """Store the Zotero directory that will be used for future operations."""

        self._zotero_path = path

    def _get_database_file(self, path: Path | None = None) -> Path | None:
        directory = path or self._zotero_path
        if not directory:
            return None

        db_file = (directory / "zotero.sqlite").expanduser()
        return db_file if db_file.is_file() else None

    def _connect_to_database(self, db_file: Path) -> sqlite3.Connection:
        uri = f"file:{db_file}?mode=ro"
        return sqlite3.connect(uri, uri=True, check_same_thread=False)

    def get_all_items(self) -> List[ZoteroItem]:
        """Return metadata for every Zotero item available in the configured directory."""

        db_file = self._get_database_file()
        if not db_file:
            raise ZoteroDatabaseError("Zotero database not configured or missing.")

        try:
            with self._connect_to_database(db_file) as connection:
                connection.row_factory = sqlite3.Row
                field_ids = self._get_field_ids(connection, ("title", "date"))
                rows = connection.execute(
                    self._item_query(),
                    {
                        "title_field": field_ids.get("title"),
                        "date_field": field_ids.get("date"),
                    },
                ).fetchall()
                return [self._row_to_item(row) for row in rows]
        except sqlite3.OperationalError as error:
            logger.exception("Unable to open Zotero database")
            raise ZoteroDatabaseError(
                f"Failed to open Zotero database: {error}"
            ) from error
        except Exception as error:
            logger.exception("Unexpected error while reading Zotero items")
            raise ZoteroDatabaseError(str(error)) from error

    def _row_to_item(self, row: sqlite3.Row) -> ZoteroItem:
        authors = row["authors"] or "Unknown authors"
        year = row["year"] or ""
        title = row["title"] or "Untitled"
        return ZoteroItem(
            item_id=row["itemID"],
            title=title,
            authors=authors,
            year=year,
        )

    @staticmethod
    def _item_query() -> str:
        return (
            "SELECT items.itemID, "
            "COALESCE(title_values.value, '') AS title, "
            "GROUP_CONCAT("
            "CASE "
            "WHEN creators.lastName IS NOT NULL AND creators.firstName IS NOT NULL THEN creators.lastName || ', ' || creators.firstName "
            "WHEN creators.lastName IS NOT NULL THEN creators.lastName "
            "WHEN creators.firstName IS NOT NULL THEN creators.firstName "
            "ELSE '' "
            "END, '; '"
            ") AS authors, "
            "COALESCE(SUBSTR(date_values.value, 1, 4), '') AS year "
            "FROM items "
            "LEFT JOIN itemData AS title_data ON items.itemID = title_data.itemID AND title_data.fieldID = :title_field "
            "LEFT JOIN itemDataValues AS title_values ON title_data.valueID = title_values.valueID "
            "LEFT JOIN itemData AS date_data ON items.itemID = date_data.itemID AND date_data.fieldID = :date_field "
            "LEFT JOIN itemDataValues AS date_values ON date_data.valueID = date_values.valueID "
            "LEFT JOIN itemCreators ON items.itemID = itemCreators.itemID "
            "LEFT JOIN creators ON itemCreators.creatorID = creators.creatorID "
            "GROUP BY items.itemID "
            "ORDER BY items.dateAdded DESC"
        )

    def _get_field_ids(
        self, connection: sqlite3.Connection, field_names: Iterable[str]
    ) -> dict[str, int]:
        names = tuple(field_names)
        if not names:
            return {}

        placeholders = ",".join("?" for _ in names)
        query = (
            f"SELECT fieldName, fieldID FROM fields "
            f"WHERE fieldName IN ({placeholders})"
        )
        rows = connection.execute(query, names).fetchall()
        return {row["fieldName"]: row["fieldID"] for row in rows}

    def get_pdf_attachments(self, item_id: int) -> list[Path]:
        """Return resolved PDF attachment paths for the provided Zotero item."""

        db_file = self._get_database_file()
        if not db_file:
            raise ZoteroDatabaseError("Zotero database not configured or missing.")

        try:
            with self._connect_to_database(db_file) as connection:
                connection.row_factory = sqlite3.Row
                rows = connection.execute(
                    "SELECT ia.path, i.key "
                    "FROM itemAttachments ia "
                    "JOIN items i ON i.itemID = ia.itemID "
                    "WHERE ia.parentItemID = ? AND ia.path IS NOT NULL "
                    "AND (ia.contentType = 'application/pdf' OR ia.path LIKE '%.pdf%')",
                    (item_id,),
                ).fetchall()
        except sqlite3.OperationalError as error:
            logger.exception("Unable to open Zotero database for attachments")
            raise ZoteroDatabaseError(
                f"Failed to open Zotero database: {error}"
            ) from error

        resolved_paths: list[Path] = []
        for row in rows:
            candidate = self._resolve_attachment_path(row["path"], row["key"])
            if candidate and candidate.exists():
                resolved_paths.append(candidate)

        return resolved_paths

    def _resolve_attachment_path(self, stored_path: str | None, attachment_key: str | None = None) -> Path | None:
        if not stored_path:
            return None

        stored_path = stored_path.strip()
        if stored_path.startswith("storage:"):
            storage_dir = self._get_storage_directory()
            if not storage_dir or not attachment_key:
                return None

            # Extract filename from storage:filename.pdf format
            filename = stored_path.split("storage:", 1)[1].lstrip("/\\")
            # Use attachment key as subdirectory: storage/{key}/{filename}
            return (storage_dir / attachment_key / filename).expanduser()

        return Path(stored_path).expanduser()

    def _get_storage_directory(self) -> Path | None:
        if not self._zotero_path:
            return None

        storage_dir = (self._zotero_path / "storage").expanduser()
        return storage_dir if storage_dir.is_dir() else None
