"""Tests for EmbeddingClient."""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from zoterorag.config.settings_manager import AppSettings
from zoterorag.core.services.embedding_client import (
    EmbeddingClient,
    EmbeddingClientError,
    RateLimitEmbeddingError,
    UnauthorizedEmbeddingError,
)


class DummySettings:
    def __init__(self, api_key: str | None) -> None:
        self._settings = AppSettings(zotero_data_path=None, api_key=api_key)

    def get_api_key(self) -> str | None:
        return self._settings.api_key


class DummySession:
    def __init__(self) -> None:
        self.last_request = None
        self.response = SimpleNamespace(status_code=200, ok=True, json=lambda: {"data": [{"embedding": [0.1, 0.2]}]})

    def post(self, url, json, headers, timeout):
        self.last_request = {"url": url, "json": json, "headers": headers, "timeout": timeout}
        if isinstance(self.response, Exception):
            raise self.response
        return self.response


def build_client(api_key: str | None, session: DummySession) -> EmbeddingClient:
    settings = DummySettings(api_key)
    return EmbeddingClient(
        settings,
        base_url="https://example.com/v1",
        session_factory=lambda: session,
    )


def test_get_embedding_returns_vector(monkeypatch):
    session = DummySession()
    client = build_client("KEY", session)

    vector = client.get_embedding("hello")
    assert vector == [0.1, 0.2]
    assert session.last_request["json"]["input"] == ["hello"]


def test_authorization_header_sent():
    session = DummySession()
    client = build_client("SECRET", session)
    client.get_embedding("test")
    assert session.last_request["headers"]["Authorization"] == "Bearer SECRET"


def test_missing_api_key_raises():
    session = DummySession()
    client = build_client(None, session)
    with pytest.raises(UnauthorizedEmbeddingError):
        client.get_embedding("test")


def test_unauthorized_response_raises():
    session = DummySession()
    session.response = SimpleNamespace(status_code=401, ok=False, json=lambda: {"error": {"message": "bad key"}})
    client = build_client("bad", session)
    with pytest.raises(UnauthorizedEmbeddingError):
        client.get_embedding("chunk")


def test_rate_limit_response_raises():
    session = DummySession()
    session.response = SimpleNamespace(status_code=429, ok=False, json=lambda: {"error": {"message": "slow down"}})
    client = build_client("key", session)
    with pytest.raises(RateLimitEmbeddingError):
        client.get_embedding("chunk")


def test_network_error_wrapped(monkeypatch):
    import requests

    session = DummySession()
    session.response = requests.exceptions.ConnectionError("fail")
    client = build_client("key", session)
    with pytest.raises(EmbeddingClientError):
        client.get_embedding("chunk")
