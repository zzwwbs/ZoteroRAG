"""Text extraction helpers for PDF documents."""

from __future__ import annotations

import logging
from pathlib import Path

try:  # pragma: no cover - import guard executed once
    import fitz  # type: ignore
except ImportError:  # pragma: no cover
    fitz = None  # type: ignore[assignment]

logger = logging.getLogger(__name__)


def extract_text_from_pdf(pdf_path: Path | str) -> str:
    """Return the textual content from the provided PDF."""

    path = Path(pdf_path)
    if not path.exists():
        logger.error("PDF not found at %s", path)
        return ""

    if fitz is None:
        logger.error("PyMuPDF is not installed. Unable to extract %s", path)
        return ""

    try:
        with fitz.open(path) as document:
            text_parts = [page.get_text("text") for page in document]
            return "\n".join(part.strip() for part in text_parts if part.strip())
    except FileNotFoundError as error:
        logger.error("Missing PDF while attempting to extract: %s", error)
    except Exception:
        logger.exception("Failed to extract text from %s", path)

    return ""
