"""Integration tests for MainWindow startup behavior based on onboarding status."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

import pytest

pytest.importorskip("PySide6")

from PySide6.QtWidgets import QApplication

from zoterorag.config.settings_manager import AppSettings
from zoterorag.ui.main_window import MainWindow


class FakeSettingsManager:
    """Mock SettingsManager for testing."""

    def __init__(self, onboarding_completed: bool = False, zotero_path: Path | None = None):
        self._settings = AppSettings(
            zotero_data_path=str(zotero_path) if zotero_path else None,
            onboarding_completed=onboarding_completed,
        )
        self._keyring_service = "test"

    def load_settings(self) -> AppSettings:
        return self._settings

    def get_zotero_path(self) -> Path | None:
        if self._settings.zotero_data_path:
            return Path(self._settings.zotero_data_path)
        return None

    def set_zotero_path(self, path: Path) -> None:
        self._settings = AppSettings(
            zotero_data_path=str(path),
            onboarding_completed=self._settings.onboarding_completed,
        )

    def save_settings(self, settings: AppSettings) -> None:
        self._settings = settings

    def get_api_key(self) -> str | None:
        return None

    def set_api_key_securely(self, key: str) -> None:
        pass

    def refresh(self) -> None:
        pass


class FakeZoteroManager:
    """Mock ZoteroManager for testing."""

    def __init__(self, valid: bool = True):
        self._valid = valid

    def is_valid_zotero_directory(self, path: Path) -> bool:
        return self._valid

    def detect_zotero_directory(self) -> Path | None:
        return None

    def set_zotero_path(self, path: Path) -> None:
        pass

    def get_all_items(self):
        return []

    def get_collections(self):
        return []


@pytest.fixture(scope="module")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app


def test_shows_onboarding_when_not_completed(qapp):
    """When onboarding_completed is False, MainWindow should show onboarding view."""
    settings_mgr = FakeSettingsManager(onboarding_completed=False)
    zotero_mgr = FakeZoteroManager(valid=True)

    window = MainWindow(
        settings_manager=settings_mgr,
        zotero_manager=zotero_mgr,
        search_service=MagicMock(),
        auto_start=True,
    )

    # Should show onboarding view (index 0 in stack)
    assert window._stack.currentWidget() == window._onboarding_view


def test_shows_main_view_when_onboarding_completed(qapp):
    """When onboarding_completed is True and path is valid, MainWindow should show main view."""
    test_path = Path("/tmp/test_zotero")
    settings_mgr = FakeSettingsManager(onboarding_completed=True, zotero_path=test_path)
    zotero_mgr = FakeZoteroManager(valid=True)

    window = MainWindow(
        settings_manager=settings_mgr,
        zotero_manager=zotero_mgr,
        search_service=MagicMock(),
        auto_start=True,
    )

    # Should show main container (index 1 in stack)
    assert window._stack.currentWidget() == window._main_container


def test_shows_onboarding_when_path_invalid(qapp):
    """Even if onboarding_completed is True, show onboarding if path is invalid."""
    test_path = Path("/tmp/invalid_zotero")
    settings_mgr = FakeSettingsManager(onboarding_completed=True, zotero_path=test_path)
    zotero_mgr = FakeZoteroManager(valid=False)

    window = MainWindow(
        settings_manager=settings_mgr,
        zotero_manager=zotero_mgr,
        search_service=MagicMock(),
        auto_start=True,
    )

    # Should show onboarding view because path is invalid
    assert window._stack.currentWidget() == window._onboarding_view


def test_tab_widget_sets_up_four_tabs(qapp):
    """Main window should initialize four tabs with expected labels."""
    settings_mgr = FakeSettingsManager(onboarding_completed=True, zotero_path=Path("/tmp/ok"))
    zotero_mgr = FakeZoteroManager(valid=True)

    window = MainWindow(
        settings_manager=settings_mgr,
        zotero_manager=zotero_mgr,
        search_service=MagicMock(),
        auto_start=False,
    )

    assert window._main_tabs.count() == 4
    assert [window._main_tabs.tabText(i) for i in range(4)] == [
        "Search",
        "Index",
        "AI Analysis",
        "Settings",
    ]
    assert window._main_tabs.isTabEnabled(window._search_tab_index) is False


def test_search_tab_enables_after_indexing(qapp):
    """Search tab should enable and become active when indexing completes."""
    settings_mgr = FakeSettingsManager(onboarding_completed=True, zotero_path=Path("/tmp/ok"))
    zotero_mgr = FakeZoteroManager(valid=True)

    window = MainWindow(
        settings_manager=settings_mgr,
        zotero_manager=zotero_mgr,
        search_service=MagicMock(),
        auto_start=False,
    )

    window._handle_indexing_progress(
        {"status": "complete", "processed_count": 0, "total_count": 0, "current_item_name": None}
    )

    assert window._main_tabs.isTabEnabled(window._search_tab_index) is True
    assert window._main_tabs.currentWidget() == window.search_tab
