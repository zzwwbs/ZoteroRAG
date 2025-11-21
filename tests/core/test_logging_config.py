"""Tests for logging configuration."""

from __future__ import annotations

import logging
import os
from pathlib import Path

from zoterorag.core.utils.logging_config import configure_logging


def test_configure_logging_creates_file_and_writes(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("ZOTERORAG_DEBUG", "True")
    log_path = configure_logging(tmp_path)

    logging.getLogger(__name__).info("hello")
    logging.getLogger(__name__).debug("debug-msg")

    assert log_path.exists()
    content = log_path.read_text(encoding="utf-8")
    assert "hello" in content
    assert "DEBUG" in content or "INFO" in content
