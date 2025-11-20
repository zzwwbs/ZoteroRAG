# Tech Stack

## Technology Stack Table

| Category | Technology | Version | Purpose | Rationale |
| :--- | :--- | :--- | :--- | :--- |
| Frontend Language | Python | 3.13+ | Primary language for the entire application. | Explicitly stated in PRD. |
| Frontend Framework | PySide6 | Latest Stable | GUI framework for cross-platform desktop application. | Explicitly stated in PRD. |
| UI Component Library | PySide6 Widgets | Latest Stable | Native UI components provided by PySide6. | Integrated with PySide6, provides native look and feel. |
| State Management | Internal Event/Observer Pattern | N/A | Manage application state and UI updates within the desktop app. | Simple, effective for monolithic desktop apps, avoids external dependencies. |
| Backend Language | Python | 3.13+ | Primary language for all core logic. | Explicitly stated in PRD. |
| Backend Framework | N/A - Integrated Logic | N/A | Core logic is integrated directly into the desktop application, not a separate server. | Monolithic desktop application architecture. |
| API Style | Internal Python API / External REST | N/A | Internal: Python function calls between GUI and core logic. External: REST for cloud embeddings. | Standard approach for desktop apps; external for specified cloud services. |
| Database | SQLite | Latest Stable | Local storage for Zotero DB (read-only) and application metadata. | Explicitly stated in PRD; lightweight, embedded, local-first. |
| Database | FAISS | Latest Stable | Local vector database for semantic search. | Explicitly stated in PRD; efficient similarity search. |
| Cache | N/A | N/A | Local-first design with direct data access minimizes need for separate caching layer. | Simplicity for MVP. |
| File Storage | Local File System | N/A | Storing PDFs, application data, and index files. | Core to local-first, privacy-centric design. |
| Authentication | BYOK API Key (External) | N/A | User-provided API key for external cloud services, stored securely. | PRD requirement for optional cloud features. |
| Frontend Testing | Pytest / PySide6 Test Utils | Latest Stable | Unit and integration testing for GUI components and interactions. | Standard Python testing framework with GUI-specific extensions. |
| Backend Testing | Pytest | Latest Stable | Unit and integration testing for core logic and data access. | Standard, flexible, and widely adopted Python testing framework. |
| E2E Testing | Pytest + UI Automation Library (e.g., `pytest-qt`) | Latest Stable | End-to-end testing of the full application workflow. | Ensures full system functionality across UI and logic. |
| Build Tool | PyInstaller | Latest Stable | Packaging Python application into standalone executables. | Explicitly stated in PRD for cross-platform distribution. |
| Bundler | PyInstaller | Latest Stable | Handles bundling Python dependencies and assets. | Integrated with PyInstaller for self-contained executables. |
| IaC Tool | N/A | N/A | Desktop application, no cloud infrastructure to manage via IaC. | Local-first architecture. |
| CI/CD | GitHub Actions | N/A | Automated build, test, and packaging for cross-platform releases. | Common, flexible, and free for open-source projects. |
| Monitoring | Python `logging` module | N/A | Local application logging for diagnostics and error tracking. | Simple, built-in, and sufficient for a desktop application. |
| Logging | Python `logging` module | N/A | Structured logging with levels (DEBUG, INFO, WARNING, ERROR, CRITICAL). Logs stored in app data directory with rotation (10MB max, 7-day retention). | Standard, flexible, and widely adopted Python logging. |
| CSS Framework | N/A (Qt Styling Sheets) | N/A | PySide6 uses Qt Styling Sheets for UI customization, not traditional web CSS frameworks. | Native GUI framework approach. |
