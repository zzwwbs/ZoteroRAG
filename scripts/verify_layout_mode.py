"""Quick-and-dirty timing helper for pypdfium2 text extraction."""

from __future__ import annotations

import time
from pathlib import Path

import pypdfium2 as pdfium


def benchmark(name: str) -> None:
    path = Path("tests/test.pdf")
    start = time.perf_counter()
    with pdfium.PdfDocument(path) as doc:
        for page in doc:
            text_page = page.get_textpage()
            text_page.get_text_range()
            text_page.close()
            page.close()
    print(f"{name}: {time.perf_counter() - start:.4f}s")


if __name__ == "__main__":
    benchmark("pypdfium2 get_text_range")
