"""Unit tests for Zotero directory detection and data access."""

import sqlite3
from pathlib import Path

import pytest

from zoterorag.core.services.zotero_manager import (
    ZoteroDatabaseError,
    ZoteroManager,
)


def test_detect_uses_env_var(monkeypatch, tmp_path: Path) -> None:
    candidate = tmp_path / "app"
    candidate.mkdir()
    (candidate / "zotero.sqlite").write_text("")

    monkeypatch.setenv("ZOTERO_DATA_DIR", str(candidate))
    manager = ZoteroManager()
    auto_path = manager.detect_zotero_directory()
    assert auto_path == candidate


def test_detect_checks_default_paths_on_linux(monkeypatch, tmp_path: Path) -> None:
    home_dir = tmp_path / "home"
    append = home_dir / "Documents" / "Zotero"
    append.mkdir(parents=True)
    (append / "zotero.sqlite").write_text("")

    monkeypatch.delenv("ZOTERO_DATA_DIR", raising=False)
    monkeypatch.setattr(
        "zoterorag.core.services.zotero_manager.system",
        lambda: "Linux",
    )
    monkeypatch.setattr(Path, "home", classmethod(lambda cls: home_dir))

    manager = ZoteroManager()
    detected = manager.detect_zotero_directory()
    assert detected == append


def test_get_all_items_returns_expected_data(tmp_path: Path) -> None:
    db_dir = tmp_path / "zotero"
    db_dir.mkdir()
    db_file = db_dir / "zotero.sqlite"

    connection = sqlite3.connect(db_file)
    cursor = connection.cursor()
    cursor.execute("CREATE TABLE items(itemID INTEGER PRIMARY KEY, dateAdded TEXT)")
    cursor.execute("CREATE TABLE creators(creatorID INTEGER PRIMARY KEY, firstName TEXT, lastName TEXT, name TEXT)")
    cursor.execute(
        "CREATE TABLE itemCreators(itemCreatorID INTEGER PRIMARY KEY, itemID INTEGER, creatorID INTEGER)"
    )
    cursor.execute(
        "CREATE TABLE fields(fieldID INTEGER PRIMARY KEY, fieldName TEXT UNIQUE NOT NULL)"
    )
    cursor.execute(
        "CREATE TABLE itemData(itemDataID INTEGER PRIMARY KEY, itemID INTEGER, fieldID INTEGER, valueID INTEGER)"
    )
    cursor.execute(
        "CREATE TABLE itemDataValues(valueID INTEGER PRIMARY KEY, value TEXT)"
    )

    cursor.executemany(
        "INSERT INTO fields(fieldID, fieldName) VALUES (?, ?)",
        [(1, "title"), (2, "date")],
    )
    cursor.execute("INSERT INTO items(itemID, dateAdded) VALUES (1, '2024-01-01')")
    cursor.execute("INSERT INTO itemDataValues(valueID, value) VALUES (1, 'Test Title')")
    cursor.execute("INSERT INTO itemDataValues(valueID, value) VALUES (2, '2022-01-01')")
    cursor.execute(
        "INSERT INTO itemData(itemID, fieldID, valueID) VALUES (1, 1, 1)"
    )
    cursor.execute(
        "INSERT INTO itemData(itemID, fieldID, valueID) VALUES (1, 2, 2)"
    )
    cursor.execute(
        "INSERT INTO creators(creatorID, firstName, lastName, name) VALUES (1, 'Jane', 'Doe', NULL)"
    )
    cursor.execute(
        "INSERT INTO itemCreators(itemID, creatorID) VALUES (1, 1)"
    )
    connection.commit()
    connection.close()

    manager = ZoteroManager(zotero_path=db_dir)
    items = manager.get_all_items()
    assert len(items) == 1
    assert items[0].title == "Test Title"
    assert "Doe" in items[0].authors
    assert items[0].year == "2022"


def test_get_all_items_missing_database_raises(tmp_path: Path) -> None:
    manager = ZoteroManager(zotero_path=tmp_path)
    with pytest.raises(ZoteroDatabaseError):
        manager.get_all_items()


def test_get_pdf_attachments_resolves_storage_paths(tmp_path: Path) -> None:
    db_dir = tmp_path / "zotero"
    storage_dir = db_dir / "storage" / "ABC123"
    storage_dir.mkdir(parents=True)
    pdf_path = storage_dir / "paper.pdf"
    pdf_path.write_text("dummy")

    db_file = db_dir / "zotero.sqlite"
    connection = sqlite3.connect(db_file)
    cursor = connection.cursor()
    
    # Create items table with key field
    cursor.execute(
        "CREATE TABLE items(" \
        "itemID INTEGER PRIMARY KEY, " \
        "key TEXT)"
    )
    cursor.execute(
        "INSERT INTO items(itemID, key) VALUES (2, 'ABC123')"
    )
    
    cursor.execute(
        "CREATE TABLE itemAttachments(" \
        "itemID INTEGER PRIMARY KEY, " \
        "parentItemID INTEGER, " \
        "linkMode INT, " \
        "contentType TEXT, " \
        "path TEXT)"
    )
    cursor.execute(
        "INSERT INTO itemAttachments(itemID, parentItemID, linkMode, contentType, path) "\
        "VALUES (2, 1, 0, 'application/pdf', 'storage:paper.pdf')"
    )
    connection.commit()
    connection.close()

    manager = ZoteroManager(zotero_path=db_dir)
    attachments = manager.get_pdf_attachments(1)
    assert attachments == [pdf_path]
