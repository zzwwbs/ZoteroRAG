# Unified Project Structure

```plaintext
zotero-rag-desk/
├── .github/                    # CI/CD workflows
│   └── workflows/
│       └── ci.yaml             # GitHub Actions for build, test, and packaging
├── docs/                       # Project documentation
│   ├── prd.md
│   └── architecture.md
├── scripts/                    # Helper scripts for development and release
│   ├── build.py                # Script to run PyInstaller for all platforms
│   └── release.py              # Script to create GitHub releases
├── src/                        # Main source code directory
│   ├── zoterorag/              # The main application Python package
│   │   ├── __init__.py
│   │   ├── __main__.py         # Main entry point to launch the application
│   │   │
│   │   ├── core/               # "Backend" - Core application logic
│   │   │   ├── __init__.py
│   │   │   ├── services/       # Business logic (Indexing, Search, AI)
│   │   │   │   ├── __init__.py
│   │   │   │   ├── indexing_service.py
│   │   │   │   ├── search_service.py
│   │   │   │   └── ...
│   │   │   ├── data/           # Data models and data access layer
│   │   │   │   ├── __init__.py
│   │   │   │   ├── models.py       # Python dataclasses for Document, Chunk, etc.
│   │   │   │   └── repositories.py # Repository classes for DB interaction
│   │   │   └── utils/          # Core utility functions (e.g., chunking)
│   │   │
│   │   ├── ui/                 # "Frontend" - PySide6 UI components
│   │   │   ├── __init__.py
│   │   │   ├── main_window.py  # Main application window
│   │   │   ├── search_view.py
│   │   │   ├── settings_dialog.py
│   │   │   ├── onboarding_view.py
│   │   │   └── assets/         # UI assets like icons, images, etc.
│   │   │
│   │   └── config/             # Application configuration and settings management
│   │       ├── __init__.py
│   │       └── settings_manager.py
│   │
│   └── tests/                    # Tests for the application
│       ├── __init__.py
│       ├── core/                 # Tests for core logic services and data layer
│       │   └── test_indexing_service.py
│       └── ui/                   # Tests for UI components and interactions
│           └── test_main_window.py
│
├── .gitignore
├── pyproject.toml              # Project metadata, dependencies, and build config (PEP 621)
└── README.md
```
