"""Settings tab showing current configuration and entry point to edit."""

from __future__ import annotations

from PySide6.QtWidgets import (
    QFormLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ..config.settings_manager import SettingsManager


class SettingsTab(QWidget):
    """Displays current settings and links to the settings dialog."""

    def __init__(
        self,
        settings_manager: SettingsManager,
        open_settings_callback,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._settings_manager = settings_manager
        self._open_settings_callback = open_settings_callback

        self._zotero_label = QLabel()
        self._embedding_provider_label = QLabel()
        self._embedding_base_label = QLabel()
        self._embedding_model_label = QLabel()
        self._embedding_key_label = QLabel()
        self._chat_provider_label = QLabel()
        self._chat_base_label = QLabel()
        self._chat_model_label = QLabel()
        self._chat_key_label = QLabel()
        self._chunk_size_label = QLabel()
        self._chunk_overlap_label = QLabel()
        self._default_search_results_label = QLabel()
        self._theme_label = QLabel()
        self._ai_enabled_label = QLabel()

        form = QFormLayout()
        form.addRow("Zotero Path", self._zotero_label)
        form.addRow("Embedding Provider", self._embedding_provider_label)
        form.addRow("Embedding Base URL", self._embedding_base_label)
        form.addRow("Embedding Model", self._embedding_model_label)
        form.addRow("Embedding API Key Stored", self._embedding_key_label)
        form.addRow("Chat Provider", self._chat_provider_label)
        form.addRow("Chat Base URL", self._chat_base_label)
        form.addRow("Chat Model", self._chat_model_label)
        form.addRow("Chat API Key Stored", self._chat_key_label)
        form.addRow("Chunk Size", self._chunk_size_label)
        form.addRow("Chunk Overlap", self._chunk_overlap_label)
        form.addRow("Default Search Results", self._default_search_results_label)
        form.addRow("Theme", self._theme_label)
        form.addRow("In-App AI Analysis", self._ai_enabled_label)

        self._edit_button = QPushButton("Edit Settings")
        self._edit_button.clicked.connect(self._open_settings_callback)

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(self._edit_button)
        layout.addStretch()

        self.refresh()

    def refresh(self) -> None:
        settings = self._settings_manager.load_settings()
        self._zotero_label.setText(settings.zotero_data_path or "(not set)")
        self._embedding_provider_label.setText(settings.embedding_provider)
        self._embedding_base_label.setText(settings.embedding_base_url)
        self._embedding_model_label.setText(settings.embedding_model)
        self._chat_provider_label.setText(settings.chat_provider)
        self._chat_base_label.setText(settings.chat_base_url)
        self._chat_model_label.setText(settings.chat_model)
        self._chunk_size_label.setText(str(settings.chunk_size))
        self._chunk_overlap_label.setText(str(settings.chunk_overlap))
        self._default_search_results_label.setText(str(settings.default_search_results))
        self._theme_label.setText(settings.theme)
        self._ai_enabled_label.setText("Enabled" if settings.enable_ai_analysis else "Disabled")
        has_embedding_key = bool(self._settings_manager.get_embedding_api_key())
        has_chat_key = bool(self._settings_manager.get_chat_api_key())
        self._embedding_key_label.setText("Stored" if has_embedding_key else "Not stored")
        self._chat_key_label.setText("Stored" if has_chat_key else "Not stored")
