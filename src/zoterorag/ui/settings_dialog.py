"""Settings dialog for managing application configuration."""

from __future__ import annotations

from typing import Callable, Optional

from PySide6.QtCore import QObject, QRunnable, QThreadPool, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QFileDialog,
    QComboBox,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
)

from ..config.settings_manager import AppSettings, SettingsManager


class SettingsDialog(QDialog):
    """Allow users to configure API key and AI analysis toggle."""

    def __init__(
        self,
        settings_manager: SettingsManager,
        *,
        validator: Optional[Callable[[str], None]] = None,
        thread_pool: Optional[QThreadPool] = None,
        parent=None,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self._settings_manager = settings_manager
        self._validator = validator
        self._thread_pool = thread_pool or QThreadPool.globalInstance()

        self._api_key_input = QLineEdit()
        self._api_key_input.setEchoMode(QLineEdit.Password)
        self._ai_toggle = QCheckBox("Enable In-App AI Analysis")

        self._status_label = QLabel()
        self._test_button = QPushButton("Test Connection")
        self._test_button.clicked.connect(self._handle_test)

        self._zotero_path = QLineEdit()
        self._browse_path = QPushButton("Browse")
        self._browse_path.clicked.connect(self._handle_browse)

        self._api_base_url = QLineEdit()
        self._api_base_url.setToolTip("OpenAI API endpoint (default: https://api.openai.com/v1)")
        
        self._embedding_model = QLineEdit()
        self._embedding_model.setToolTip("Model for generating text embeddings (e.g., text-embedding-3-small)")
        
        self._chat_model = QLineEdit()
        self._chat_model.setToolTip("Model for AI-assisted analysis (e.g., gpt-4o-mini)")
        
        self._chunk_size = QSpinBox()
        self._chunk_size.setRange(100, 5000)
        self._chunk_size.setToolTip(
            "Number of characters per text chunk for embedding (100-5000).\n"
            "Smaller chunks provide more precise results but require more embeddings.\n"
            "Recommended: 500-1000."
        )
        
        self._chunk_overlap = QSpinBox()
        self._chunk_overlap.setRange(0, 2000)
        self._chunk_overlap.setToolTip(
            "Number of overlapping characters between chunks (0-2000).\n"
            "Overlap ensures context continuity across chunks.\n"
            "Recommended: 10-20% of chunk size."
        )
        
        self._default_search_results = QSpinBox()
        self._default_search_results.setRange(1, 200)
        self._theme = QComboBox()
        self._theme.addItems(["light", "dark", "auto"])

        form = QFormLayout()
        form.addRow("Zotero Data Path", self._zotero_path)
        form.addRow("", self._browse_path)
        form.addRow("API Base URL", self._api_base_url)
        form.addRow("Embedding Model", self._embedding_model)
        form.addRow("Chat Model", self._chat_model)
        form.addRow("Chunk Size", self._chunk_size)
        form.addRow("Chunk Overlap", self._chunk_overlap)
        form.addRow("Default Search Results", self._default_search_results)
        form.addRow("Theme", self._theme)
        form.addRow("API Key", self._api_key_input)
        form.addRow("", self._ai_toggle)

        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self._handle_save)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(self._test_button)
        layout.addWidget(self._status_label)
        layout.addWidget(buttons)

        self._load_settings()

    def _load_settings(self) -> None:
        settings = self._settings_manager.load_settings()
        self._ai_toggle.setChecked(settings.enable_ai_analysis)
        self._zotero_path.setText(settings.zotero_data_path or "")
        self._api_base_url.setText(settings.api_base_url)
        self._embedding_model.setText(settings.embedding_model)
        self._chat_model.setText(settings.chat_model)
        self._chunk_size.setValue(settings.chunk_size)
        self._chunk_overlap.setValue(settings.chunk_overlap)
        self._default_search_results.setValue(settings.default_search_results)
        idx = self._theme.findText(settings.theme)
        if idx != -1:
            self._theme.setCurrentIndex(idx)
        # Do not pre-fill the key for security; show placeholder if one exists.
        existing_key = self._settings_manager.get_api_key()
        if existing_key:
            self._api_key_input.setPlaceholderText("Existing key stored securely")

    def _handle_save(self) -> None:
        api_key = self._api_key_input.text().strip()
        if api_key:
            self._settings_manager.set_api_key_securely(api_key)

        enable_ai = self._ai_toggle.isChecked()
        new_settings = AppSettings(
            zotero_data_path=self._zotero_path.text().strip() or None,
            api_base_url=self._api_base_url.text().strip(),
            embedding_model=self._embedding_model.text().strip(),
            chat_model=self._chat_model.text().strip(),
            chunk_size=self._chunk_size.value(),
            chunk_overlap=self._chunk_overlap.value(),
            default_search_results=self._default_search_results.value(),
            theme=self._theme.currentText(),
            enable_ai_analysis=enable_ai,
            keyring_service=self._settings_manager._keyring_service,  # reuse existing service
        )
        self._settings_manager.save_settings(new_settings)
        # Refresh settings from keyring after save
        self._settings_manager.refresh()
        self.accept()

    def _handle_test(self) -> None:
        api_key = self._api_key_input.text().strip() or self._settings_manager.get_api_key()
        if not api_key:
            self._status_label.setText("Enter an API key before testing.")
            return

        if not self._validator:
            # No validator provided; use a simple success message.
            self._status_label.setText("Test connection not configured.")
            return

        runnable = _TestConnectionRunnable(api_key, self._validator)
        runnable.signals.success.connect(
            lambda: self._status_label.setText("Connection successful.")
        )
        runnable.signals.failure.connect(
            lambda message: self._status_label.setText(f"Connection failed: {message}")
        )
        self._thread_pool.start(runnable)

    def _handle_browse(self) -> None:
        directory = QFileDialog.getExistingDirectory(self, "Select Zotero Data Directory")
        if directory:
            self._zotero_path.setText(directory)


class _TestSignals(QObject):
    success = Signal()
    failure = Signal(str)


class _TestConnectionRunnable(QRunnable):
    """Background task to validate API connectivity."""

    def __init__(self, api_key: str, validator: Callable[[str], None]) -> None:
        super().__init__()
        self._api_key = api_key
        self._validator = validator
        self.signals = _TestSignals()

    def run(self) -> None:
        try:
            self._validator(self._api_key)
            self.signals.success.emit()
        except Exception as exc:  # pragma: no cover - protective
            self.signals.failure.emit(str(exc))
