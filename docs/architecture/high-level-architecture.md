# High Level Architecture

## Technical Summary

ZoteroRAG Desk is architected as a **monolithic, cross-platform desktop application** designed to run locally on the user's machine (Windows, macOS, and Linux). The architecture prioritizes privacy and safety by keeping all user data, including the semantic index, on the local file system. The user interface is built with **PySide6**, and the core application logic is written in **Python**. These two layers operate within a single process, ensuring a simple and responsive user experience. Cloud services, specifically an OpenAI-compatible API, are used only on an opt-in, Bring-Your-Own-Key (BYOK) basis for embedding generation and AI synthesis, ensuring no user data is processed without explicit consent.

## Platform and Infrastructure Choice

The application follows a **local-first** paradigm. The primary platform is the user's own desktop computer.

*   **Platform:** User's local machine (Windows, macOS, Linux).
*   **Key Services (Local):**
    *   **File System:** For storing the application, its configuration, and the generated index.
    *   **SQLite:** For reading the Zotero database and storing local metadata for text chunks.
    *   **FAISS:** For storing and searching local vector embeddings.
    *   **OS Credential Manager:** For securely storing the user's API key.
*   **Key Services (Cloud):**
    *   **OpenAI-compatible API:** For generating text embeddings and performing AI synthesis (BYOK).
*   **Deployment Host and Regions:** Not applicable, as the application is deployed and runs directly on the user's machine.

## Repository Structure

As specified in the PRD, the project will use a **monorepo** structure. This simplifies dependency management and the build process for the monolithic desktop application.

*   **Structure:** Monorepo (single Git repository).
*   **Monorepo Tool:** Not applicable (Python-native project structure is sufficient).
*   **Package Organization:** The code will be organized into logical packages within a `src` directory, separating concerns like `ui`, `core_logic`, `data_access`, and `services`.

## High Level Architecture Diagram

```mermaid
graph TD
    subgraph User's Machine
        User -- Interacts with --> App_GUI[Desktop App GUI<br>(PySide6)]

        subgraph ZoteroRAG Desk Application
            App_GUI -- Calls --> Core_Logic[Core Logic<br>(Python Services)]
            Core_Logic -- Manages --> Indexing_Service[Indexing Service]
            Core_Logic -- Manages --> Search_Service[Search Service]
            Core_Logic -- Manages --> Analysis_Service[AI Analysis Service]
        end

        subgraph Local Data Storage
            Indexing_Service -- Reads --> Zotero_DB[Zotero DB<br>(zotero.sqlite)]
            Indexing_Service -- Reads --> PDFs[PDF Files<br>(storage/)]
            Indexing_Service -- Writes to --> Metadata_DB[Metadata DB<br>(SQLite)]
            Indexing_Service -- Writes to --> Vector_DB[Vector Index<br>(FAISS)]

            Search_Service -- Reads from --> Metadata_DB
            Search_Service -- Reads from --> Vector_DB
        end
    end

    subgraph Cloud (Optional, BYOK)
        Analysis_Service -- Sends Query + Chunks --> OpenAI_API[OpenAI-compatible API]
        Indexing_Service -- Sends Chunks --> OpenAI_API
        OpenAI_API -- Returns Embeddings/Analysis --> Core_Logic
    end

    style Zotero_DB fill:#f9f,stroke:#333,stroke-width:2px
    style PDFs fill:#f9f,stroke:#333,stroke-width:2px
```

## Architectural Patterns

*   **Monolithic Desktop Application:** The entire application is a single, self-contained unit.
    *   *Rationale:* Simplifies development, deployment, and maintenance for a local-first utility, as specified in the PRD.
*   **Model-View-Controller (MVC):** The UI (View) will be separated from the business logic (Controller) and data (Model).
    *   *Rationale:* This classic pattern promotes separation of concerns within the monolithic structure, making the PySide6 GUI code more maintainable and testable.
*   **Service Layer:** Business logic for indexing, searching, and analysis will be encapsulated in dedicated service classes.
    *   *Rationale:* Decouples the core logic from the UI and data access layers, improving modularity.
*   **Repository Pattern:** Data access for all local storage (Zotero DB, Metadata DB, FAISS index) will be abstracted behind repository classes.
    *   *Rationale:* Isolates data storage details, allowing for easier testing (mocks) and potential future changes to the storage mechanism.

*   **Secure Storage:** The primary security concern is the user's API key. This will be handled exclusively by the `SettingsManager`, which will use the native OS credential manager (e.g., Windows Credential Manager, macOS Keychain) via the `keyring` library. The key will never be stored in plain text files.
*   **Local Data at Rest Encryption:** For the MVP, the application will rely on the operating system's native encryption capabilities (e.g., BitLocker, FileVault, LUKS) for protecting local data at rest (SQLite databases, FAISS index, PDF files). Application-level encryption for these data stores is not planned for the MVP due to complexity and potential performance overhead, but can be considered in future iterations if a higher security profile is required.
