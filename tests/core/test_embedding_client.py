"""Unit tests for the EmbeddingClient behavior."""

from __future__ import annotations

import pytest

from zoterorag.core.services.embedding_client import (
    EmbeddingClient,
    EmbeddingClientError,
    RateLimitEmbeddingError,
    UnauthorizedEmbeddingError,
)


class DummySettings:
    def __init__(self, api_key: str | None) -> None:
        self._api_key = api_key

    def get_api_key(self) -> str | None:  # pragma: no cover - trivial accessor
        return self._api_key


class FakeResponse:
    def __init__(self, ok: bool, status_code: int = 200, json_data: dict | None = None, text: str = "") -> None:
        self.ok = ok
        self.status_code = status_code
        self._json_data = json_data or {}
        self.text = text

    def json(self) -> dict:
        return self._json_data


class FakeSession:
    def __init__(self, responder):
        self._responder = responder

    def post(self, url, json=None, headers=None, timeout=None):
        return self._responder(url, json, headers, timeout)


def test_get_embedding_success_returns_vector():
    payload = {"data": [{"embedding": [0.1, 0.2, 0.3]}]}

    def responder(url, json, headers, timeout):
        return FakeResponse(True, json_data=payload)

    client = EmbeddingClient(
        settings_manager=DummySettings("abc123"),
        session_factory=lambda: FakeSession(responder),
    )

    result = client.get_embedding("hello world")
    assert result == [0.1, 0.2, 0.3]


def test_missing_api_key_raises():
    client = EmbeddingClient(
        settings_manager=DummySettings(None),
        session_factory=lambda: FakeSession(lambda *_: FakeResponse(True)),
    )

    with pytest.raises(UnauthorizedEmbeddingError):
        client.get_embedding("hello")


def test_rate_limit_error_raises():
    def responder(url, json, headers, timeout):
        return FakeResponse(
            ok=False,
            status_code=429,
            json_data={"error": {"message": "Rate limit exceeded"}},
        )

    client = EmbeddingClient(
        settings_manager=DummySettings("key"),
        session_factory=lambda: FakeSession(responder),
    )

    with pytest.raises(RateLimitEmbeddingError):
        client.get_embedding("rate limit")


def test_unexpected_error_bubbles_as_embedding_error():
    def responder(url, json, headers, timeout):
        return FakeResponse(
            ok=False,
            status_code=500,
            json_data={"error": {"message": "Internal error"}},
        )

    client = EmbeddingClient(
        settings_manager=DummySettings("key"),
        session_factory=lambda: FakeSession(responder),
    )

    with pytest.raises(EmbeddingClientError):
        client.get_embedding("server error")
