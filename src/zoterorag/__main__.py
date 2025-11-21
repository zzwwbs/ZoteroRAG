"""This module allows the package to be executed with python -m zoterorag."""

from __future__ import annotations

import logging
import sys
import traceback

from PySide6.QtWidgets import QApplication, QMessageBox

from zoterorag.core.utils.logging_config import configure_logging
from zoterorag.main import main


def _global_exception_hook(exc_type, exc_value, exc_traceback):
    logging.error(
        "Uncaught exception",
        exc_info=(exc_type, exc_value, exc_traceback),
    )
    app = QApplication.instance() or QApplication([])
    QMessageBox.critical(
        None,
        "Unexpected Error",
        "An unexpected error occurred and has been logged. Please restart the application.",
    )


if __name__ == "__main__":
    configure_logging()
    sys.excepthook = _global_exception_hook
    raise SystemExit(main())
