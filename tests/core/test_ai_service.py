"""Tests for AIService citation formatting and request flow."""

from __future__ import annotations

import json
from typing import Any

import pytest

from zoterorag.core.data.models import Chunk, Document
from zoterorag.core.services.ai_service import (
    AIService,
    AIServiceError,
    UnauthorizedAIServiceError,
)
from zoterorag.core.services.search_service import SearchMatch


class DummySettings:
    def __init__(self, key: str | None) -> None:
        self._key = key

    def get_chat_api_key(self) -> str | None:  # pragma: no cover - trivial
        return self._key


class FakeResponse:
    def __init__(self, ok: bool, status_code: int = 200, payload: dict[str, Any] | None = None, text: str = "") -> None:
        self.ok = ok
        self.status_code = status_code
        self._payload = payload or {}
        self.text = text

    def json(self) -> dict[str, Any]:
        return self._payload


class FakeSession:
    def __init__(self, responder):
        self._responder = responder
        self.requests = []

    def post(self, url, json=None, headers=None, timeout=None):
        self.requests.append({"url": url, "json": json, "headers": headers, "timeout": timeout})
        return self._responder(url, json, headers, timeout)


def _match() -> SearchMatch:
    return SearchMatch(
        chunk=Chunk(
            id=1,
            document_id=1,
            content="This is chunk content.",
            page_number=1,
            vector_id=5,
        ),
        document=Document(
            id=1,
            zotero_item_key="abc",
            title="Doc",
            authors=["A"],
            year=2024,
            pdf_file_path="/tmp/doc.pdf",
            indexed_at=None,  # type: ignore[arg-type]
        ),
        distance=0.1,
    )


def test_analyze_chunks_replaces_placeholders():
    def responder(url, json_payload, headers, timeout):
        content = (
            "Answer referencing [CHUNK_1]."
        )
        return FakeResponse(
            True,
            payload={
                "choices": [{"message": {"content": content}}],
                "usage": {"prompt_tokens": 3, "completion_tokens": 4},
            },
        )

    session = FakeSession(responder)
    service = AIService(
        DummySettings("key"),
        session_factory=lambda: session,
        model="test-model",
        base_url="https://example.com/v1",
    )
    result, usage = service.analyze_chunks("query", [_match()], top_n=5)
    assert "[1]" in result
    assert usage.tokens_used == 7
    # Verify payload chunk inclusion
    sent = session.requests[0]["json"]
    user_content = sent["messages"][1]["content"]
    assert "CHUNK_1" in user_content
    assert "chunk content" in user_content
    assert session.requests[0]["url"] == "https://example.com/v1/chat/completions"


def test_chat_returns_content_and_usage():
    def responder(url, json_payload, headers, timeout):
        assert json_payload["messages"][0]["role"] == "system"
        return FakeResponse(
            True,
            payload={
                "choices": [{"message": {"content": "hi"}}],
                "usage": {"prompt_tokens": 2, "completion_tokens": 3},
            },
        )

    service = AIService(
        DummySettings("key"),
        session_factory=lambda: FakeSession(responder),
        model="chat-model",
        base_url="https://example.com/v1",
    )
    reply, usage = service.chat(
        [
            {"role": "system", "content": "hello"},
            {"role": "user", "content": "hi"},
        ]
    )
    assert reply == "hi"
    assert usage.tokens_used == 5
    assert usage.prompt_tokens == 2
    assert usage.completion_tokens == 3


def test_missing_key_raises():
    service = AIService(DummySettings(None))
    with pytest.raises(UnauthorizedAIServiceError):
        service.analyze_chunks("q", [], top_n=1)


def test_error_response_raises():
    def responder(url, json_payload, headers, timeout):
        return FakeResponse(False, status_code=500, text="error")

    service = AIService(
        DummySettings("key"),
        session_factory=lambda: FakeSession(responder),
    )
    with pytest.raises(AIServiceError):
        service.analyze_chunks("q", [_match()], top_n=1)
