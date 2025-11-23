# Project Source Tree

The project follows a standard Python monorepo structure, designed for clarity and maintainability. Below is an overview of the top-level directories and their purposes:

*   `.github/`: Contains GitHub Actions workflows for continuous integration and deployment.
*   `docs/`: Stores all project documentation, including the Product Requirements Document (PRD) and architectural specifications.
*   `scripts/`: Houses utility scripts for development tasks, such as building and releasing the application.
*   `src/`: The main source code directory for the ZoteroRAG Desk application.
*   `tests/`: Contains all unit, integration, and end-to-end tests for the application.
*   `.gitignore`: Specifies intentionally untracked files that Git should ignore.
*   `pyproject.toml`: Defines project metadata, dependencies, and build configurations (PEP 621).
*   `README.md`: The main project README file, providing an overview and quick start guide.

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
│   │   │   ├── main_window.py          # Main window with QTabWidget (Epic 6.1)
│   │   │   ├── search_tab.py           # "Search" tab with reorganized controls (Epic 9.1)
│   │   │   ├── index_tab.py            # "Index" tab with status column and summary (Epic 8)
│   │   │   ├── analysis_tab.py         # "AI Analysis" tab, now an interactive chat interface (Epic 7)
│   │   │   ├── settings_tab.py         # "Settings" tab
│   │   │   ├── chunk_detail_dialog.py  # Non-modal chunk viewer (Epic 6.4)
│   │   │   ├── onboarding_view.py      # Initial setup screen
│   │   │   ├── assets/                 # UI assets like icons, images, etc.
│   │   │   └── widgets/                # Reusable custom widgets (TokenUsage is now a controller)
│   │   │       ├── __init__.py
│   │   │       └── ...
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
