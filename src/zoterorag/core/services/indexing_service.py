"""Indexing orchestration that relies on Zotero data and PDF extraction."""

from __future__ import annotations

import logging
from typing import Callable, Dict, Iterable

from ..utils.pdf_extractor import extract_text_from_pdf
from .zotero_manager import ZoteroManager

logger = logging.getLogger(__name__)


class IndexingService:
    """Coordinates pulling Zotero items and extracting their textual content."""

    def __init__(
        self,
        zotero_manager: ZoteroManager,
        pdf_extractor: Callable[[str], str] = extract_text_from_pdf,
    ) -> None:
        self._zotero_manager = zotero_manager
        self._pdf_extractor = pdf_extractor

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
