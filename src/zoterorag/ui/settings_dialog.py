"""Settings dialog for managing API keys and AI toggle."""

from __future__ import annotations

from typing import Callable, Optional

from PySide6.QtCore import QObject, QRunnable, QThreadPool, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLabel,
    QLineEdit,
    QPushButton,
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

        form = QFormLayout()
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
        # Do not pre-fill the key for security; show placeholder if one exists.
        existing_key = self._settings_manager.get_api_key()
        if existing_key:
            self._api_key_input.setPlaceholderText("Existing key stored securely")

    def _handle_save(self) -> None:
        api_key = self._api_key_input.text().strip()
        if api_key:
            self._settings_manager.set_api_key_securely(api_key)

        enable_ai = self._ai_toggle.isChecked()
        # Get current API key to preserve it in settings
        current_api_key = self._settings_manager.get_api_key()
        new_settings = AppSettings(
            zotero_data_path=self._settings_manager.get_zotero_path()
            and str(self._settings_manager.get_zotero_path()),
            api_key=current_api_key,
            enable_ai_analysis=enable_ai,
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
