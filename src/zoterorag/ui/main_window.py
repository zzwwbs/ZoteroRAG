"""Main window implementation for the Zotero RAG desktop application."""

from __future__ import annotations

import os
import subprocess
import sys
import logging
import shutil
from pathlib import Path
from datetime import datetime

from PySide6.QtCore import QObject, QRunnable, QThreadPool, Signal
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QMessageBox,
    QMainWindow,
    QApplication,
    QStackedWidget,
    QVBoxLayout,
    QTabWidget,
    QFileDialog,
    QLabel,
    QWidget,
)

from ..config.settings_manager import SettingsManager
from ..config.settings_manager import AppSettings
from ..core.services.embedding_client import EmbeddingClient
from ..core.services.indexing_service import IndexingService
from ..core.services.metadata_db_manager import MetadataDBManager
from ..core.services.search_service import (
    SearchMatch,
    SearchResult,
    SearchService,
    SearchServiceError,
)
from ..core.services.ai_service import AIService, AIServiceError, UnauthorizedAIServiceError
from ..core.services.vector_db_manager import VectorDBManager
from ..core.services.zotero_manager import (
    ZoteroDatabaseError,
    ZoteroManager,
)
from .onboarding_view import OnboardingView
from .settings_dialog import SettingsDialog
from .analysis_tab import AnalysisTab
from .chat_worker import ChatRunnable
from .index_tab import IndexTab
from .search_tab import SearchTab
from .settings_tab import SettingsTab
from .state import AppState

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """Primary shell window with setup detection and onboarding."""

    token_usage_recorded = Signal(object)

    def __init__(
        self,
        settings_manager: SettingsManager | None = None,
        zotero_manager: ZoteroManager | None = None,
        search_service: SearchService | None = None,
        thread_pool: QThreadPool | None = None,
        auto_start: bool = True,
    ) -> None:
        super().__init__()
        self.setWindowTitle("Zotero RAG")
        self.resize(1024, 768)

        self._settings_manager = settings_manager or SettingsManager()
        initial_settings = self._settings_manager.load_settings()
        self._zotero_manager = zotero_manager or ZoteroManager()
        self._thread_pool = thread_pool or QThreadPool.globalInstance()
        self._metadata_manager = MetadataDBManager()
        self._vector_manager = VectorDBManager(dimension=1536)
        self._embedding_client = EmbeddingClient(
            self._settings_manager,
            base_url=initial_settings.embedding_base_url,
            model=initial_settings.embedding_model,
        )
        self._ai_service = AIService(
            self._settings_manager,
            base_url=initial_settings.chat_base_url,
            model=initial_settings.chat_model,
            metadata_manager=self._metadata_manager,
        )
        self._search_service_provided = search_service is not None
        self._search_service = search_service or SearchService(
            self._embedding_client,
            self._vector_manager,
            self._metadata_manager,
        )
        self._indexing_service = IndexingService(
            self._zotero_manager,
            metadata_manager=self._metadata_manager,
            vector_manager=self._vector_manager,
            embedding_client=self._embedding_client,
        )
        self._state = AppState()
        self._cancel_requested = False

        self._stack = QStackedWidget()
        self.setCentralWidget(self._stack)
        self._token_status = QLabel("Tokens: 0")
        self._session_token_total = 0
        self._session_embedding_tokens = 0
        self._session_analysis_tokens = 0
        self._session_embedding_prompt = 0
        self._session_analysis_prompt = 0
        self._session_analysis_completion = 0
        self._session_embedding_model: str | None = None
        self._session_analysis_model: str | None = None
        self.statusBar().addPermanentWidget(self._token_status)

        self._onboarding_view = OnboardingView(self._zotero_manager)
        self._onboarding_view.done.connect(self._handle_onboarding_complete)

        self.search_tab = SearchTab()
        self._search_view = self.search_tab.search_view
        self._search_view.search_triggered.connect(self._on_search)
        self._search_view.copy_to_chatgpt_requested.connect(self._handle_copy_to_chatgpt)
        self._search_view.export_pdfs_requested.connect(self._handle_export_pdfs)

        self._paper_list_view = self.search_tab.paper_list_view
        self._paper_list_view.paper_selected.connect(self._on_paper_selected)
        self._paper_list_view.clear_filter_requested.connect(self._clear_selection)
        self._paper_list_view.open_pdf_requested.connect(self._open_pdf_for_document)

        self._chunk_list_view = self.search_tab.chunk_list_view
        self._chunk_list_view.open_pdf_requested.connect(self._open_pdf_for_document)

        self._chunk_count = self.search_tab.chunk_count

        self.index_tab = IndexTab()
        self._library_view = self.index_tab.library_view
        self._indexing_scope_view = self.index_tab.indexing_scope_view
        self.index_tab.start_indexing.connect(self._start_indexing_task)
        self.index_tab.cancel_indexing.connect(self._cancel_indexing_task)

        self.analysis_tab = AnalysisTab()
        self._analysis_loading = self.analysis_tab.loading_label
        self._chat_view = self.analysis_tab.chat_view
        self._chat_input = self.analysis_tab.chat_input
        self._chat_send_button = self.analysis_tab.send_button
        self._analyze_button = self.analysis_tab.analyze_button
        self._analyze_button.clicked.connect(self._handle_analyze_clicked)
        self._chat_send_button.clicked.connect(self._handle_send_message)

        self.settings_tab = SettingsTab(self._settings_manager, self._open_settings_dialog)

        self._main_tabs = QTabWidget()
        self._main_tabs.addTab(self.search_tab, "Search")
        self._main_tabs.addTab(self.index_tab, "Index")
        self._main_tabs.addTab(self.analysis_tab, "AI Analysis")
        self._main_tabs.addTab(self.settings_tab, "Settings")
        self._search_tab_index = self._main_tabs.indexOf(self.search_tab)
        self._set_search_tab_enabled(False)
        self._main_tabs.setCurrentWidget(self.index_tab)

        self._main_container = QWidget()
        main_layout = QVBoxLayout(self._main_container)
        main_layout.addWidget(self._main_tabs)

        self._stack.addWidget(self._onboarding_view)
        self._stack.addWidget(self._main_container)

        self._setup_menu_bar()
        self._has_search_selection = False
        self.search_tab.selection_changed.connect(self._handle_selection_changed)
        self.token_usage_recorded.connect(self._handle_token_usage)
        if auto_start:
            self._determine_initial_view()
        self._load_state_from_settings()

    def _determine_initial_view(self) -> None:
        saved_path = self._settings_manager.get_zotero_path()
        onboarding_done = getattr(self._settings_manager.load_settings(), "onboarding_completed", False)

        if saved_path and self._zotero_manager.is_valid_zotero_directory(saved_path) and onboarding_done:
            self._show_main_view(saved_path)
            return

        self._show_onboarding_view()

    def _show_main_view(self, zotero_path: Path | None = None) -> None:
        self._stack.setCurrentWidget(self._main_container)
        self._main_tabs.setCurrentWidget(self.index_tab)
        self._refresh_library(zotero_path or self._settings_manager.get_zotero_path())

    def _show_onboarding_view(self) -> None:
        self._stack.setCurrentWidget(self._onboarding_view)
        self._onboarding_view.start_detection()

    def _refresh_library(self, zotero_path: Path | None) -> None:
        if not zotero_path:
            self._library_view.show_error(
                "Zotero directory not configured. Please restart and select it."
            )
            return

        self._zotero_manager.set_zotero_path(zotero_path)
        try:
            items = self._zotero_manager.get_all_items()
            status_map: dict[str, str] = {}
            try:
                keys = [it.item_key for it in items]
                status_map = self._metadata_manager.document_repository.get_status_by_keys(keys)
            except Exception:
                logger.exception("Failed to load document statuses")
            self._library_view.set_items(items, status_map)
            collections = self._zotero_manager.get_collections()
            total_papers = self._zotero_manager.get_total_paper_count()
            collection_counts = self._zotero_manager.get_collection_paper_counts()
            self._indexing_scope_view.set_total_paper_count(total_papers)
            self._indexing_scope_view.set_collections(collections, collection_counts)
            self._maybe_enable_search_from_existing_index()
        except ZoteroDatabaseError as error:
            self._library_view.show_error(str(error))

    def _handle_onboarding_complete(self, path: str | None) -> None:
        actual_path = Path(path) if path else None
        # Load current settings first to ensure we have latest values
        current_settings = self._settings_manager.load_settings()
        # Save all settings including the new zotero path and onboarding completion flag
        self._settings_manager.save_settings(
            self._settings_manager._current_settings(
                zotero_data_path=str(actual_path) if actual_path else None,
                onboarding_completed=True,
            )
        )
        self._show_main_view(actual_path)
        self._show_first_run_visual_cues()
        QMessageBox.information(
            self,
            "Getting Started",
            "Onboarding completed. Use 'Start Indexing' to build your index, or search once indexing is ready.",
        )

    def _show_first_run_visual_cues(self) -> None:
        """Add helpful tooltips to key UI elements for first-time users."""
        
        # Add tooltip to search bar input
        self._search_view._input.setToolTip(
            "💡 Enter your search query here to find relevant papers using semantic search.\n"
            "Example: 'machine learning applications in healthcare'"
        )
        
        # Add tooltip to search button
        self._search_view._start_button.setToolTip(
            "🔍 Click to perform semantic search on your indexed papers"
        )
        
        # Add tooltip to Start Indexing button
        self._indexing_scope_view._start_button.setToolTip(
            "👉 Click here to start indexing your Zotero library.\n"
            "This creates embeddings for semantic search. You can index all papers or specific collections."
        )
        
        # Add tooltip to library view
        self._library_view.setToolTip(
            "📚 Your Zotero library will appear here after indexing.\n"
            "Browse your papers and collections."
        )
        
        # Add tooltip to indexing scope options
        self._indexing_scope_view._entire_radio.setToolTip(
            "Index all papers in your Zotero library"
        )
        self._indexing_scope_view._collection_radio.setToolTip(
            "Index only papers in a specific collection"
        )

    def _setup_menu_bar(self) -> None:
        """Create the basic menu that includes the About dialog."""

        file_menu = self.menuBar().addMenu("&File")
        about_action = QAction("About Zotero RAG", self)
        about_action.triggered.connect(self._show_about_dialog)
        file_menu.addAction(about_action)

        settings_action = QAction("Settings", self)
        settings_action.triggered.connect(self._open_settings_dialog)
        file_menu.addAction(settings_action)

    def _show_about_dialog(self) -> None:
        """Present an informational dialog describing the application."""

        QMessageBox.about(
            self,
            "About Zotero RAG",
            "Zotero RAG is a PySide6 desktop shell for exploring Zotero references with embedded AI.",
        )

    def _start_indexing_task(self, scope: dict) -> None:
        self._set_search_tab_enabled(False)
        self._cancel_requested = False
        self.index_tab.show_indexing_active()
        worker = _IndexingRunnable(self._indexing_service, scope)
        worker.signals.progress.connect(self._handle_indexing_progress)
        worker.signals.finished.connect(self._handle_indexing_finished)
        worker.signals.token_usage.connect(self.token_usage_recorded.emit)
        self._indexing_scope_view.set_busy(True)
        self._thread_pool.start(worker)

    def _cancel_indexing_task(self) -> None:
        self._indexing_service.cancel_indexing()
        self._cancel_requested = True
        self.index_tab.show_cancelling()
        self._indexing_scope_view.set_status_message("Cancelling...")

    def _handle_indexing_progress(self, payload: dict) -> None:
        self._indexing_scope_view.update_progress(payload)
        status = payload.get("status")
        if status == "complete":
            self._set_search_tab_enabled(True)
            self._main_tabs.setCurrentWidget(self.search_tab)
            self._cancel_requested = False
        elif status == "processing" and not self._cancel_requested:
            self.index_tab.show_indexing_active()
        elif status in {"cancelled", "error"}:
            self._cancel_requested = False
            self.index_tab.show_idle()

    def _handle_indexing_finished(self) -> None:
        self._cancel_requested = False
        self._indexing_scope_view.set_busy(False)
        self.index_tab.show_idle()

    def _on_search(self, query: str, count: int) -> None:
        worker = _SearchRunnable(self._search_service, query, count)
        worker.signals.result.connect(self._handle_search_result)
        worker.signals.error.connect(self._handle_search_error)
        worker.signals.finished.connect(self._handle_search_finished)
        worker.signals.usage.connect(self.token_usage_recorded.emit)
        self._search_view.clear_messages()
        self._search_view.set_busy(True)
        self._search_view.set_status("Searching...")
        self._thread_pool.start(worker)

    def _handle_search_result(self, result: SearchResult) -> None:
        self._state.search_matches = result.matches or []
        self._state.selected_paper = None
        self._state.current_query = result.query
        self._has_search_selection = False
        self._chat_view.clear_messages()
        self._refresh_results_views()
        match_count = len(self._state.search_matches)
        self._search_view.set_status(
            f"Found {match_count} results (embedding {len(result.query_embedding)} dims)."
        )
        self._update_analysis_controls()

    def _handle_search_error(self, message: str) -> None:
        self._search_view.set_error(message)
        self._search_view.set_status("Search failed.")

    def _handle_search_finished(self) -> None:
        self._search_view.set_busy(False)
        self._update_analysis_controls()

    def _handle_analyze_clicked(self) -> None:
        if not self._state.search_matches:
            self._chat_view.add_message("Error", "No results to analyze.", role="error", is_error=True)
            return
        if not self._state.current_query:
            self._chat_view.add_message("Error", "No query available to analyze.", role="error", is_error=True)
            return
        self.analysis_tab.reset_conversation()
        top_n = self._chunk_count.value()
        worker = _AIAnalyzeRunnable(
            self._ai_service,
            self._state.current_query,
            self._state.search_matches,
            top_n,
        )
        worker.signals.result.connect(self._handle_analysis_result)
        worker.signals.error.connect(self._handle_analysis_error)
        worker.signals.finished.connect(self._handle_analysis_finished)
        worker.signals.usage.connect(self._handle_token_usage)
        self._set_analysis_busy(True)
        self._analysis_loading.setVisible(True)
        self._analysis_loading.setText("Analyzing with AI...")
        self._thread_pool.start(worker)

    def _handle_copy_to_chatgpt(self) -> None:
        if not self._state.search_matches:
            QMessageBox.information(self, "Copy to ChatGPT", "No search results to export.")
            return
        prompt = format_chatgpt_prompt(
            self._state.current_query,
            self._state.search_matches,
            limit=self._chunk_count.value(),
            selected_document_id=self._state.selected_paper.id if self._state.selected_paper else None,
        )
        QApplication.clipboard().setText(prompt)
        QMessageBox.information(self, "Copy to ChatGPT", "Prompt copied to clipboard.")

    def _handle_analysis_result(self, text: str) -> None:
        self.analysis_tab.add_assistant_message(text)

    def _handle_analysis_error(self, message: str) -> None:
        self.analysis_tab.add_error_message(f"Analysis failed: {message}")

    def _handle_analysis_finished(self) -> None:
        self._set_analysis_busy(False)
        self._analysis_loading.setVisible(False)

    def _handle_send_message(self) -> None:
        if bool(self._analyze_button.property("busy")):
            return
        text = self._chat_input.toPlainText().strip()
        if not text:
            self.analysis_tab.add_error_message("Enter a question to send.")
            return
        if not self._state.search_matches:
            self.analysis_tab.add_error_message("Run a search and select results before chatting.")
            return

        self.analysis_tab.add_user_message(text)
        self._chat_input.clear()
        messages = self._build_chat_messages()
        worker = ChatRunnable(self._ai_service, messages)
        worker.signals.result.connect(self._handle_analysis_result)
        worker.signals.error.connect(self._handle_analysis_error)
        worker.signals.finished.connect(self._handle_analysis_finished)
        worker.signals.usage.connect(self._handle_token_usage)
        self._set_analysis_busy(True)
        self._analysis_loading.setVisible(True)
        self._analysis_loading.setText("Sending...")
        self._thread_pool.start(worker)

    def _build_chat_messages(self) -> list[dict]:
        """Construct chat history with system prompt and limited context."""
        system_message = {
            "role": "system",
            "content": (
                "You are a research assistant helping summarize and discuss academic papers. "
                "Keep answers concise and cite specifics when possible."
            ),
        }
        history = self.analysis_tab.get_history()

        messages: list[dict] = [system_message]

        if self.analysis_tab.include_context_checkbox.isChecked() and self._state.search_matches:
            limit = self.analysis_tab.chunk_spinbox.value()
            context_lines: list[str] = []
            for idx, match in enumerate(self._state.search_matches[:limit], start=1):
                doc = match.document
                title = doc.title if doc else "Unknown title"
                authors = ", ".join(doc.authors) if doc and doc.authors else "Unknown authors"
                snippet = match.chunk.content.replace("\n", " ").strip()
                context_lines.append(
                    f"{idx}. {title} ({authors}) - Page {match.chunk.page_number}: {snippet}"
                )
            context_block = "Context from search results:\n" + "\n".join(context_lines)
            messages.append({"role": "system", "content": context_block})

        messages.extend(history)
        return messages

    def _set_analysis_busy(self, busy: bool) -> None:
        self._analyze_button.setProperty("busy", busy)
        self._update_analysis_controls()

    def _handle_export_pdfs(self) -> None:
        if not self._state.search_matches:
            QMessageBox.information(self, "Export PDFs", "No search results to export.")
            return

        destination = QFileDialog.getExistingDirectory(self, "Select Destination Folder")
        if not destination:
            return

        worker = _ExportPdfRunnable(destination, self._state.search_matches, self._state.selected_paper)
        worker.signals.success.connect(self._handle_export_success)
        worker.signals.error.connect(self._handle_export_error)
        self._thread_pool.start(worker)

    def _handle_export_success(self, folder: str) -> None:
        QMessageBox.information(self, "Export PDFs", f"Exported PDFs to: {folder}")

    def _handle_export_error(self, message: str) -> None:
        QMessageBox.critical(self, "Export PDFs", message)
    def _refresh_results_views(self) -> None:
        """Update paper and chunk lists from current state."""
        documents: list = []
        seen: set[int] = set()
        for match in self._state.search_matches:
            doc = match.document
            if doc and doc.id is not None and doc.id not in seen:
                seen.add(doc.id)
                documents.append(doc)

        self._paper_list_view.set_papers(documents)
        self._chunk_list_view.update_chunks(
            self._state.search_matches,
            selected_document_id=self._state.selected_paper.id if self._state.selected_paper else None,
        )
        self._update_analysis_controls()

    def _on_paper_selected(self, document) -> None:
        if document is None:
            return
        self._state.selected_paper = document
        self._has_search_selection = True
        self._update_analysis_controls()
        self._chunk_list_view.update_chunks(
            self._state.search_matches, selected_document_id=document.id
        )

    def _clear_selection(self) -> None:
        self._state.selected_paper = None
        self._has_search_selection = False
        self._chunk_list_view.update_chunks(self._state.search_matches, None)
        self._update_analysis_controls()

    def _open_pdf_for_document(self, document) -> None:
        if not document or not document.pdf_file_path:
            QMessageBox.warning(self, "Missing PDF", "This item does not have a PDF path.")
            return

        path = Path(document.pdf_file_path).expanduser()
        if not path.exists():
            QMessageBox.warning(self, "File not found", f"PDF not found: {path}")
            return

        # Launch in background to avoid blocking UI.
        runnable = _OpenPdfRunnable(path)
        self._thread_pool.start(runnable)

    def _open_settings_dialog(self) -> None:
        """Open the settings dialog for API key configuration."""
        dialog = SettingsDialog(
            self._settings_manager,
            validator=self._validate_api_key,
            thread_pool=self._thread_pool,
            parent=self,
        )
        if dialog.exec():
            self._load_state_from_settings()
            self.settings_tab.refresh()

    def _validate_api_key(self, api_key: str, *, base_url: str, model: str) -> None:
        """Lightweight embedding request to validate API key with provided base/model."""

        class _TransientSettings:
            def __init__(self, key: str, base: str, model_name: str) -> None:
                self._key = key
                self.embedding_base_url = base
                self.embedding_model = model_name

            def get_embedding_api_key(self) -> str | None:  # pragma: no cover - trivial
                return self._key

        client = EmbeddingClient(
            _TransientSettings(api_key, base_url, model),
            base_url=base_url,
            model=model,
        )
        # Small payload to verify credentials.
        client.get_embedding("ping")

    def _load_state_from_settings(self) -> None:
        """Load enable_ai_analysis flag from persisted settings."""
        settings = self._settings_manager.load_settings()
        if not self._search_service_provided:
            self._embedding_client = EmbeddingClient(
                self._settings_manager,
                base_url=settings.embedding_base_url,
                model=settings.embedding_model,
            )
            self._search_service = SearchService(
                self._embedding_client,
                self._vector_manager,
                self._metadata_manager,
            )
            self._ai_service = AIService(
                self._settings_manager,
                base_url=settings.chat_base_url,
                model=settings.chat_model,
                metadata_manager=self._metadata_manager,
            )
        # Always refresh indexing service to use current embedding client
        self._indexing_service = IndexingService(
            self._zotero_manager,
            metadata_manager=self._metadata_manager,
            vector_manager=self._vector_manager,
            embedding_client=self._embedding_client,
        )
        self._state.enable_ai_analysis = settings.enable_ai_analysis
        self._update_analysis_controls()

    def _handle_selection_changed(self, has_selection: bool) -> None:
        self._has_search_selection = bool(has_selection)
        self._update_analysis_controls()

    def _set_search_tab_enabled(self, enabled: bool) -> None:
        """Toggle Search tab availability."""
        if self._search_tab_index >= 0:
            self._main_tabs.setTabEnabled(self._search_tab_index, enabled)
            self.search_tab.setEnabled(enabled)

    def _maybe_enable_search_from_existing_index(self) -> None:
        """Enable Search tab when an existing index is already present."""
        try:
            if self._metadata_manager.has_documents():
                self._set_search_tab_enabled(True)
        except Exception:
            logger.exception("Failed to check existing index presence")

    def _update_analysis_controls(self) -> None:
        """Update visibility and enabled state of AI analysis controls."""
        can_analyze = bool(self._settings_manager.get_chat_api_key()) and self._state.enable_ai_analysis
        has_results = bool(self._state.search_matches)
        busy = bool(self._analyze_button.property("busy"))
        enabled = can_analyze and has_results and not busy
        self._analyze_button.setVisible(True)
        self._analysis_loading.setVisible(busy)
        self._analyze_button.setEnabled(enabled)
        self._chat_send_button.setEnabled(enabled)
        self._chunk_count.setEnabled(not busy)

        if not can_analyze:
            tooltip = "Configure AI analysis and API keys in Settings to enable analysis."
            self._analysis_loading.setText("AI analysis unavailable; configure settings.")
        elif not has_results:
            tooltip = "Run a search to enable analysis."
            self._analysis_loading.setText("")
        elif busy:
            tooltip = "Analysis in progress."
        else:
            tooltip = "Analyze selected papers with AI."
            if not self._has_search_selection:
                tooltip = "Select a paper to focus analysis, or analyze current results."
            self._analysis_loading.setText("")

        self._analyze_button.setToolTip(tooltip)

    def _handle_token_usage(self, usage) -> None:
        """Update status bar and session totals when token usage is recorded."""
        print(
            "[UI] token usage received",
            "op=", getattr(usage, "operation", None),
            "model=", getattr(usage, "model", None),
            "total=", getattr(usage, "tokens_used", None),
            "prompt=", getattr(usage, "prompt_tokens", None),
            "completion=", getattr(usage, "completion_tokens", None),
            flush=True,
        )
        logger.info(
            "Token usage received: op=%s model=%s total=%s prompt=%s completion=%s",
            getattr(usage, "operation", None),
            getattr(usage, "model", None),
            getattr(usage, "tokens_used", None),
            getattr(usage, "prompt_tokens", None),
            getattr(usage, "completion_tokens", None),
        )
        try:
            tokens = int(getattr(usage, "tokens_used", 0))
        except Exception:
            tokens = 0
        prompt = max(0, getattr(usage, "prompt_tokens", 0))
        completion = max(0, getattr(usage, "completion_tokens", 0))
        op = getattr(usage, "operation", "")
        if op == "embedding":
            self._session_embedding_tokens += max(0, tokens)
            self._session_embedding_prompt += prompt
            self._session_embedding_model = getattr(usage, "model", None)
        elif op == "chat_completion":
            self._session_analysis_tokens += max(0, tokens)
            self._session_analysis_prompt += prompt
            self._session_analysis_completion += completion
            self._session_analysis_model = getattr(usage, "model", None)
        self._token_status.setText(
            f"Embedding ({self._session_embedding_model or '-'}) {self._session_embedding_prompt} tokens "
            f"| AI Analysis ({self._session_analysis_model or '-'}) "
            f"{self._session_analysis_prompt} prompt / {self._session_analysis_completion} completion tokens"
        )


