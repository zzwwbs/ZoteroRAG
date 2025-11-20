# Architectural Decision Log

This log records key architectural decisions and their rationale.

| Decision ID | Decision | Rationale |
| :--- | :--- | :--- |
| AD-01 | **Monolithic Desktop Application** | Aligns with PRD (4.2) and project goals. Simplifies development, deployment, and maintenance for a single-user, local-first utility. Avoids the complexity of a client-server architecture. |
| AD-02 | **Python with PySide6** | Explicitly required by the PRD (4.4). Python is excellent for data processing and scripting, while PySide6 provides a mature, cross-platform GUI framework with strong native integration. |
| AD-03 | **FAISS + SQLite for Local Index** | Explicitly required by the PRD (4.4). This combination is powerful: FAISS provides extremely fast vector search, while SQLite is a robust, lightweight, and ubiquitous solution for storing the structured metadata (documents, chunks) associated with the vectors. |
| AD-04 | **Repository Pattern for Data Access** | Decouples business logic (services) from the data storage implementation (SQLite). This makes the code more modular, easier to test (by mocking repositories), and easier to maintain or migrate in the future. |
| AD-05 | **Service Layer for Core Logic** | Encapsulates business logic into distinct service classes (`IndexingService`, `SearchService`). This improves separation of concerns, making the system easier to understand, test, and refactor. |
| AD-06 | **`keyring` for API Key Storage** | Fulfills the security requirement (NFR3) for secure, encrypted storage of secrets. It abstracts away platform-specific details, providing a single, secure interface for all target operating systems. |
| AD-07 | **`QThreadPool` for Background Tasks** | Fulfills the non-functional requirement for a responsive UI during long-running tasks like indexing (NFR5). It is the standard, idiomatic way to handle background processing in a Qt/PySide6 application. |
