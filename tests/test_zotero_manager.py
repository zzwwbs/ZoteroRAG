"""Unit tests for Zotero directory detection."""

from pathlib import Path

from zoterorag.core.services.zotero_manager import ZoteroManager


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
