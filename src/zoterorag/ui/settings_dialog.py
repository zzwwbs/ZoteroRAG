"""Settings dialog for managing application configuration."""

from __future__ import annotations

from typing import Callable, Optional

from PySide6.QtCore import QObject, QRunnable, QThreadPool, Qt, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QFileDialog,
    QComboBox,
    QGroupBox,
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

        self._ai_toggle = QCheckBox("Enable In-App AI Analysis")

        self._zotero_path = QLineEdit()
        self._browse_path = QPushButton("Browse")
        self._browse_path.clicked.connect(self._handle_browse)

        # Embedding config
        self._embedding_provider = QComboBox()
        self._embedding_provider.addItems(["openai"])
        self._embedding_base_url = QLineEdit()
        self._embedding_base_url.setToolTip("OpenAI-compatible embeddings endpoint (e.g., https://api.openai.com/v1)")
        self._embedding_model = QLineEdit()
        self._embedding_model.setToolTip("Model for generating text embeddings (e.g., text-embedding-3-small)")
        self._embedding_key = QLineEdit()
        self._embedding_key.setEchoMode(QLineEdit.Password)

        # Chat config
        self._chat_provider = QComboBox()
        self._chat_provider.addItems(["openai"])
        self._chat_base_url = QLineEdit()
        self._chat_base_url.setToolTip("OpenAI-compatible chat endpoint (e.g., https://api.openai.com/v1)")
        self._chat_model = QLineEdit()
        self._chat_model.setToolTip("Model for AI-assisted analysis (e.g., gpt-4o-mini)")
        self._chat_key = QLineEdit()
        self._chat_key.setEchoMode(QLineEdit.Password)

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

        embedding_group = QGroupBox("Embedding Configuration")
        emb_form = QFormLayout(embedding_group)
        emb_form.setLabelAlignment(Qt.AlignLeft)
        emb_form.setFormAlignment(Qt.AlignLeft | Qt.AlignTop)
        emb_form.addRow("Provider:", self._embedding_provider)
        emb_form.addRow("Base URL:", self._embedding_base_url)
        help_label_emb = QLabel("Endpoint must be OpenAI-compatible (e.g., https://your-host/v1)")
        help_label_emb.setStyleSheet("color: gray; font-size: 9pt;")
        emb_form.addRow("", help_label_emb)
        emb_form.addRow("Model:", self._embedding_model)
        emb_form.addRow("API Key:", self._embedding_key)

        chat_group = QGroupBox("Chat Configuration")
        chat_form = QFormLayout(chat_group)
        chat_form.setLabelAlignment(Qt.AlignLeft)
        chat_form.setFormAlignment(Qt.AlignLeft | Qt.AlignTop)
        chat_form.addRow("Provider:", self._chat_provider)
        chat_form.addRow("Base URL:", self._chat_base_url)
        help_label_chat = QLabel("Endpoint must be OpenAI-compatible (e.g., https://your-host/v1)")
        help_label_chat.setStyleSheet("color: gray; font-size: 9pt;")
        chat_form.addRow("", help_label_chat)
        chat_form.addRow("Model:", self._chat_model)
        chat_form.addRow("API Key:", self._chat_key)

        general_box = QGroupBox("General")
        general_form = QFormLayout(general_box)
        general_form.setLabelAlignment(Qt.AlignLeft)
        general_form.setFormAlignment(Qt.AlignLeft | Qt.AlignTop)
        general_form.addRow("Zotero Data Path:", self._zotero_path)
        general_form.addRow("", self._browse_path)
        general_form.addRow("Chunk Size:", self._chunk_size)
        general_form.addRow("Chunk Overlap:", self._chunk_overlap)
        general_form.addRow("Default Search Results:", self._default_search_results)
        general_form.addRow("Theme:", self._theme)
        general_form.addRow("", self._ai_toggle)

        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self._handle_save)
        buttons.rejected.connect(self.reject)

        self._status_label = QLabel()
        self._test_button = QPushButton("Test Connection")
        self._test_button.clicked.connect(self._handle_test)

        layout = QVBoxLayout(self)
        layout.addWidget(embedding_group)
        layout.addWidget(chat_group)
        layout.addWidget(general_box)
        layout.addWidget(self._test_button)
        layout.addWidget(self._status_label)
        layout.addWidget(buttons)

        self._load_settings()

    def _load_settings(self) -> None:
        settings = self._settings_manager.load_settings()
        self._ai_toggle.setChecked(settings.enable_ai_analysis)
        self._zotero_path.setText(settings.zotero_data_path or "")
        self._embedding_provider.setCurrentText(settings.embedding_provider)
        self._embedding_base_url.setText(settings.embedding_base_url)
        self._embedding_model.setText(settings.embedding_model)
        self._chat_provider.setCurrentText(settings.chat_provider)
        self._chat_base_url.setText(settings.chat_base_url)
        self._chat_model.setText(settings.chat_model)
        self._chunk_size.setValue(settings.chunk_size)
        self._chunk_overlap.setValue(settings.chunk_overlap)
        self._default_search_results.setValue(settings.default_search_results)
        idx = self._theme.findText(settings.theme)
        if idx != -1:
            self._theme.setCurrentIndex(idx)
        # Do not pre-fill keys for security; show placeholder if one exists.
        if self._settings_manager.get_embedding_api_key():
            self._embedding_key.setPlaceholderText("Existing key stored securely")
        if self._settings_manager.get_chat_api_key():
            self._chat_key.setPlaceholderText("Existing key stored securely")

    def _handle_save(self) -> None:
        embedding_key = self._embedding_key.text().strip()
        chat_key = self._chat_key.text().strip()
        current_settings = self._settings_manager.load_settings()

        errors = []
        emb_base = self._embedding_base_url.text().strip()
        chat_base = self._chat_base_url.text().strip()
        emb_model = self._embedding_model.text().strip()
        chat_model = self._chat_model.text().strip()

        if not emb_base:
            errors.append("Embedding base URL is required.")
        if not chat_base:
            errors.append("Chat base URL is required.")
        if not emb_model:
            errors.append("Embedding model is required.")
        if not chat_model:
            errors.append("Chat model is required.")
        if not (embedding_key or self._settings_manager.get_embedding_api_key()):
            errors.append("Embedding API key is required.")
        if not (chat_key or self._settings_manager.get_chat_api_key()):
            errors.append("Chat API key is required.")

        if errors:
            self._status_label.setText(" ".join(errors))
            return

        if self._validator:
            try:
                self._validator(embedding_key or self._settings_manager.get_embedding_api_key(), base_url=emb_base, model=emb_model)
            except Exception as exc:
                self._status_label.setText(f"Embedding config invalid: {exc}")
                return
            try:
                self._validator(chat_key or self._settings_manager.get_chat_api_key(), base_url=chat_base, model=chat_model)
            except Exception as exc:
                self._status_label.setText(f"Chat config invalid: {exc}")
                return

        if embedding_key:
            self._settings_manager.set_embedding_api_key_securely(embedding_key)
        if chat_key:
            self._settings_manager.set_chat_api_key_securely(chat_key)

        # Preserve plaintext keys only when secure storage is unavailable.
        embed_api_value = None
        chat_api_value = None
        if not self._settings_manager.supports_secure_storage():
            embed_api_value = embedding_key or current_settings.embedding_api_key
            chat_api_value = chat_key or current_settings.chat_api_key

        new_settings = AppSettings(
            zotero_data_path=self._zotero_path.text().strip() or None,
            embedding_provider=self._embedding_provider.currentText(),
            embedding_base_url=emb_base,
            embedding_model=self._embedding_model.text().strip(),
            embedding_api_key=embed_api_value,
            chat_provider=self._chat_provider.currentText(),
            chat_base_url=chat_base,
            chat_model=self._chat_model.text().strip(),
            chat_api_key=chat_api_value,
            api_provider=self._chat_provider.currentText(),  # legacy mirror
            api_base_url=chat_base,  # legacy mirror
            chunk_size=self._chunk_size.value(),
            chunk_overlap=self._chunk_overlap.value(),
            default_search_results=self._default_search_results.value(),
            theme=self._theme.currentText(),
            enable_ai_analysis=self._ai_toggle.isChecked(),
            keyring_service=self._settings_manager._keyring_service,  # reuse existing service
        )
        self._settings_manager.save_settings(new_settings)
        # Refresh settings from keyring after save
        self._settings_manager.refresh()
        self.accept()

    def _handle_test(self) -> None:
        """Validate both embedding and chat configurations."""
        if not self._validator:
            self._status_label.setText("Test connection not configured.")
            return

        embedding_key = self._embedding_key.text().strip() or self._settings_manager.get_embedding_api_key()
        chat_key = self._chat_key.text().strip() or self._settings_manager.get_chat_api_key()
        if not embedding_key or not chat_key:
            self._status_label.setText("Enter both API keys before testing.")
            return

        def _on_success(label: str):
            return lambda: self._status_label.setText(label)

        def _on_failure(label_prefix: str):
            return lambda message: self._status_label.setText(f"{label_prefix}: {message}")

        # Run embedding then chat sequentially; chat result overwrites final status.
        runnable = _TestConnectionRunnable(
            embedding_key,
            self._validator,
            base_url=self._embedding_base_url.text().strip(),
            model=self._embedding_model.text().strip(),
        )
        runnable.signals.success.connect(_on_success("Embedding connection successful."))
        runnable.signals.failure.connect(_on_failure("Embedding connection failed"))
        self._thread_pool.start(runnable)

        runnable_chat = _TestConnectionRunnable(
            chat_key,
            self._validator,
            base_url=self._chat_base_url.text().strip(),
            model=self._chat_model.text().strip(),
        )
        runnable_chat.signals.success.connect(_on_success("Chat connection successful."))
        runnable_chat.signals.failure.connect(_on_failure("Chat connection failed"))
        self._thread_pool.start(runnable_chat)

    def _handle_browse(self) -> None:
        directory = QFileDialog.getExistingDirectory(self, "Select Zotero Data Directory")
        if directory:
            self._zotero_path.setText(directory)


class _TestSignals(QObject):
    success = Signal()
    failure = Signal(str)


class _TestConnectionRunnable(QRunnable):
    """Background task to validate API connectivity."""

    def __init__(self, api_key: str, validator: Callable[..., None], *, base_url: str, model: str) -> None:
        super().__init__()
        self._api_key = api_key
        self._validator = validator
        self._base_url = base_url
        self._model = model
        self.signals = _TestSignals()

    def run(self) -> None:
        try:
            self._validator(self._api_key, base_url=self._base_url, model=self._model)
            self.signals.success.emit()
        except Exception as exc:  # pragma: no cover - protective
            self.signals.failure.emit(str(exc))
