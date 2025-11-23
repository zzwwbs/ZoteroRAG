"""Tests for the PDF extraction utility."""

from pathlib import Path
from types import SimpleNamespace

from zoterorag.core.utils import pdf_extractor
from zoterorag.core.utils.pdf_extractor import extract_text_from_pdf


def _install_fake_pdfplumber(monkeypatch, text: str) -> None:
    class DummyPage:
        def __init__(self, contents: str) -> None:
            self._contents = contents

        def extract_text(self) -> str:
            return self._contents

    class DummyDocument:
        def __init__(self) -> None:
            self.pages = [DummyPage(text)]

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):  # pragma: no cover - trivial
            return False

    monkeypatch.setattr(
        pdf_extractor,
        "pdfplumber",
        SimpleNamespace(open=lambda _path: DummyDocument()),
    )


def test_extract_text_from_pdf_returns_expected_string(tmp_path: Path, monkeypatch) -> None:
    pdf_path = tmp_path / "sample.pdf"
    pdf_path.write_text("placeholder")
    _install_fake_pdfplumber(monkeypatch, "Hello Zotero")

    extracted = extract_text_from_pdf(pdf_path)
    assert "Hello Zotero" in extracted


def test_extract_text_handles_missing_file(tmp_path: Path) -> None:
    missing = tmp_path / "missing.pdf"
    extracted = extract_text_from_pdf(missing)
    assert extracted == ""


def test_extract_text_logs_and_continues_on_error(tmp_path: Path, monkeypatch, caplog) -> None:
    pdf_path = tmp_path / "broken.pdf"
    pdf_path.write_text("placeholder")

    def _boom(_path):
        raise ValueError("broken pdf")

    monkeypatch.setattr(
        pdf_extractor,
        "pdfplumber",
        SimpleNamespace(open=_boom),
    )

    with caplog.at_level("ERROR"):
        extracted = extract_text_from_pdf(pdf_path)

    assert extracted == ""
    assert any("Failed to extract text from" in rec.message for rec in caplog.records)
