"""UI component for selecting the indexing scope."""

from __future__ import annotations

from typing import Iterable

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QComboBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QRadioButton,
    QVBoxLayout,
    QWidget,
)

from ..core.data.models import Collection


class IndexingScopeView(QWidget):
    """Widget that lets the user choose which part of their library to index."""

    scope_selected = Signal(dict)
    cancel_requested = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._collections: list[Collection] = []
        self._entire_radio = QRadioButton("Entire Library")
        self._collection_radio = QRadioButton("Specific Collection")
        self._collection_combo = QComboBox()
        self._start_button = QPushButton("Start Indexing")
        self._status_label = QLabel("")
        self._busy = False
        self._cancel_mode = False

        self._entire_radio.setChecked(True)
        self._collection_combo.setEnabled(False)

        self._collection_radio.toggled.connect(self._handle_collection_toggle)
        self._start_button.clicked.connect(self._handle_start_or_cancel)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("<b>Indexing Scope</b>"))

        radio_box = QGroupBox("Choose scope")
        radio_layout = QVBoxLayout(radio_box)
        radio_layout.addWidget(self._entire_radio)
        radio_layout.addWidget(self._collection_radio)

        combo_layout = QHBoxLayout()
        combo_layout.addWidget(QLabel("Collection:"))
        combo_layout.addWidget(self._collection_combo)
        radio_layout.addLayout(combo_layout)

        layout.addWidget(radio_box)
        layout.addWidget(self._start_button)
        layout.addWidget(self._status_label)

    def set_collections(self, collections: Iterable[Collection], counts: dict[int, int] | None = None) -> None:
        """Populate the combobox with available collections."""

        self._collections = list(collections)
        self._collection_combo.clear()
        counts = counts or {}
        for collection in self._collections:
            label = self._format_collection_label(collection, counts.get(collection.id, 0))
            self._collection_combo.addItem(label, userData=collection)

        self._update_collection_controls()
        self._status_label.setText(
            "Collections loaded." if self._collections else "No collections available."
        )

    def set_busy(self, busy: bool) -> None:
        """Enable/disable user interaction while indexing runs."""

        self._busy = busy
        self._start_button.setEnabled((not busy) or self._cancel_mode)
        self._entire_radio.setEnabled(not busy)
        self._update_collection_controls()

    def update_progress(self, payload: dict) -> None:
        status = payload.get("status")
        processed = payload.get("processed_count")
        total = payload.get("total_count")
        current = payload.get("current_item_name") or ""
        if status == "complete":
            message = "Indexing complete."
            self.set_idle_mode()
        elif status == "cancelled":
            message = "Indexing cancelled."
            self.set_idle_mode()
        elif status == "error":
            message = f"Error: {payload.get('error_message')}"
            self.set_idle_mode()
        elif status == "skipped":
            message = f"Skipped {current} ({processed}/{total})."
        else:
            message = f"Indexing {current} ({processed}/{total})..."
        self._status_label.setText(message)

    def set_cancel_mode(self) -> None:
        """Switch button to a cancel affordance."""
        self._cancel_mode = True
        self._start_button.setText("Cancel Indexing")
        self._start_button.setStyleSheet("background-color: red; color: white;")
        self._start_button.setEnabled(True)

    def set_cancelling_mode(self) -> None:
        """Show cancellation in progress."""
        self._cancel_mode = True
        self._start_button.setText("Cancelling...")
        self._start_button.setEnabled(False)

    def set_idle_mode(self) -> None:
        """Restore start state after completion or cancellation."""
        self._cancel_mode = False
        self._start_button.setText("Start Indexing")
        self._start_button.setStyleSheet("")
        self.set_busy(False)

    def set_status_message(self, message: str) -> None:
        self._status_label.setText(message)

    def set_total_paper_count(self, count: int) -> None:
        """Update the entire library radio label with count."""
        self._entire_radio.setText(f"Entire Library ({count} papers)")

    def _format_collection_label(self, collection: Collection, count: int) -> str:
        suffix = "paper" if count == 1 else "papers"
        return f"{collection.name} ({count} {suffix})"

    def _handle_start_or_cancel(self) -> None:
        if self._cancel_mode:
            self.cancel_requested.emit()
            self.set_cancelling_mode()
            self._status_label.setText("Cancelling...")
            return
        self._emit_scope()

    def _emit_scope(self) -> None:
        if self._entire_radio.isChecked():
            scope = {"type": "all"}
        elif self._collection_radio.isChecked() and self._collections:
            index = self._collection_combo.currentIndex()
            collection = self._collection_combo.itemData(index)
            if not collection:
                self._status_label.setText("Please select a collection.")
                return
            scope = {
                "type": "collection",
                "id": collection.id,
                "key": collection.zotero_collection_key,
            }
        else:
            self._status_label.setText("Please choose a scope.")
            return

        self.scope_selected.emit(scope)
        self._status_label.setText("Indexing requested…")

    def _handle_collection_toggle(self, checked: bool) -> None:
        has_collections = bool(self._collections)
        self._collection_combo.setEnabled(checked and has_collections and not self._busy)

    def _update_collection_controls(self) -> None:
        has_collections = bool(self._collections)
        self._collection_radio.setEnabled(has_collections and not self._busy)
        self._collection_combo.setEnabled(
            self._collection_radio.isChecked() and has_collections and not self._busy
        )
