# Components

## Component List

## ZoteroRAG Desk Application (Main UI)
**Responsibility:** Provides the main graphical user interface, handles user input, displays results, and orchestrates interactions between core services.
**Key Interfaces:**
- User input handling (search queries, button clicks)
- Display of search results, indexing progress, and application status
- Navigation to settings and PDF viewer
**Dependencies:** `ZoteroManager`, `IndexingService`, `SearchService`, `AIService`, `SettingsManager`.
**Technology Stack:** PySide6.

## ZoteroManager
**Responsibility:** Manages all read-only interactions with the user's Zotero database (`zotero.sqlite`) and associated PDF files. This includes detecting the Zotero directory, reading item and collection metadata, and locating PDF paths.
**Key Interfaces:**
- `detect_zotero_directory() -> str`
- `get_collections() -> list[Collection]`
- `get_items_in_collection(collection_id) -> list[Document]`
- `get_all_documents() -> list[Document]`
- `get_item_pdf_path(document_id) -> str`
- `extract_text_from_pdf(pdf_path) -> str`
**Dependencies:** PyMuPDF, `sqlite3` (for `zotero.sqlite`).
**Technology Stack:** Python, PyMuPDF.

## IndexingService
**Responsibility:** Orchestrates the end-to-end process of building and updating the semantic index. This involves fetching documents, extracting text, chunking, generating embeddings, and storing data in the local databases. Handles incremental indexing and progress reporting.
**Key Interfaces:**
- `start_indexing(scope: IndexingScope) -> None`
- `update_index() -> None`
- `get_indexing_progress() -> IndexingProgress`
**Dependencies:** `ZoteroManager`, `ChunkingUtility`, `EmbeddingClient`, `VectorDBManager`, `MetadataDBManager`.
**Technology Stack:** Python.

## ChunkingUtility
**Responsibility:** Breaks down raw text content from PDFs into smaller, overlapping text segments (chunks) suitable for generating meaningful embeddings.
**Key Interfaces:**
- `chunk_text(text: str, document_id: int, page_number: int) -> list[Chunk]`
**Dependencies:** N/A (pure utility).
**Technology Stack:** Python.

## EmbeddingClient
**Responsibility:** Handles communication with the external OpenAI-compatible API to generate vector embeddings for text. Manages API requests, authentication (using user-provided key), and error handling for the embedding endpoint.
**Key Interfaces:**
- `get_embedding(text: str) -> list[float]`
**Dependencies:** `SettingsManager`, `requests` (or similar HTTP client).
**Technology Stack:** Python.

## VectorDBManager
**Responsibility:** Manages the local FAISS index, including creation, loading, saving, adding vectors, and performing efficient similarity searches.
**Key Interfaces:**
- `initialize_index() -> None`
- `load_index() -> None`
- `save_index() -> None`
- `add_vectors(vectors: list[list[float]], ids: list[int]) -> None`
- `search_vectors(query_vector: list[float], k: int) -> list[int]`
**Dependencies:** FAISS.
**Technology Stack:** Python, FAISS.

## MetadataDBManager
**Responsibility:** Manages the local SQLite database for storing all application-specific metadata, including `Document`, `Chunk`, `Collection`, and `DocumentCollection` records. Provides CRUD operations for these models.
**Key Interfaces:**
- `save_document(document: Document) -> None`
- `get_document(id: int) -> Document`
- `save_chunk(chunk: Chunk) -> None`
- `get_chunk(id: int) -> Chunk`
- `save_collection(collection: Collection) -> None`
- `get_collection(id: int) -> Collection`
- `link_document_to_collection(document_id: int, collection_id: int) -> None`
- `get_chunks_by_document_id(document_id: int) -> list[Chunk]`
- `get_documents_by_collection_id(collection_id: int) -> list[Document]`
**Dependencies:** `sqlite3`.
**Technology Stack:** Python.

## SearchService
**Responsibility:** Processes natural language search queries. This involves generating an embedding for the query, performing a vector similarity search, retrieving associated chunk and document metadata, and formatting the results for display.
**Key Interfaces:**
- `search(query_text: str, k: int) -> list[SearchResult]`
**Dependencies:** `EmbeddingClient`, `VectorDBManager`, `MetadataDBManager`.
**Technology Stack:** Python.

## AIService
**Responsibility:** Handles communication with the external OpenAI-compatible API for AI analysis and synthesis of search results. Manages API requests, authentication, and error handling for the chat completions endpoint.
**Key Interfaces:**
- `analyze_chunks(query: str, chunks: list[Chunk]) -> str`
**Dependencies:** `SettingsManager`, `requests`.
**Technology Stack:** Python.

## SettingsManager
**Responsibility:** Manages all application settings and user preferences, including the Zotero data directory path, external API keys, and other configurable options. Ensures secure storage of sensitive data like API keys.
**Key Interfaces:**
- `load_settings() -> AppSettings`
- `save_settings(settings: AppSettings) -> None`
- `get_api_key() -> str`
- `set_api_key_securely(key: str) -> None`
**Dependencies:** OS-specific credential management (e.g., `keyring` library), local file I/O for general settings.
**Technology Stack:** Python.

## Component Diagrams

```mermaid
graph TD
    subgraph User Interface (PySide6)
        UI[ZoteroRAG Desk App]
    end

    subgraph Core Application Logic (Python)
        UI --> ZoteroManager
        UI --> IndexingService
        UI --> SearchService
        UI --> AIService
        UI --> SettingsManager

        IndexingService --> ZoteroManager
        IndexingService --> ChunkingUtility
        IndexingService --> EmbeddingClient
        IndexingService --> VectorDBManager
        IndexingService --> MetadataDBManager

        SearchService --> EmbeddingClient
        SearchService --> VectorDBManager
        SearchService --> MetadataDBManager

        AIService --> EmbeddingClient
        AIService --> SettingsManager

        SettingsManager -- Manages --> OS_Credential_Store[OS Credential Store]
    end

    subgraph Data Storage
        ZoteroManager -- Reads --> Zotero_DB[Zotero DB<br>(zotero.sqlite)]
        ZoteroManager -- Reads --> PDFs[PDF Files<br>(storage/)]
        MetadataDBManager -- Manages --> App_Metadata_DB[App Metadata DB<br>(SQLite)]
        VectorDBManager -- Manages --> FAISS_Index[FAISS Index]
    end

    subgraph External Services (Optional, BYOK)
        EmbeddingClient -- Calls --> OpenAI_API[OpenAI-compatible API<br>(Embeddings)]
        AIService -- Calls --> OpenAI_API
    end

    style Zotero_DB fill:#f9f,stroke:#333,stroke-width:2px
    style PDFs fill:#f9f,stroke:#333,stroke-width:2px
    style OS_Credential_Store fill:#f9f,stroke:#333,stroke-width:2px
```
