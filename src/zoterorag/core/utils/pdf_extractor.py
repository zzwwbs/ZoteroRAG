"""Text extraction helpers for PDF documents."""

from __future__ import annotations

import logging
import os
import time
from pathlib import Path

try:  # pragma: no cover - import guard executed once
    import pypdfium2 as pdfium  # type: ignore
    from pypdfium2 import PdfiumError  # type: ignore
except ImportError:  # pragma: no cover
    pdfium = None  # type: ignore[assignment]
    PdfiumError = Exception  # type: ignore[misc,assignment]

logger = logging.getLogger(__name__)


def _is_profile_enabled() -> bool:
    """Return True when PDF extraction profiling is requested."""

    return os.environ.get("ZOTERORAG_PROFILE_PDF", "0") == "1"


def extract_text_from_pdf(pdf_path: Path | str) -> str:
    """Return the textual content from the provided PDF."""

    path = Path(pdf_path)
    if not path.exists():
        logger.error("PDF not found at %s", path)
        return ""

    if pdfium is None:
        logger.error("pypdfium2 is not installed. Unable to extract %s", path)
        return ""

    profile_enabled = _is_profile_enabled()
    start_time = time.perf_counter() if profile_enabled else 0.0
    total_pages = 0
    text_len = 0

    try:
        with pdfium.PdfDocument(path) as document:
            text_parts: list[str] = []
            total_pages = len(document)
            for page in document:
                text_page = page.get_textpage()
                text = (text_page.get_text_range() or "").strip()
                if text:
                    text_parts.append(text)
                text_page.close()
                page.close()

            full_text = "\n".join(text_parts)
            text_len = len(full_text)
            return full_text

    except FileNotFoundError as error:
        logger.error("Missing PDF while attempting to extract: %s", error)
    except PdfiumError as error:
        logger.error("Failed to extract text from %s: %s", path, error)
    except Exception:
        logger.exception("Failed to extract text from %s", path)
    finally:
        if profile_enabled:
            elapsed = (time.perf_counter() - start_time) * 1000
            logger.info(
                "PDF Profile: file=%s pages=%d len=%d elapsed=%.2fms",
                path.name,
                total_pages,
                text_len,
                elapsed,
            )

    return ""
