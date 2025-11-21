"""Integration-flavored tests for MainWindow search wiring."""

from __future__ import annotations

import pytest

pytest.importorskip("PySide6")

from PySide6.QtCore import QThreadPool
from PySide6.QtWidgets import QApplication, QMainWindow

from zoterorag.core.services.search_service import SearchResult, SearchServiceError
from zoterorag.ui.main_window import MainWindow


class FakeSettings:
    def get_zotero_path(self):
        return None

    def set_zotero_path(self, path):  # pragma: no cover - test helper
        self._path = path


class FakeSearchService:
    def __init__(self, should_fail: bool = False) -> None:
        self.should_fail = should_fail
        self.calls: list[str] = []

    def search(self, query: str, *, k: int | None = None) -> SearchResult:
        self.calls.append(query)
        if self.should_fail:
            raise SearchServiceError("Embedding lookup failed")
        return SearchResult(query=query, query_embedding=[0.1, 0.2, 0.3])


class ImmediateThreadPool(QThreadPool):
    def start(self, runnable, priority: int = 0):  # type: ignore[override]
        runnable.run()


@pytest.fixture(scope="module")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app


def test_search_success_updates_status_and_calls_service(qapp):
    service = FakeSearchService()
    window = MainWindow(
        settings_manager=FakeSettings(),
        search_service=service,
        thread_pool=ImmediateThreadPool(),
        auto_start=False,
    )
    assert isinstance(window, QMainWindow)
    window._stack.setCurrentWidget(window._main_container)

    window._search_view._input.setText("deep learning")
    window._search_view._start_button.click()

    assert service.calls == ["deep learning"]
    assert window._search_view.is_busy() is False
    assert "Embedding received" in window._search_view._status_label.text()


def test_search_error_shows_error_message(qapp):
    service = FakeSearchService(should_fail=True)
    window = MainWindow(
        settings_manager=FakeSettings(),
        search_service=service,
        thread_pool=ImmediateThreadPool(),
        auto_start=False,
    )
    window._stack.setCurrentWidget(window._main_container)

    window._search_view._input.setText("fail me")
    window._search_view._start_button.click()

    assert window._search_view.is_busy() is False
    assert "failed" in window._search_view._status_label.text().lower()
    assert window._search_view._error_label.text() == "Embedding lookup failed"
