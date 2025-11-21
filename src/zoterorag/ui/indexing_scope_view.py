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

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._collections: list[Collection] = []
        self._entire_radio = QRadioButton("Entire Library")
        self._collection_radio = QRadioButton("Specific Collection")
        self._collection_combo = QComboBox()
        self._start_button = QPushButton("Start Indexing")
        self._status_label = QLabel("")

        self._entire_radio.setChecked(True)
        self._collection_combo.setEnabled(False)

        self._collection_radio.toggled.connect(self._collection_combo.setEnabled)
        self._start_button.clicked.connect(self._emit_scope)

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

    def set_collections(self, collections: Iterable[Collection]) -> None:
        """Populate the combobox with available collections."""

        self._collections = list(collections)
        self._collection_combo.clear()
        for collection in self._collections:
            label = collection.name
            self._collection_combo.addItem(label, userData=collection)

        has_collections = bool(self._collections)
        self._collection_radio.setEnabled(has_collections)
        self._collection_combo.setEnabled(has_collections and self._collection_radio.isChecked())
        self._status_label.setText(
            "Collections loaded." if has_collections else "No collections available."
        )

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
