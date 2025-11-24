# Components

## Component List

## ZoteroRAG Desk Application (Main UI)
**Responsibility:** Provides the main graphical user interface organized into a task-oriented tabbed layout. Manages the application lifecycle, orchestrates interactions between core services and UI components, handles background task execution, and maintains application state, including the new interactive chat history (Epic 7.4). It defaults to the Search tab on launch and no longer auto-switches tabs after indexing (Epic 8.4).
**Key Interfaces:**
- `__init__()`: Initializes the main window with `QTabWidget`, setting "Search" as the default tab (Epic 8.4)
- `switch_to_tab(tab_name: str)`: Programmatically switches between tabs
- `launch_chunk_detail_dialog(chunk: Chunk, all_chunks: list[Chunk])`: Opens non-modal chunk detail dialog
- `update_token_usage(usage: TokenUsage)`: Updates token usage display in status bar
- Manages `QStackedWidget` for onboarding vs. main tabbed interface
- Handles user input (search queries, button clicks) from all tabs via signal/slot connections
- Displays search results, indexing progress/status, and application status across tabs
- Manages settings dialog and application preferences
**Dependencies:** `ZoteroManager`, `IndexingService`, `SearchService`, `AIService`, `SettingsManager`, `ChunkDetailDialog`, `TokenUsageWidget`.
**Technology Stack:** PySide6.

## ChunkDetailDialog
**Responsibility:** Displays the full, unabridged text of a selected search result chunk in a non-modal dialog (Epic 6, Story 6.4), allowing for easy reading, navigation between results, and actions without leaving the search context.
**Key Interfaces:**
- `show_chunk(chunk: Chunk, chunk_index: int, total_chunks: int)`: Displays the specified chunk with context
- `navigate_previous()`: Shows the previous chunk in the search results list
- `navigate_next()`: Shows the next chunk in the search results list
- `copy_text_to_clipboard()`: Copies the full chunk text to system clipboard
- `open_source_pdf()`: Opens the source PDF at the chunk's page number
- Keyboard shortcuts: `←`/`→` for navigation, `Esc` to close, `Ctrl+C` to copy
**Dependencies:** None (receives data from Main UI via constructor/method calls).
**Technology Stack:** PySide6.

## TokenUsageWidget
**Responsibility:** A non-visual component or controller that tracks API token consumption and estimated costs for the current session (Epic 6.6). It provides data to be displayed in the main window's status bar, ensuring users have persistent visibility of their API usage and costs without cluttering a specific tab (Epic 7.3).
**Key Interfaces:**
- `update_usage(usage: TokenUsage)`: Adds a new token usage record and updates session totals
- `get_session_totals() -> dict`: Returns aggregated statistics (total tokens, total cost, call counts)
- `reset_session_tracking()`: Clears session usage data
- Emits signals to the `MainWindow` to update the status bar display
**Dependencies:** None (receives `TokenUsage` data from `MainWindow`).

## ZoteroManager
**Responsibility:** Manages all read-only interactions with the user's Zotero database (`zotero.sqlite`) and associated PDF files. This includes detecting the Zotero directory, reading item and collection metadata with paper counts (Epic 6, Story 6.3), and locating PDF paths.
**Key Interfaces:**
- `detect_zotero_directory() -> str`
- `get_collections() -> list[Collection]`
- `get_collection_paper_counts() -> dict[str, int]`: Returns mapping of collection IDs to paper counts for display in UI (Story 6.3)
- `get_total_paper_count() -> int`: Returns total number of papers in the entire library
- `get_items_in_collection(collection_id) -> list[Document]`
- `get_all_documents() -> list[Document]`
- `get_item_pdf_path(document_id) -> str`
- `extract_text_from_pdf(pdf_path) -> str`
**Dependencies:** pypdfium2, `sqlite3` (for `zotero.sqlite`).
**Technology Stack:** Python, pypdfium2.

## IndexingService
**Responsibility:** Orchestrates the end-to-end process of building and updating the semantic index. This involves fetching documents, extracting text, chunking, generating embeddings, and storing data in the local databases. Handles incremental indexing, progress reporting, safe cancellation (Epic 6.2), and provides real-time status updates per paper (Epic 8.2). After completion, it provides a summary of the indexing job (Epic 8.3).
**Key Interfaces:**
- `start_indexing(scope: IndexingScope) -> None`: Begins indexing operation in background thread
- `cancel_indexing() -> None`: Safely requests cancellation of in-progress indexing; sets cancellation flag (Story 6.2)
- `is_cancellation_requested() -> bool`: Checks if cancellation has been requested
- `update_index() -> None`: Performs incremental indexing for new/modified documents
- `get_indexing_progress() -> IndexingProgress`: Returns current progress (processed count, total count, percentage)
- Emits signals for progress updates, per-paper status changes (Epic 8.2), and a final summary upon completion/cancellation (Epic 8.3)
**Dependencies:** `ZoteroManager`, `ChunkingUtility`, `EmbeddingClient`, `VectorDBManager`, `MetadataDBManager`.

