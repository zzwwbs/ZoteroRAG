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
        self._api_base_label = QLabel()
        self._embedding_model_label = QLabel()
        self._chat_model_label = QLabel()
        self._chunk_size_label = QLabel()
        self._chunk_overlap_label = QLabel()
        self._default_search_results_label = QLabel()
        self._theme_label = QLabel()
        self._ai_enabled_label = QLabel()
        self._api_key_label = QLabel()

        form = QFormLayout()
        form.addRow("Zotero Path", self._zotero_label)
        form.addRow("API Base URL", self._api_base_label)
        form.addRow("Embedding Model", self._embedding_model_label)
        form.addRow("Chat Model", self._chat_model_label)
        form.addRow("Chunk Size", self._chunk_size_label)
        form.addRow("Chunk Overlap", self._chunk_overlap_label)
        form.addRow("Default Search Results", self._default_search_results_label)
        form.addRow("Theme", self._theme_label)
        form.addRow("In-App AI Analysis", self._ai_enabled_label)
        form.addRow("API Key Stored", self._api_key_label)

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
        self._api_base_label.setText(settings.api_base_url)
        self._embedding_model_label.setText(settings.embedding_model)
        self._chat_model_label.setText(settings.chat_model)
        self._chunk_size_label.setText(str(settings.chunk_size))
        self._chunk_overlap_label.setText(str(settings.chunk_overlap))
        self._default_search_results_label.setText(str(settings.default_search_results))
        self._theme_label.setText(settings.theme)
        self._ai_enabled_label.setText("Enabled" if settings.enable_ai_analysis else "Disabled")
        has_key = bool(self._settings_manager.get_api_key())
        self._api_key_label.setText("Stored" if has_key else "Not stored")
