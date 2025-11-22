"""Integration-flavored tests for MainWindow search wiring."""

from __future__ import annotations

import pytest

pytest.importorskip("PySide6")

from PySide6.QtCore import QThreadPool
from PySide6.QtWidgets import QApplication, QMainWindow

from zoterorag.core.data.models import Chunk, Document
from zoterorag.core.services.search_service import SearchMatch, SearchResult, SearchServiceError
from zoterorag.ui.main_window import MainWindow
from zoterorag.config.settings_manager import AppSettings
from datetime import datetime


class FakeSettings:
    def get_zotero_path(self):
        return None

    def set_zotero_path(self, path):  # pragma: no cover - test helper
        self._path = path

    def load_settings(self) -> AppSettings:
        """Return default settings for testing."""
        return AppSettings()
    
    def get_api_key(self) -> str | None:
        """Return None for testing (no API key configured)."""
        return None


class FakeSearchService:
    def __init__(self, should_fail: bool = False) -> None:
        self.should_fail = should_fail
        self.calls: list[str] = []

    def search(self, query: str, *, k: int | None = None) -> SearchResult:
        self.calls.append(query)
        if self.should_fail:
            raise SearchServiceError("Embedding lookup failed")
        return SearchResult(
            query=query,
            query_embedding=[0.1, 0.2, 0.3],
            matches=[
                SearchMatch(
                    chunk=Chunk(
                        id=1,
                        document_id=1,
                        content="chunk content",
                        page_number=1,
                        vector_id=5,
                    ),
                    document=Document(
                        id=1,
                        zotero_item_key="abc",
                        title="Doc Title",
                        authors=["Author"],
                        year=2024,
                        pdf_file_path="/tmp/doc.pdf",
                        indexed_at=datetime.utcnow(),
                    ),
                    distance=0.01,
                )
            ],
        )


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
    window._handle_indexing_progress(
        {"status": "complete", "processed_count": 0, "total_count": 0, "current_item_name": None}
    )

    window._search_view._input.setText("deep learning")
    window._search_view._start_button.click()

    assert service.calls == ["deep learning"]
    assert window._search_view.is_busy() is False
    assert "Found" in window._search_view._status_label.text()


def test_search_error_shows_error_message(qapp):
    service = FakeSearchService(should_fail=True)
    window = MainWindow(
        settings_manager=FakeSettings(),
        search_service=service,
        thread_pool=ImmediateThreadPool(),
        auto_start=False,
    )
    window._stack.setCurrentWidget(window._main_container)
    window._handle_indexing_progress(
        {"status": "complete", "processed_count": 0, "total_count": 0, "current_item_name": None}
    )

    window._search_view._input.setText("fail me")
    window._search_view._start_button.click()

    assert window._search_view.is_busy() is False
    assert "failed" in window._search_view._status_label.text().lower()
    assert window._search_view._error_label.text() == "Embedding lookup failed"
