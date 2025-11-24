# 4. Technical Assumptions

## 4.1. Repository Structure: Monorepo

For a standalone desktop application, a monorepo structure is assumed. This simplifies dependency management, build processes, and code sharing between different components of the application (e.g., core logic, GUI).

## 4.2. Service Architecture: Monolith

The MVP will be built as a monolithic desktop application. This aligns with the project brief's statement that "A monolithic desktop application structure is sufficient for the MVP." This approach simplifies deployment and reduces initial architectural complexity.

## 4.3. Testing Requirements: Unit + Integration

Testing will include both unit tests for individual components and integration tests to ensure that different parts of the application (e.g., PDF extraction, Zotero integration, vector DB interaction) work correctly together. This provides a balanced approach to quality assurance for a desktop application.

## 4.4. Additional Technical Assumptions and Requests

*   **Language:** Python 3.13+
*   **GUI Framework:** PySide6
*   **PDF Extraction Library:** pypdfium2
*   **Cloud Embedding API:** OpenAI embeddings as default, with the ability for users to configure other compatible API endpoints.
*   **Local Vector Database:** FAISS
*   **Local Metadata Storage:** SQLite (for storing chunk metadata and Zotero item information, complementing FAISS for vector storage)
*   **LLM Integration (BYOK):** OpenAI Chat/Responses API (or similar, configurable by user)
*   **Packaging:** Self-contained installers/bundles for Windows, macOS, and Linux (e.g., using PyInstaller or similar tools)
*   **API Key Storage:** Secure local storage of API keys, using OS-specific credential management systems (keyring library).
