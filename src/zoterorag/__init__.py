"""Entry point helpers for the Zotero RAG desktop application."""

def main() -> int:
    """Lazy-load the application entry point to avoid GUI imports during testing."""

    from .main import main as _main_func

    return _main_func()


__all__ = ["main"]
