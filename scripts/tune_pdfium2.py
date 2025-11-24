"""Micro-benchmark helper for tuning pypdfium2 text extraction."""

from __future__ import annotations

import time
from pathlib import Path

import pypdfium2 as pdfium


def benchmark_extraction(path: Path) -> float:
    start = time.perf_counter()
    with pdfium.PdfDocument(path) as doc:
        for page in doc:
            text_page = page.get_textpage()
            text_page.get_text_range()
            text_page.close()
            page.close()
    return time.perf_counter() - start


def main() -> None:
    pdf_path = Path("tests/test.pdf")
    if not pdf_path.exists():
        print(f"Missing PDF at {pdf_path}")
        return

    print(f"Benchmarking {pdf_path}")
    print(f"Baseline (get_text_range): {benchmark_extraction(pdf_path):.4f}s")


if __name__ == "__main__":
    main()
