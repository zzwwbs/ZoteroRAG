"""First-launch onboarding experience for Zotero directory configuration."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QFileDialog,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ..core.services.zotero_manager import ZoteroManager


class OnboardingView(QWidget):
    """UI displayed when a Zotero path is missing."""

    path_confirmed = Signal(str)

    def __init__(self, zotero_manager: ZoteroManager, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._zotero_manager = zotero_manager
        self._status_label = QLabel()
        self._path_label = QLabel()
        self._select_button = QPushButton("Select Zotero Directory")

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("<b>Configure your Zotero library</b>"))
        layout.addWidget(self._status_label)
        layout.addWidget(self._path_label)
        layout.addWidget(self._select_button)
        layout.addStretch()

        self._select_button.clicked.connect(self._handle_manual_selection)

        self._status_label.setText("Waiting to detect your Zotero directory...")
        self._path_label.setText("")

    def _attempt_auto_detection(self) -> None:
        detected = self._zotero_manager.detect_zotero_directory()

        if detected:
            self._path_label.setText(f"Detected: {detected}")
            self._status_label.setText("Auto-detected a Zotero directory.")
            self.path_confirmed.emit(str(detected))
            return

        self._status_label.setText("Auto-detection did not find a Zotero directory.")
        self._path_label.setText("Please select the folder that contains your Zotero library.")

    def start_detection(self) -> None:
        """Kick off the auto-detection workflow."""

        self._status_label.setText("Detecting Zotero directory...")
        self._attempt_auto_detection()

    def _handle_manual_selection(self) -> None:
        start = str(Path.home())
        selection = QFileDialog.getExistingDirectory(
            self,
            "Select Zotero Data Directory",
            start,
            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks,
        )

        if not selection:
            return

        candidate = Path(selection)
        if not self._zotero_manager.is_valid_zotero_directory(candidate):
            self._status_label.setText("The selected folder does not contain zotero.sqlite.")
            self._path_label.setText(selection)
            return

        self._status_label.setText("Zotero directory verified.")
        self._path_label.setText(f"Selected: {selection}")
        self.path_confirmed.emit(selection)
