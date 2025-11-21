"""Tests for PDF export runnable logic."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

import pytest

import pytest

pytest.importorskip("PySide6")

from zoterorag.core.data.models import Chunk, Document
from zoterorag.core.services.search_service import SearchMatch
from zoterorag.ui.main_window import _ExportPdfRunnable


def _match(doc_id: int, path: Path) -> SearchMatch:
    doc = Document(
        id=doc_id,
        zotero_item_key=f"key-{doc_id}",
        title=f"Doc {doc_id}",
        authors=["Author"],
        year=2024,
        pdf_file_path=str(path),
        indexed_at=datetime.utcnow(),
    )
    chunk = Chunk(
        id=doc_id,
        document_id=doc_id,
        content="text",
        page_number=1,
        vector_id=doc_id,
    )
    return SearchMatch(chunk=chunk, document=doc, distance=0.1)


def test_export_copies_unique_pdfs(tmp_path):
    src1 = tmp_path / "a.pdf"
    src2 = tmp_path / "b.pdf"
    src1.write_text("a")
    src2.write_text("b")
    matches = [_match(1, src1), _match(2, src2)]

    runnable = _ExportPdfRunnable(str(tmp_path), matches, selected_paper=None)
    captured = {}

    def on_success(folder: str):
        captured["folder"] = folder

    runnable.signals.success.connect(on_success)
    runnable._perform_export()

    target = Path(captured["folder"])
    assert target.exists()
    assert (target / "a.pdf").read_text() == "a"
    assert (target / "b.pdf").read_text() == "b"


def test_export_filters_by_selected_document(tmp_path):
    src1 = tmp_path / "a.pdf"
    src2 = tmp_path / "b.pdf"
    src1.write_text("a")
    src2.write_text("b")
    matches = [_match(1, src1), _match(2, src2)]

    class DummyDoc:
        id = 1

    runnable = _ExportPdfRunnable(str(tmp_path), matches, selected_paper=DummyDoc())
    captured = {}

    def on_success(folder: str):
        captured["folder"] = folder

    runnable.signals.success.connect(on_success)
    runnable._perform_export()

    target = Path(captured["folder"])
    assert target.exists()
    assert (target / "a.pdf").exists()
    assert not (target / "b.pdf").exists()
