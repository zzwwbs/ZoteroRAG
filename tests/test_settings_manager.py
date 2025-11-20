"""Unit tests for the SettingsManager persistence helper."""

from pathlib import Path

from zoterorag.config.settings_manager import SettingsManager


def test_settings_manager_persists_path(tmp_path: Path) -> None:
    storage_dir = tmp_path / "config"
    manager = SettingsManager(settings_dir=storage_dir)
    assert manager.get_zotero_path() is None

    candidate_dir = tmp_path / "zotero"
    candidate_dir.mkdir()
    (candidate_dir / "zotero.sqlite").write_text("")

    manager.set_zotero_path(candidate_dir)
    assert manager.get_zotero_path() == candidate_dir

    # Ensure persistence to disk uses the expected JSON structure.
    saved = Path(storage_dir / "settings.json")
    assert saved.exists()
    content = saved.read_text(encoding="utf-8")
    assert str(candidate_dir) in content

    # Removing the underlying directory causes get_zotero_path to return None.
    (candidate_dir / "zotero.sqlite").unlink()
    candidate_dir.rmdir()
    assert manager.get_zotero_path() is None
