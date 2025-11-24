#!/usr/bin/env python3
"""
Test sequential vs threaded PDF extraction performance with pypdfium2.
"""

from __future__ import annotations

import time
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from pathlib import Path
from typing import Tuple

import pypdfium2 as pdfium


def extract_sequential(path: Path) -> str:
    """Current implementation - sequential page extraction."""

    with pdfium.PdfDocument(path) as doc:
        parts: list[str] = []
        for page in doc:
            text_page = page.get_textpage()
            text = (text_page.get_text_range() or "").strip()
            if text:
                parts.append(text)
            text_page.close()
            page.close()
        return "\n".join(parts)


def extract_page(path: Path, page_num: int) -> Tuple[int, str]:
    """Extract text from a single page (for parallel processing)."""

    try:
        with pdfium.PdfDocument(path) as doc:
            page = doc[page_num]
            text_page = page.get_textpage()
            text = (text_page.get_text_range() or "").strip()
            text_page.close()
            page.close()
            return (page_num, text)
    except Exception as exc:
        print(f"Error extracting page {page_num}: {exc}")
        return (page_num, "")


def extract_parallel_thread(path: Path, max_workers: int = 4) -> str:
    """Parallel extraction using ThreadPoolExecutor."""

    with pdfium.PdfDocument(path) as doc:
        num_pages = len(doc)

    with ThreadPoolExecutor(max_workers=max_workers) as tpe:
        results = list(tpe.map(partial(extract_page, path), range(num_pages)))

    results.sort(key=lambda x: x[0])
    parts = [text for _, text in results if text]
    return "\n".join(parts)


def main() -> None:
    pdf_path = Path("tests/test.pdf")

    if not pdf_path.exists():
        print(f"Error: {pdf_path} not found")
        return

    print(f"Testing PDF extraction on: {pdf_path}")
    print()

    # Get page count
    with pdfium.PdfDocument(pdf_path) as doc:
        num_pages = len(doc)
    print(f"PDF has {num_pages} pages")
    print()

    # Test sequential extraction
    print("1. SEQUENTIAL (current implementation):")
    start = time.perf_counter()
    text_seq = extract_sequential(pdf_path)
    elapsed_seq = time.perf_counter() - start
    print(f"   Time: {elapsed_seq:.3f}s")
    print(f"   Text length: {len(text_seq):,} chars")
    print()

    # Test parallel with different worker counts
    for workers in [2, 4, 8]:
        print(f"{workers}. PARALLEL with ThreadPoolExecutor ({workers} workers):")
        start = time.perf_counter()
        text_parallel = extract_parallel_thread(pdf_path, max_workers=workers)
        elapsed_parallel = time.perf_counter() - start
        print(f"   Time: {elapsed_parallel:.3f}s")
        print(f"   Text length: {len(text_parallel):,} chars")

        speedup = elapsed_seq / elapsed_parallel if elapsed_parallel else 0.0
        print(f"   Speedup: {speedup:.2f}x", end="")
        if speedup > 1.1:
            print(" ✅ (faster)")
        elif speedup < 0.9:
            print(" ❌ (slower)")
        else:
            print(" ≈ (similar)")

        if text_seq == text_parallel:
            print("   Verification: ✅ Output matches sequential")
        else:
            print("   Verification: ❌ Output differs from sequential!")
        print()

    # Summary
    print("=" * 60)
    print("SUMMARY:")
    print(f"Sequential baseline: {elapsed_seq:.3f}s")
    print()
    print("ANALYSIS:")
    print("pypdfium2 performs extraction in C/C++; Python threads may not help much.")
    print("ThreadPoolExecutor overhead can outweigh benefits unless PDFs are large.")
    print()
    print("RECOMMENDATION:")
    print("✅ Stick with sequential extraction unless profiling shows thread-safe gains.")
    print("✅ Focus on I/O (fast disks) and batching upstream embedding requests.")


if __name__ == "__main__":
    main()
