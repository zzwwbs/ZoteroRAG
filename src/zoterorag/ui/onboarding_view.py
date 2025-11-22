"""First-launch onboarding experience with welcome, privacy, and Zotero path steps."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QFileDialog,
    QLabel,
    QPushButton,
    QStackedWidget,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QCheckBox,
)

from ..core.services.zotero_manager import ZoteroManager


class OnboardingView(QWidget):
    """UI displayed when a Zotero path is missing."""

    done = Signal(str)

    def __init__(self, zotero_manager: ZoteroManager, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._zotero_manager = zotero_manager
        self._stack = QStackedWidget()
        self._selected_path: Path | None = None

        self._welcome = self._build_welcome()
        self._privacy = self._build_privacy()
        self._path_step = self._build_path_step()

        self._stack.addWidget(self._welcome)
        self._stack.addWidget(self._privacy)
        self._stack.addWidget(self._path_step)

        layout = QVBoxLayout(self)
        layout.addWidget(self._stack)

    def _attempt_auto_detection(self) -> None:
        detected = self._zotero_manager.detect_zotero_directory()

        if detected:
            self._selected_path = detected
            self._path_label.setText(f"Detected: {detected}")
            self._status_label.setText("Auto-detected a Zotero directory.")
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
        self._selected_path = candidate
        self._finish(candidate)

    def _finish(self, path: str | Path | None) -> None:
        if isinstance(path, str):
            path = Path(path)
        self.done.emit(str(path) if path else "")

    def _build_welcome(self) -> QWidget:
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.addWidget(QLabel("<b>Welcome to ZoteroRAG Desk</b>"))
        layout.addWidget(QLabel("We will help you pick your Zotero library and review privacy notes."))
        btn = QPushButton("Next")
        btn.clicked.connect(lambda: self._stack.setCurrentWidget(self._privacy))
        layout.addWidget(btn)
        layout.addStretch()
        return container

    def _build_privacy(self) -> QWidget:
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.addWidget(QLabel("<b>Privacy & Cloud Disclosure</b>"))
        layout.addWidget(QLabel("Embeddings and AI calls use your BYOK key; local data stays on your machine."))
        self._privacy_ack = QCheckBox("I understand and accept these terms.")
        next_btn = QPushButton("Next")
        next_btn.clicked.connect(self._go_to_path_step)
        layout.addWidget(self._privacy_ack)
        layout.addWidget(next_btn)
        layout.addStretch()
        return container

    def _go_to_path_step(self) -> None:
        if not self._privacy_ack.isChecked():
            return
        self._stack.setCurrentWidget(self._path_step)
        self.start_detection()

    def _build_path_step(self) -> QWidget:
        container = QWidget()
        self._status_label = QLabel()
        self._path_label = QLabel()
        self._select_button = QPushButton("Select Zotero Directory")
        finish_btn = QPushButton("Finish")
        self._select_button.clicked.connect(self._handle_manual_selection)
        finish_btn.clicked.connect(lambda: self._finish(self._selected_path))

        layout = QVBoxLayout(container)
        layout.addWidget(QLabel("<b>Choose your Zotero library</b>"))
        layout.addWidget(self._status_label)
        layout.addWidget(self._path_label)
        layout.addWidget(self._select_button)
        layout.addWidget(finish_btn)
        layout.addStretch()

        self._status_label.setText("Waiting to detect your Zotero directory...")
        self._path_label.setText("")
        return container
