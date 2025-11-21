"""Central logging configuration for ZoteroRAG."""

from __future__ import annotations

import logging
import os
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from pathlib import Path


def configure_logging(data_dir: Path | None = None) -> Path:
    """Configure root logging; returns the log file path."""

    log_dir = (data_dir or Path.home() / ".zotero_rag").expanduser()
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "debug.log"

    level = logging.DEBUG if os.getenv("ZOTERORAG_DEBUG") == "True" else logging.INFO
    fmt = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"

    # Size-based rotation; retain 7 backups for roughly a week; combine with timed rotation at midnight.
    file_handler = RotatingFileHandler(log_file, maxBytes=10 * 1024 * 1024, backupCount=7, encoding="utf-8")
    file_handler.setFormatter(logging.Formatter(fmt))
    file_handler.setLevel(level)

    root = logging.getLogger()
    root.setLevel(level)
    root.handlers.clear()
    root.addHandler(file_handler)

    console = logging.StreamHandler()
    console.setFormatter(logging.Formatter(fmt))
    console.setLevel(level)
    root.addHandler(console)

    return log_file
