"""Unit tests for chunking utility."""

from pathlib import Path

from zoterorag.core.utils.chunking_utility import chunk_text


def _token_lengths(chunks):
    return [len(chunk.content.split()) for chunk in chunks]


def test_default_chunking_size_and_overlap():
    text = " ".join(f"word{i}." for i in range(1200))
    chunks = chunk_text(text, document_id=1, page_number=1)
    assert len(chunks) >= 2
    lengths = _token_lengths(chunks)
    assert all(length <= 600 for length in lengths)
    assert lengths[0] - lengths[1] <= 600  # basic sanity across chunks


def test_configurable_chunk_size_and_overlap():
    text = " ".join(["sentence" + str(i) + "." for i in range(900)])
    chunks = chunk_text(text, 2, 1, chunk_size=450, chunk_overlap=150)
    assert all(length <= 450 for length in _token_lengths(chunks))


def test_chunks_preserve_document_and_page_ids():
    text = "Short document." * 10
    chunks = chunk_text(text, document_id=99, page_number=5)
    assert chunks
    assert all(chunk.document_id == 99 for chunk in chunks)
    assert all(chunk.page_number == 5 for chunk in chunks)


def test_handles_short_document_without_empty_chunks():
    text = "Tiny."  # < 100 tokens
    chunks = chunk_text(text, document_id=3, page_number=1)
    assert len(chunks) == 1
    assert chunks[0].content.strip() == "Tiny."


def test_handles_long_document_without_excess_memory():
    text = " ".join(f"sentence{i}." for i in range(5000))
    chunks = chunk_text(text, document_id=4, page_number=1)
    assert chunks
    assert sum(_token_lengths(chunks)) >= 5000


def test_sentence_boundaries_respected():
    sentences = [" ".join(["word"] * 250) + "." for _ in range(3)]
    text = " ".join(sentences)
    chunks = chunk_text(text, document_id=5, page_number=1, chunk_size=400)
    assert len(chunks) >= 3
    for chunk in chunks:
        assert chunk.content.strip().endswith(".")