class _IndexingWorkerSignals(QObject):
    progress = Signal(dict)
    finished = Signal()
    token_usage = Signal(object)


class _IndexingRunnable(QRunnable):
    """Background task runner for indexing requests."""

    def __init__(self, service: IndexingService, scope: dict) -> None:
        super().__init__()
        self._service = service
        self._scope = scope
        self.signals = _IndexingWorkerSignals()

    def run(self) -> None:
        try:
            self._service.set_progress_callback(self.signals.progress.emit)
            self._service.set_usage_callback(self.signals.token_usage.emit)
            self._service.start_indexing(self._scope)
        finally:
            self._service.set_progress_callback(None)
            self._service.set_usage_callback(None)
            self.signals.finished.emit()


class _SearchWorkerSignals(QObject):
    result = Signal(SearchResult)
    error = Signal(str)
    finished = Signal()
    usage = Signal(object)


class _SearchRunnable(QRunnable):
    """Background task runner for search requests."""

    def __init__(self, service: SearchService, query: str, count: int) -> None:
        super().__init__()
        self._service = service
        self._query = query
        self._count = count
        self.signals = _SearchWorkerSignals()

    def run(self) -> None:
        try:
            result = self._service.search(self._query, k=self._count)
            self.signals.result.emit(result)
            if result.token_usage:
                self.signals.usage.emit(result.token_usage)
        except SearchServiceError as error:
            self.signals.error.emit(str(error))
        except Exception as error:  # pragma: no cover - safeguard
            self.signals.error.emit(str(error))
        finally:
            self.signals.finished.emit()


