"""Indexing service orchestration tests."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Iterable, List

from zoterorag.core.data.models import Chunk, Document
from zoterorag.core.services.indexing_service import IndexingService
from zoterorag.core.services.zotero_manager import ZoteroItem


class DummyZoteroManager:
    def __init__(self, items: List[ZoteroItem], attachments: Dict[int, List[Path]]) -> None:
        self._items = items
        self._attachments = attachments

    def get_items_for_scope(self, scope: Dict[str, Any]) -> List[ZoteroItem]:
        if scope.get("type") == "selection":
            ids = set(scope.get("item_ids", []))
            return [item for item in self._items if item.item_id in ids]
        return self._items

    def get_pdf_attachments(self, item_id: int) -> List[Path]:
        return self._attachments.get(item_id, [])


class DummyDocumentRepository:
    def __init__(self) -> None:
        self._store: Dict[str, Document] = {}
        self._next_id = 1

    def insert(self, document: Document) -> Document:
        document.id = self._next_id
        self._next_id += 1
        self._store[document.zotero_item_key] = document
        return document

    def get_by_zotero_key(self, key: str) -> Document | None:
        return self._store.get(key)


class DummyChunkRepository:
    def __init__(self) -> None:
        self.entries: list[Chunk] = []

    def insert(self, chunk: Chunk) -> Chunk:
        chunk.id = len(self.entries) + 1
        self.entries.append(chunk)
        return chunk


class DummyMetadataManager:
    def __init__(self) -> None:
        self.document_repository = DummyDocumentRepository()
        self.chunk_repository = DummyChunkRepository()
        self._vector_counter = 0

    def initialize_database(self) -> None:  # pragma: no cover - no-op
        pass

    def get_document_by_key(self, key: str) -> Document | None:
        return self.document_repository.get_by_zotero_key(key)

    def get_next_vector_id(self) -> int:
        self._vector_counter += 1
        return self._vector_counter


class DummyVectorManager:
    def __init__(self) -> None:
        self.added: list[tuple[List[float], int]] = []
        self.saved = False

    def load_index(self) -> None:  # pragma: no cover - no-op
        pass

    def add_vectors(self, vectors, vector_ids) -> None:
        for embedding, identifier in zip(vectors, vector_ids):
            self.added.append((embedding, identifier))

    def save_index(self) -> None:
        self.saved = True


class DummyEmbeddingClient:
    def __init__(self) -> None:
        self.requests: list[str] = []

    def get_embedding(self, text: str) -> list[float]:
        self.requests.append(text)
        return [float(len(text))]


def dummy_chunker(text: str, document_id: int, page_number: int, chunk_size: int, chunk_overlap: int):
    chunk = Chunk(document_id=document_id, content=text.strip(), page_number=page_number)
    return [chunk]


def dummy_pdf_extractor(path: str) -> str:
    return f"text for {Path(path).name}"


def test_indexing_service_processes_items_and_emits_progress():
    items = [
        ZoteroItem(item_id=1, item_key="AAA", title="Doc A", authors="Author One", year="2022"),
        ZoteroItem(item_id=2, item_key="BBB", title="Doc B", authors="Author Two", year="2023"),
    ]
    attachments = {1: [Path("doc1.pdf")], 2: [Path("doc2.pdf")]}
    metadata = DummyMetadataManager()
    vector_manager = DummyVectorManager()
    embedding_client = DummyEmbeddingClient()
    manager = DummyZoteroManager(items, attachments)
    service = IndexingService(
        manager,
        metadata_manager=metadata,
        vector_manager=vector_manager,
        embedding_client=embedding_client,
        pdf_extractor=dummy_pdf_extractor,
        chunker=dummy_chunker,
    )

    progress_events: list[dict] = []
    service.set_progress_callback(progress_events.append)
    service.start_indexing({"type": "all"})

    assert metadata.chunk_repository.entries  # chunks stored
    assert vector_manager.saved
    assert len(embedding_client.requests) == 2
    assert progress_events[-1]["status"] == "complete"


def test_indexing_service_skips_previously_indexed_items():
    items = [ZoteroItem(item_id=1, item_key="AAA", title="Doc A", authors="Author", year="2022")]
    attachments = {1: [Path("doc1.pdf")]}
    metadata = DummyMetadataManager()
    metadata.document_repository.insert(
        Document(zotero_item_key="AAA", title="Doc A", authors=[], year=2022, pdf_file_path="")
    )
    vector_manager = DummyVectorManager()
    embedding_client = DummyEmbeddingClient()

    service = IndexingService(
        DummyZoteroManager(items, attachments),
        metadata_manager=metadata,
        vector_manager=vector_manager,
        embedding_client=embedding_client,
        pdf_extractor=dummy_pdf_extractor,
        chunker=dummy_chunker,
    )

    service.start_indexing({"type": "all"})
    # Should not add new vectors since item skipped
    assert not vector_manager.added


def test_indexing_service_cancels_after_current_item():
    items = [
        ZoteroItem(item_id=1, item_key="AAA", title="Doc A", authors="Author One", year="2022"),
        ZoteroItem(item_id=2, item_key="BBB", title="Doc B", authors="Author Two", year="2023"),
    ]
    attachments = {1: [Path("doc1.pdf")], 2: [Path("doc2.pdf")]}
    metadata = DummyMetadataManager()
    vector_manager = DummyVectorManager()
    embedding_client = DummyEmbeddingClient()
    manager = DummyZoteroManager(items, attachments)
    service = IndexingService(
        manager,
        metadata_manager=metadata,
        vector_manager=vector_manager,
        embedding_client=embedding_client,
        pdf_extractor=dummy_pdf_extractor,
        chunker=dummy_chunker,
    )

    progress_events: list[dict] = []

    def progress(payload: dict) -> None:
        progress_events.append(payload.copy())
        if payload.get("processed_count") == 1:
            service.cancel_indexing()

    service.set_progress_callback(progress)
    service.start_indexing({"type": "all"})

    assert len(embedding_client.requests) == 1
    assert progress_events[-1]["status"] == "cancelled"
    assert vector_manager.saved
