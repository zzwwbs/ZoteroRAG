"""Utility for splitting extracted text into overlapping chunks."""

from __future__ import annotations

import re
from typing import Iterable, List

from ..data.models import Chunk

DEFAULT_CHUNK_SIZE = 600
DEFAULT_CHUNK_OVERLAP = 100
MIN_CHUNK_SIZE = 400
MAX_CHUNK_SIZE = 1000
MIN_OVERLAP = 50
MAX_OVERLAP = 200


def chunk_text(
    text: str,
    document_id: int,
    page_number: int,
    *,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> list[Chunk]:
    """Split text into overlapping chunks suitable for embeddings.

    Args:
        text: Full text extracted from a PDF page/document section.
        document_id: Identifier of the parent document.
        page_number: Page number associated with the text.
        chunk_size: Target number of tokens per chunk (clamped to 400-1000).
        chunk_overlap: Number of overlapping tokens between consecutive chunks
            (clamped to 50-200).

    Returns:
        A list of `Chunk` objects ready for persistence and embedding creation.
    """

    normalized_text = text.strip()
    if not normalized_text:
        return []

    chunk_size = _clamp(chunk_size, MIN_CHUNK_SIZE, MAX_CHUNK_SIZE)
    chunk_overlap = _clamp(chunk_overlap, MIN_OVERLAP, MAX_OVERLAP)
    chunk_overlap = min(chunk_overlap, chunk_size // 2)

    sentences = _split_sentences(normalized_text)
    chunk_strings: list[str] = []
    current_sentences: list[str] = []
    current_tokens = 0

    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
        sentence_tokens = _token_count(sentence)

        if sentence_tokens >= chunk_size:
            current_tokens, current_sentences = _flush_if_needed(
                current_sentences, chunk_strings, chunk_overlap
            )
            _append_long_sentence_chunks(
                sentence, chunk_size, chunk_overlap, chunk_strings
            )
            current_sentences = []
            current_tokens = 0
            continue

        if current_tokens and current_tokens + sentence_tokens > chunk_size:
            current_tokens, current_sentences = _flush_if_needed(
                current_sentences, chunk_strings, chunk_overlap
            )

        current_sentences.append(sentence)
        current_tokens += sentence_tokens

    if current_sentences:
        chunk_strings.append(" ".join(current_sentences).strip())

    return [
        Chunk(
            document_id=document_id,
            content=chunk_text,
            page_number=page_number,
        )
        for chunk_text in chunk_strings
        if chunk_text
    ]


def _flush_if_needed(
    current_sentences: list[str],
    chunk_strings: list[str],
    chunk_overlap: int,
) -> tuple[int, list[str]]:
    if not current_sentences:
        return 0, []

    chunk_strings.append(" ".join(current_sentences).strip())
    overlap_sentences = _retain_overlap(current_sentences, chunk_overlap)
    overlap_tokens = sum(_token_count(sentence) for sentence in overlap_sentences)
    return overlap_tokens, overlap_sentences.copy()


def _retain_overlap(sentences: list[str], overlap_tokens: int) -> list[str]:
    if overlap_tokens <= 0:
        return []

    retained: list[str] = []
    token_total = 0
    for sentence in reversed(sentences):
        retained.append(sentence)
        token_total += _token_count(sentence)
        if token_total >= overlap_tokens:
            break
    return list(reversed(retained))


def _append_long_sentence_chunks(
    sentence: str,
    chunk_size: int,
    chunk_overlap: int,
    chunk_strings: list[str],
) -> None:
    tokens = sentence.split()
    if not tokens:
        return

    start = 0
    while start < len(tokens):
        end = min(start + chunk_size, len(tokens))
        chunk_tokens = tokens[start:end]
        chunk_strings.append(" ".join(chunk_tokens).strip())
        if end == len(tokens):
            break
        start = max(end - chunk_overlap, 0)


def _split_sentences(text: str) -> list[str]:
    pattern = re.compile(r"(?<=[.!?])\s+")
    sentences = pattern.split(text)
    if len(sentences) == 1:
        return [text]
    return sentences


def _token_count(sentence: str) -> int:
    return len(sentence.split())


def _clamp(value: int, min_value: int, max_value: int) -> int:
    return max(min_value, min(max_value, value))