class _OpenPdfRunnable(QRunnable):
    """Open a PDF using the system default viewer without blocking the UI."""

    def __init__(self, pdf_path: Path) -> None:
        super().__init__()
        self._pdf_path = pdf_path

    def run(self) -> None:
        try:
            if sys.platform.startswith("darwin"):
                subprocess.Popen(["open", str(self._pdf_path)])
            elif os.name == "nt":
                os.startfile(self._pdf_path)  # type: ignore[attr-defined]
            else:
                subprocess.Popen(["xdg-open", str(self._pdf_path)])
        except Exception:
            logger.exception("Failed to open PDF: %s", self._pdf_path)


class _AIWorkerSignals(QObject):
    result = Signal(str)
    error = Signal(str)
    finished = Signal()
    usage = Signal(object)


class _AIAnalyzeRunnable(QRunnable):
    """Background task runner for AI analysis."""

    def __init__(
        self,
        service: AIService,
        query: str,
        matches: list[SearchMatch],
        top_n: int,
    ) -> None:
        super().__init__()
        self._service = service
        self._query = query
        self._matches = matches
        self._top_n = top_n
        self.signals = _AIWorkerSignals()

    def run(self) -> None:
        try:
            result, usage = self._service.analyze_chunks(self._query, self._matches, self._top_n)
            print(
                "[AIAnalyzeRunnable] emitting usage",
                "op=", getattr(usage, "operation", None),
                "model=", getattr(usage, "model", None),
                "total=", getattr(usage, "tokens_used", None),
                "prompt=", getattr(usage, "prompt_tokens", None),
                "completion=", getattr(usage, "completion_tokens", None),
                flush=True,
            )
            self.signals.result.emit(result)
            self.signals.usage.emit(usage)
        except (AIServiceError, UnauthorizedAIServiceError) as error:
            self.signals.error.emit(str(error))
        except Exception as error:  # pragma: no cover - safeguard
            self.signals.error.emit(str(error))
        finally:
            self.signals.finished.emit()