## ChunkingUtility
**Responsibility:** Breaks down raw text content from PDFs into smaller, overlapping text segments (chunks) suitable for generating meaningful embeddings.
**Key Interfaces:**
- `chunk_text(text: str, document_id: int, page_number: int) -> list[Chunk]`
**Dependencies:** N/A (pure utility).
**Technology Stack:** Python.

## EmbeddingClient
**Responsibility:** Handles communication with the external OpenAI-compatible API to generate vector embeddings for text. Manages API requests, authentication, error handling, and tracks token usage for transparency (Epic 6, Story 6.6).
**Key Interfaces:**
- `get_embedding(text: str) -> tuple[list[float], TokenUsage]`: Returns embedding vector and token usage record
- `get_embeddings_batch(texts: list[str]) -> tuple[list[list[float]], TokenUsage]`: Batched embedding generation for efficiency
- `_calculate_cost(tokens: int, model: str) -> float`: Calculates estimated cost based on current pricing
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
**Responsibility:** Manages the local SQLite database for storing all application-specific metadata, including `Document`, `Chunk`, `Collection`, and `DocumentCollection` records. Provides CRUD operations for these models and is responsible for updating the `indexing_status` of documents during the indexing process (Epic 8.1).
**Key Interfaces:**
- `save_document(document: Document) -> None`
- `get_document(id: int) -> Document`
- `update_document_status(document_id: int, status: str) -> None`: Updates the indexing status for a given document (Epic 8.1).
- `save_chunk(chunk: Chunk) -> None`
- `get_chunk(id: int) -> Chunk`
- `save_collection(collection: Collection) -> None`
- `get_collection(id: int) -> Collection`
- `link_document_to_collection(document_id: int, collection_id: int) -> None`
- `get_chunks_by_document_id(document_id: int) -> list[Chunk]`
- `get_documents_by_collection_id(collection_id: int) -> list[Document]`
**Dependencies:** `sqlite3`.

## SearchService
**Responsibility:** Processes natural language search queries. This involves generating an embedding for the query, performing a vector similarity search, retrieving associated chunk and document metadata, and formatting the results for display.
**Key Interfaces:**
- `search(query_text: str, k: int) -> list[SearchResult]`
**Dependencies:** `EmbeddingClient`, `VectorDBManager`, `MetadataDBManager`.
**Technology Stack:** Python.

## AIService
**Responsibility:** Handles communication with the external OpenAI-compatible API for the interactive AI chat analysis (Epic 7.4). It constructs prompts that include conversation history and, optionally, retrieved search result chunks to provide context to the LLM (Epic 7.6). Manages API requests, authentication, error handling, and tracks token usage.
**Key Interfaces:**
- `get_chat_response(messages: list[dict], include_context: bool, context_chunks: list[Chunk]) -> tuple[str, TokenUsage]`: Sends the conversation history (and optional context) to the chat model and returns the AI's response and token usage.
- `_calculate_cost(tokens: int, model: str) -> float`: Calculates estimated cost based on current pricing.
**Dependencies:** `SettingsManager`, `requests`.

## SettingsManager
**Responsibility:** Manages all application settings and user preferences, including the Zotero data directory path, external API keys for both embedding and chat services (Epic 7.1), and other configurable options. Ensures secure storage of sensitive data like API keys.
**Key Interfaces:**
- `load_settings() -> AppSettings`
- `save_settings(settings: AppSettings) -> None`
- `get_embedding_api_key() -> str`
- `set_embedding_api_key_securely(key: str) -> None`
- `get_chat_api_key() -> str`
- `set_chat_api_key_securely(key: str) -> None`
**Dependencies:** OS-specific credential management (e.g., `keyring` library), local file I/O for general settings.

## Component Diagrams

```mermaid
graph TD
    subgraph User Interface (PySide6)
        UI[ZoteroRAG Desk App<br>(Manages Tabs)]
        SearchTab[Search Tab]
        IndexTab[Index Tab]
        AnalysisTab[Analysis Tab]
        SettingsTab[Settings Tab]
        ChunkDialog[Chunk Detail Dialog]
        TokenWidget[Token Usage Widget]

        UI -- Contains --> SearchTab
        UI -- Contains --> IndexTab
        UI -- Contains --> AnalysisTab
        UI -- Contains --> SettingsTab
        AnalysisTab -- Contains --> TokenWidget
        SearchTab -- Triggers --> ChunkDialog
    end

    subgraph Core Application Logic (Python)
        UI -- Interacts with --> ZoteroManager
        UI -- Interacts with --> IndexingService
        UI -- Interacts with --> SearchService
        UI -- Interacts with --> AIService
        UI -- Interacts with --> SettingsManager

        IndexingService -- Uses --> ZoteroManager
        IndexingService -- Uses --> ChunkingUtility
        IndexingService -- Uses --> EmbeddingClient
        IndexingService -- Uses --> VectorDBManager
        IndexingService -- Uses --> MetadataDBManager

        SearchService -- Uses --> EmbeddingClient
        SearchService -- Uses --> VectorDBManager
        SearchService -- Uses --> MetadataDBManager

        AIService -- Uses --> SettingsManager

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
