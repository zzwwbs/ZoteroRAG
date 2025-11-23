"""Indexing orchestration that relies on Zotero data and PDF extraction."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List
import threading

from ..data.models import Chunk, Document
from ..utils.chunking_utility import chunk_text
from ..utils.pdf_extractor import extract_text_from_pdf
from .embedding_client import EmbeddingClient, EmbeddingClientError
from .metadata_db_manager import MetadataDBManager
from .vector_db_manager import VectorDBManager
from .zotero_manager import ZoteroManager, ZoteroItem

logger = logging.getLogger(__name__)


class IndexingService:
    """Coordinates pulling Zotero items and extracting their textual content."""

    def __init__(
        self,
        zotero_manager: ZoteroManager,
        metadata_manager: MetadataDBManager | None = None,
        vector_manager: VectorDBManager | None = None,
        embedding_client: EmbeddingClient | None = None,
        pdf_extractor: Callable[[str], str] = extract_text_from_pdf,
        chunker: Callable[..., List[Chunk]] = chunk_text,
        chunk_size: int = 600,
        chunk_overlap: int = 100,
    ) -> None:
        self._zotero_manager = zotero_manager
        self._metadata_manager = metadata_manager or MetadataDBManager()
        self._vector_manager = vector_manager or VectorDBManager(dimension=1536)
        if embedding_client is None:
            raise ValueError("embedding_client is required")
        self._embedding_client = embedding_client
        self._pdf_extractor = pdf_extractor
        self._chunker = chunker
        self._chunk_size = chunk_size
        self._chunk_overlap = chunk_overlap
        self._progress_callback: Callable[[Dict[str, Any]], None] | None = None
        self._cancel_event = threading.Event()
        self._usage_callback: Callable[[Any], None] | None = None
        self._status_callback: Callable[[Dict[str, Any]], None] | None = None

        self._metadata_manager.initialize_database()
        try:
            self._vector_manager.load_index()
        except RuntimeError as error:
            logger.warning("Unable to load FAISS index: %s", error)

    def set_progress_callback(self, callback: Callable[[Dict[str, Any]], None] | None) -> None:
        self._progress_callback = callback

    def set_usage_callback(self, callback: Callable[[Any], None] | None) -> None:
        self._usage_callback = callback

    def set_status_callback(self, callback: Callable[[Dict[str, Any]], None] | None) -> None:
        self._status_callback = callback

    def cancel_indexing(self) -> None:
        """Signal the current indexing run to stop after the current item."""

        self._cancel_event.set()

    def extract_text_for_items(self, item_ids: Iterable[int]) -> Dict[int, str]:
        """Return extracted text for each item by visiting its PDF attachments."""

        results: Dict[int, str] = {}
        for item_id in item_ids:
            pdf_paths = self._zotero_manager.get_pdf_attachments(item_id)
            aggregated: list[str] = []
            for pdf_path in pdf_paths:
                text = self._pdf_extractor(str(pdf_path))
                if text:
                    aggregated.append(text)
                else:
                    logger.warning("No text extracted for %s", pdf_path)

            if aggregated:
                results[item_id] = "\n\n".join(aggregated)

        return results

    def start_indexing(self, scope: Dict[str, Any]) -> None:
        """Kick off the indexing pipeline for the selected scope."""

        self._cancel_event.clear()
        items = self._zotero_manager.get_items_for_scope(scope)
        total = len(items)
        processed = 0

        self._emit_progress(
            {
                "status": "processing",
                "processed_count": processed,
                "total_count": total,
                "current_item_name": None,
                "error_message": None,
            }
        )

        for item in items:
            if self._cancel_event.is_set():
                break
            processed += 1
            payload = {
                "status": "processing",
                "processed_count": processed,
                "total_count": total,
                "current_item_name": item.title,
                "error_message": None,
            }

            if self._is_already_indexed(item):
                payload["status"] = "skipped"
                self._record_status(item, "Indexed")
                self._emit_progress(payload)
                continue

            try:
                self._process_item(item, self._embedding_client)
                self._emit_progress(payload)
            except EmbeddingClientError as error:
                payload["status"] = "error"
                payload["error_message"] = str(error)
                self._record_status(item, "PDF Error")
                self._emit_progress(payload)
            except Exception as error:
                logger.exception("Failed to index item %s", item.item_id)
                payload["status"] = "error"
                payload["error_message"] = str(error)
                self._record_status(item, "PDF Error")
                self._emit_progress(payload)
            if self._cancel_event.is_set():
                break

        try:
            self._vector_manager.save_index()
        except RuntimeError as error:
            logger.error("Failed to save vector index: %s", error)

        final_status = "cancelled" if self._cancel_event.is_set() else "complete"
        self._emit_progress(
            {
                "status": final_status,
                "processed_count": processed,
                "total_count": total,
                "current_item_name": None,
                "error_message": None,
            }
        )
        self._cancel_event.clear()

    def _process_item(self, item: ZoteroItem, embedding_client: EmbeddingClient) -> None:
        pdf_paths = self._zotero_manager.get_pdf_attachments(item.item_id)
        if not pdf_paths:
            self._record_status(item, "No PDF")
            return

        document = Document(
            zotero_item_key=item.item_key or str(item.item_id),
            title=item.title,
            authors=[name.strip() for name in item.authors.split(";") if name.strip()],
            year=int(item.year) if item.year.isdigit() else None,
            pdf_file_path=str(pdf_paths[0]) if pdf_paths else "",
        )
        saved_document = self._metadata_manager.document_repository.insert(document)

        vectors: list[list[float]] = []
        vector_ids: list[int] = []

        page_number = 1
        for pdf_path in pdf_paths:
            text = self._pdf_extractor(str(pdf_path))
            if not text.strip():
                continue

            chunks = self._chunker(
                text,
                saved_document.id or 0,
                page_number=page_number,
                chunk_size=self._chunk_size,
                chunk_overlap=self._chunk_overlap,
            )
            page_number += 1

            for chunk in chunks:
                embedding, usage = embedding_client.get_embedding(chunk.content)
                if usage.tokens_used > 0:
                    try:
                        self._metadata_manager.token_usage_repository.insert(usage)
                    except Exception:  # pragma: no cover - safety
                        logger.exception("Failed to record token usage for indexing")
                    if self._usage_callback:
                        self._usage_callback(usage)
                vector_id = self._metadata_manager.get_next_vector_id()
                chunk.vector_id = vector_id
                self._metadata_manager.chunk_repository.insert(chunk)
                vectors.append(embedding)
                vector_ids.append(vector_id)

        if vectors:
            self._vector_manager.add_vectors(vectors, vector_ids)
            self._record_status(item, "Indexed")
        else:
            self._record_status(item, "PDF Error")

    def _is_already_indexed(self, item: ZoteroItem) -> bool:
        existing = self._metadata_manager.get_document_by_key(item.item_key or str(item.item_id))
        return existing is not None

    def _record_status(self, item: ZoteroItem, status: str) -> None:
        """Ensure a document row exists and set indexing status."""
        repo = self._metadata_manager.document_repository
        existing = repo.get_by_zotero_key(item.item_key or str(item.item_id))
        if existing:
            repo.update_status(item.item_key or str(item.item_id), status)
            if self._status_callback:
                self._status_callback(
                    {
                        "zotero_key": item.item_key or str(item.item_id),
                        "status": status,
                        "title": item.title,
                    }
                )
            return
        doc = Document(
            zotero_item_key=item.item_key or str(item.item_id),
            title=item.title,
            authors=[name.strip() for name in item.authors.split(";") if name.strip()],
            year=int(item.year) if item.year.isdigit() else None,
            pdf_file_path="",
            indexing_status=status,
        )
        saved = repo.insert(doc)
        if self._status_callback and saved.id is not None:
            self._status_callback(
                {
                    "zotero_key": item.item_key or str(item.item_id),
                    "status": status,
                    "title": item.title,
                }
            )

    def _emit_progress(self, payload: Dict[str, Any]) -> None:
        if self._progress_callback:
            self._progress_callback(payload)
