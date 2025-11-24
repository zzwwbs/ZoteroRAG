"""Lightweight benchmarking for PDF extraction backends.

Compares the production pypdfium2 extractor against an optional PyMuPDF baseline.
Measures elapsed time and peak memory (tracemalloc) across a set of PDFs.
"""

from __future__ import annotations

import argparse
import importlib
import tracemalloc
from pathlib import Path
from time import perf_counter
from typing import Callable, Iterable, List, Optional

try:  # Optional dependency; falls back to tracemalloc if absent.
    from memory_profiler import memory_usage  # type: ignore
except Exception:  # pragma: no cover - optional
    memory_usage = None  # type: ignore


def _extract_with_pypdfium2(path: Path) -> str:
    import pypdfium2 as pdfium  # type: ignore

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


def _extract_with_pymupdf(path: Path) -> str:
    fitz = importlib.import_module("fitz")  # PyMuPDF
    with fitz.open(path) as doc:
        parts = [page.get_text("text").strip() for page in doc]
        return "\n".join(part for part in parts if part)


def _measure(extractor: Callable[[Path], str], files: Iterable[Path]) -> dict:
    durations: List[float] = []
    peaks: List[int] = []
    errors: List[str] = []

    for pdf in files:
        start = perf_counter()
        peak_bytes = 0
        if memory_usage:
            try:
                # memory_usage returns a list of RSS samples (in MiB) when given a callable.
                samples = memory_usage((extractor, (pdf,), {}), max_usage=False)
                peak_bytes = int(max(samples) * 1024 * 1024) if samples else 0
            except Exception as exc:  # pragma: no cover - optional path
                errors.append(f"{pdf.name}: memory_profiler failed ({exc})")
        if not peak_bytes:
            tracemalloc.start()
            try:
                extractor(pdf)
            except Exception as exc:  # pragma: no cover - benchmark helper
                errors.append(f"{pdf.name}: {exc}")
            current, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            peak_bytes = peak
        durations.append(perf_counter() - start)
        peaks.append(peak_bytes)

    return {
        "avg_time_s": sum(durations) / len(durations) if durations else 0.0,
        "avg_peak_mb": (sum(peaks) / len(peaks) / (1024 * 1024)) if peaks else 0.0,
        "errors": errors,
        "samples": len(durations),
    }


def _load_pdfs(paths: Iterable[str]) -> list[Path]:
    files: list[Path] = []
    for raw in paths:
        p = Path(raw).expanduser()
        if p.is_dir():
            files.extend(sorted(p.glob("*.pdf")))
        elif p.suffix.lower() == ".pdf":
            files.append(p)
    return [p for p in files if p.is_file()]


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Benchmark PDF extraction backends.")
    parser.add_argument(
        "paths",
        nargs="+",
        help="PDF files or directories containing PDFs to benchmark (5+ recommended).",
    )
    parser.add_argument(
        "--no-baseline",
        action="store_true",
        help="Skip PyMuPDF baseline comparison.",
    )
    args = parser.parse_args(argv)

    pdfs = _load_pdfs(args.paths)
    if not pdfs:
        print("No PDF files found in provided paths.")
        return 1

    print(f"Benchmarking {len(pdfs)} PDFs")

    pdfium_results = _measure(_extract_with_pypdfium2, pdfs)
    print(
        f"[pypdfium2] avg_time={pdfium_results['avg_time_s']:.3f}s "
        f"avg_peak={pdfium_results['avg_peak_mb']:.2f} MB "
        f"errors={len(pdfium_results['errors'])}"
    )
    if pdfium_results["errors"]:
        for err in pdfium_results["errors"]:
            print(f"  error: {err}")

    if not args.no_baseline:
        try:
            importlib.import_module("fitz")
        except ImportError:
            print("[PyMuPDF] not installed; skipping baseline. Install PyMuPDF to compare.")
        else:
            pymupdf_results = _measure(_extract_with_pymupdf, pdfs)
            print(f"[PyMuPDF]   avg_time={pymupdf_results['avg_time_s']:.3f}s "
                  f"avg_peak={pymupdf_results['avg_peak_mb']:.2f} MB "
                  f"errors={len(pymupdf_results['errors'])}")
            if pymupdf_results["errors"]:
                for err in pymupdf_results["errors"]:
                    print(f"  error: {err}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
