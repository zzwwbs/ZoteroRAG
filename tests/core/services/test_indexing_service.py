"""Indexing service orchestration tests."""

from pathlib import Path

from zoterorag.core.services.indexing_service import IndexingService


class DummyZoteroManager:
    def __init__(self, attachments: dict[int, list[Path]]) -> None:
        self._attachments = attachments

    def get_pdf_attachments(self, item_id: int) -> list[Path]:
        return self._attachments.get(item_id, [])


def test_extract_text_for_items_aggregates_text(tmp_path):
    pdf_a = tmp_path / "a.pdf"
    pdf_a.write_text("unused")
    attachments = {1: [pdf_a]}

    def fake_extractor(path: str) -> str:
        return f"text:{Path(path).name}"

    service = IndexingService(DummyZoteroManager(attachments), pdf_extractor=fake_extractor)
    result = service.extract_text_for_items([1, 2])
    assert result[1] == "text:a.pdf"
    assert 2 not in result


def test_start_indexing_accepts_scope(tmp_path, caplog):
    service = IndexingService(DummyZoteroManager({}), pdf_extractor=lambda _: "")
    with caplog.at_level("INFO"):
        service.start_indexing({"type": "collection", "id": 5})
    assert "scope" in caplog.text