class _ExportSignals(QObject):
    success = Signal(str)
    error = Signal(str)


class _ExportPdfRunnable(QRunnable):
    """Background task to copy PDFs from matches into a destination subfolder."""

    def __init__(self, destination: str, matches: list[SearchMatch], selected_paper) -> None:
        super().__init__()
        self._destination = destination
        self._matches = matches
        self._selected_paper = selected_paper
        self.signals = _ExportSignals()

    def run(self) -> None:
        try:
            self._perform_export()
        except Exception as error:  # pragma: no cover - safeguard
            self.signals.error.emit(str(error))

    def _perform_export(self) -> None:
        unique_paths: dict[str, Path] = {}
        for match in self._matches:
            doc = match.document
            if self._selected_paper and (not doc or doc.id != self._selected_paper.id):
                continue
            if doc and doc.pdf_file_path:
                p = Path(doc.pdf_file_path).expanduser()
                if p.exists():
                    unique_paths[p.name] = p

        if not unique_paths:
            self.signals.error.emit("No PDF files found to export.")
            return

        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        target_dir = Path(self._destination) / f"zotero-export-{timestamp}"
        target_dir.mkdir(parents=True, exist_ok=True)

        for name, src in unique_paths.items():
            shutil.copy2(src, target_dir / name)

        self.signals.success.emit(str(target_dir))


def format_chatgpt_prompt(
    query: str,
    matches: list[SearchMatch],
    *,
    limit: int,
    selected_document_id: int | None = None,
) -> str:
    """Create a ChatGPT-friendly prompt from query and matches."""

    limited: list[SearchMatch] = []
    for match in matches:
        if selected_document_id and (not match.document or match.document.id != selected_document_id):
            continue
        limited.append(match)
        if len(limited) >= max(1, min(limit, 50)):
            break

    lines = [
        "Based on the following research paper excerpts, please answer the query below.",
        "",
        f"Query: \"{query}\"",
        "",
        "Excerpts:",
    ]
    for idx, match in enumerate(limited, start=1):
        doc = match.document
        title = doc.title if doc else "Unknown title"
        authors = ", ".join(doc.authors) if doc and doc.authors else "Unknown authors"
        year = doc.year if doc else "n/a"
        page = match.chunk.page_number
        content = match.chunk.content.replace("\n", " ").strip()
        lines.append(
            f"{idx}. Source: {title} ({authors}, {year}) - Page {page}\n    Content: \"{content}\""
        )

    return "\n".join(lines)
