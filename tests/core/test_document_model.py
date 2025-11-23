"""Tests for the Document dataclass defaults."""

from zoterorag.core.data.models import Document


def test_document_has_default_indexing_status():
    doc = Document(zotero_item_key="k1", title="t1")
    assert doc.indexing_status == "Not Indexed"
