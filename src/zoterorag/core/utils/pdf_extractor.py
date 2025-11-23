"""Text extraction helpers for PDF documents."""

from __future__ import annotations

import logging
from pathlib import Path

try:  # pragma: no cover - import guard executed once
    import pdfplumber  # type: ignore
except ImportError:  # pragma: no cover
    pdfplumber = None  # type: ignore[assignment]

logger = logging.getLogger(__name__)


def extract_text_from_pdf(pdf_path: Path | str) -> str:
    """Return the textual content from the provided PDF."""

    path = Path(pdf_path)
    if not path.exists():
        logger.error("PDF not found at %s", path)
        return ""

    if pdfplumber is None:
        logger.error("pdfplumber is not installed. Unable to extract %s", path)
        return ""

    try:
        with pdfplumber.open(path) as document:
            text_parts = []
            for page in document.pages:
                text = page.extract_text() or ""
                text = text.strip()
                if text:
                    text_parts.append(text)
            return "\n".join(text_parts)
    except FileNotFoundError as error:
        logger.error("Missing PDF while attempting to extract: %s", error)
    except Exception:
        logger.exception("Failed to extract text from %s", path)

    return ""
