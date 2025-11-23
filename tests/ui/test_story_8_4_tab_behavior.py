"""Tests for Story 8.4: Remove Auto-Tab-Switch & Default to Search Tab."""

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
            embedding_base_url="https://api.example.com/v1",
            chat_base_url="https://api.example.com/v1",
        )

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

    def get_embedding_api_key(self) -> str | None:
        return None

    def get_chat_api_key(self) -> str | None:
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

    def get_total_paper_count(self) -> int:
        return 0

    def get_collection_paper_counts(self) -> dict:
        return {}


@pytest.fixture(scope="module")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app


def test_default_tab_is_search_on_startup(qapp):
    """AC2: Application opens to the Search tab on launch."""
    test_path = Path("/tmp/test_zotero")
    settings_mgr = FakeSettingsManager(onboarding_completed=True, zotero_path=test_path)
    zotero_mgr = FakeZoteroManager(valid=True)

    window = MainWindow(
        settings_manager=settings_mgr,
        zotero_manager=zotero_mgr,
        search_service=MagicMock(),
        auto_start=True,
    )

    # Should show main container and default to Search tab
    assert window._stack.currentWidget() == window._main_container
    assert window._main_tabs.currentWidget() == window.search_tab


def test_no_auto_switch_after_indexing_completes(qapp):
    """AC1: After indexing completes, user remains on Index tab (no auto-switch)."""
    test_path = Path("/tmp/test_zotero")
    settings_mgr = FakeSettingsManager(onboarding_completed=True, zotero_path=test_path)
    zotero_mgr = FakeZoteroManager(valid=True)

    window = MainWindow(
        settings_manager=settings_mgr,
        zotero_manager=zotero_mgr,
        search_service=MagicMock(),
        auto_start=True,
    )

    # Manually switch to Index tab (simulating user action)
    window._main_tabs.setCurrentWidget(window.index_tab)
    assert window._main_tabs.currentWidget() == window.index_tab

    # Simulate indexing completion
    window._handle_indexing_progress(
        {"status": "complete", "processed_count": 5, "total_count": 5, "current_item_name": None}
    )

    # AC1: Should remain on Index tab (no automatic switch to Search)
    assert window._main_tabs.currentWidget() == window.index_tab
    # Search tab should be enabled but not automatically switched to
    assert window._main_tabs.isTabEnabled(window._search_tab_index) is True


def test_state_consistency_during_indexing(qapp):
    """AC4: Active tab state preserved if user switches during indexing."""
    test_path = Path("/tmp/test_zotero")
    settings_mgr = FakeSettingsManager(onboarding_completed=True, zotero_path=test_path)
    zotero_mgr = FakeZoteroManager(valid=True)

    window = MainWindow(
        settings_manager=settings_mgr,
        zotero_manager=zotero_mgr,
        search_service=MagicMock(),
        auto_start=True,
    )

    # Start on Index tab
    window._main_tabs.setCurrentWidget(window.index_tab)

    # Simulate indexing in progress
    window._handle_indexing_progress(
        {"status": "processing", "processed_count": 2, "total_count": 5, "current_item_name": "Paper 2"}
    )

    # User manually switches to Settings tab during indexing
    window._main_tabs.setCurrentWidget(window.settings_tab)
    assert window._main_tabs.currentWidget() == window.settings_tab

    # Indexing completes
    window._handle_indexing_progress(
        {"status": "complete", "processed_count": 5, "total_count": 5, "current_item_name": None}
    )

    # AC4: Should still be on Settings tab (user's choice preserved)
    assert window._main_tabs.currentWidget() == window.settings_tab


def test_manual_tab_switching_preserved(qapp):
    """AC3: User can switch tabs at any time - functionality works normally."""
    test_path = Path("/tmp/test_zotero")
    settings_mgr = FakeSettingsManager(onboarding_completed=True, zotero_path=test_path)
    zotero_mgr = FakeZoteroManager(valid=True)

    window = MainWindow(
        settings_manager=settings_mgr,
        zotero_manager=zotero_mgr,
        search_service=MagicMock(),
        auto_start=True,
    )

    # Start on Search tab (default)
    assert window._main_tabs.currentWidget() == window.search_tab

    # Manual switch to Index tab
    window._main_tabs.setCurrentWidget(window.index_tab)
    assert window._main_tabs.currentWidget() == window.index_tab

    # Manual switch to AI Analysis tab
    window._main_tabs.setCurrentWidget(window.analysis_tab)
    assert window._main_tabs.currentWidget() == window.analysis_tab

    # Manual switch to Settings tab
    window._main_tabs.setCurrentWidget(window.settings_tab)
    assert window._main_tabs.currentWidget() == window.settings_tab

    # Manual switch back to Search tab
    window._main_tabs.setCurrentWidget(window.search_tab)
    assert window._main_tabs.currentWidget() == window.search_tab
