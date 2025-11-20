"""Tests for the PDF extraction utility."""

from pathlib import Path
from types import SimpleNamespace

from zoterorag.core.utils import pdf_extractor
from zoterorag.core.utils.pdf_extractor import extract_text_from_pdf


def _install_fake_fitz(monkeypatch, text: str) -> None:
    class DummyPage:
        def __init__(self, contents: str) -> None:
            self._contents = contents

        def get_text(self, *_args, **_kwargs) -> str:
            return self._contents

    class DummyDocument:
        def __init__(self) -> None:
            self._pages = [DummyPage(text)]

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):  # pragma: no cover - trivial
            return False

        def __iter__(self):
            return iter(self._pages)

    monkeypatch.setattr(
        pdf_extractor,
        "fitz",
        SimpleNamespace(open=lambda _path: DummyDocument()),
    )


def test_extract_text_from_pdf_returns_expected_string(tmp_path: Path, monkeypatch) -> None:
    pdf_path = tmp_path / "sample.pdf"
    pdf_path.write_text("placeholder")
    _install_fake_fitz(monkeypatch, "Hello Zotero")

    extracted = extract_text_from_pdf(pdf_path)
    assert "Hello Zotero" in extracted


def test_extract_text_handles_missing_file(tmp_path: Path) -> None:
    missing = tmp_path / "missing.pdf"
    extracted = extract_text_from_pdf(missing)
    assert extracted == ""
