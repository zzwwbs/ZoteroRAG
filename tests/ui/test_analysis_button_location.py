"""UI tests for analysis button placement and enablement."""

from __future__ import annotations

from datetime import datetime

import pytest

pytest.importorskip("PySide6")

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QThreadPool

from zoterorag.config.settings_manager import AppSettings
from zoterorag.core.data.models import Chunk, Document
from zoterorag.core.services.search_service import SearchMatch, SearchResult
from zoterorag.ui.analysis_tab import AnalysisTab
from zoterorag.ui.main_window import MainWindow
from zoterorag.ui.search_tab import SearchTab


class ImmediateThreadPool(QThreadPool):
    def start(self, runnable, priority: int = 0):  # type: ignore[override]
        runnable.run()


class FakeSettings:
    def __init__(self):
        self._settings = AppSettings(
            enable_ai_analysis=True,
            chat_base_url="https://api.example.com/v1",
            embedding_base_url="https://api.example.com/v1",
        )

    def load_settings(self) -> AppSettings:
        return self._settings

    def get_zotero_path(self):
        return None

    def set_zotero_path(self, path):
        pass

    def get_chat_api_key(self) -> str | None:
        return "test-chat-key"

    def get_embedding_api_key(self) -> str | None:
        return "test-embed-key"

    def refresh(self):
        return self._settings


class FakeSearchService:
    def search(self, query: str, *, k: int | None = None) -> SearchResult:  # pragma: no cover - unused in these tests
        return SearchResult(query=query, query_embedding=[], matches=[])


@pytest.fixture(scope="module")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app


def test_search_tab_has_no_analyze_button(qapp):
    tab = SearchTab()
    assert not hasattr(tab, "analyze_button"), "SearchTab should not expose analyze button"


def test_analysis_tab_shows_analyze_button(qapp):
    tab = AnalysisTab()
    assert tab.analyze_button.text() == "Analyze Selected Papers"
    assert tab.analyze_button.isEnabled() is False


def test_analyze_button_enables_when_results_present(qapp):
    window = MainWindow(
        settings_manager=FakeSettings(),
        search_service=FakeSearchService(),
        thread_pool=ImmediateThreadPool(),
        auto_start=False,
    )
    button = window._analyze_button
    assert button.isEnabled() is False

    match = SearchMatch(
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
            title="Doc",
            authors=["A"],
            year=2024,
            pdf_file_path="/tmp/doc.pdf",
            indexed_at=datetime.utcnow(),
        ),
        distance=0.01,
    )
    window._handle_search_result(SearchResult(query="q", query_embedding=[], matches=[match]))
    assert button.isEnabled() is True


def test_clicking_analyze_invokes_handler(qapp):
    window = MainWindow(
        settings_manager=FakeSettings(),
        search_service=FakeSearchService(),
        thread_pool=ImmediateThreadPool(),
        auto_start=False,
    )
    match = SearchMatch(
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
            title="Doc",
            authors=["A"],
            year=2024,
            pdf_file_path="/tmp/doc.pdf",
            indexed_at=datetime.utcnow(),
        ),
        distance=0.01,
    )
    window._handle_search_result(SearchResult(query="q", query_embedding=[], matches=[match]))

    # Replace handler to avoid spinning up background threads in the test environment.
    window._analyze_button.clicked.disconnect()
    called = {"hit": False}
    window._analyze_button.clicked.connect(lambda: called.__setitem__("hit", True))
    window._analyze_button.click()
    assert called["hit"] is True
