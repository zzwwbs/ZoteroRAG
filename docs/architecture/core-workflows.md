# Core Workflows

## Initial Setup & Indexing Workflow

```mermaid
sequenceDiagram
    actor User
    participant UI as ZoteroRAG Desk App (UI)
    participant SM as SettingsManager
    participant ZM as ZoteroManager
    participant IS as IndexingService
    participant CU as ChunkingUtility
    participant EC as EmbeddingClient
    participant MDM as MetadataDBManager
    participant VDM as VectorDBManager
    participant OAI as OpenAI-compatible API

    User->>UI: Launches Application
    UI->>SM: Check Zotero Path
    SM-->>UI: Returns Zotero Path (or None)

    alt Zotero Path Not Configured
        UI->>User: Prompts for Zotero Directory Selection
        User->>UI: Selects Zotero Directory
        UI->>SM: Save Zotero Path(selected_path)
        SM-->>UI: Path Saved Confirmation
    end

    UI->>User: Displays "Start Indexing" Option on Index Tab
    User->>UI: Clicks "Start Indexing"
    UI->>IS: start_indexing(scope=ALL_LIBRARY)
    activate IS

    par
        IS->>ZM: get_all_documents()
        activate ZM
        ZM->>ZM: Reads zotero.sqlite & Locates PDFs
        ZM->>ZM: Extracts text from PDFs (pdfplumber)
        ZM-->>IS: Returns list of (Document, ExtractedText)
        deactivate ZM

        loop For Each Document
            IS->>UI: Update Indexing Progress

            loop For Each Text Chunk
                IS->>CU: chunk_text(text, doc_id, page_num)
                CU-->>IS: Returns Chunk object

                IS->>EC: get_embedding(chunk.content)
                EC-->>IS: Returns (embedding_vector, token_usage)

                IS->>MDM: save_chunk(chunk_metadata)
                MDM-->>IS: Chunk Saved Confirmation

                IS->>VDM: add_vectors([embedding_vector], [chunk.id])
                VDM-->>IS: Vector Added Confirmation
            end
        end
        IS-->>UI: Indexing Complete
        deactivate IS
        UI->>User: Displays "Indexing Complete"

    and User can cancel anytime (Epic 6, Story 6.2)
        User->>UI: Clicks "Cancel Indexing"
        UI->>IS: cancel_indexing()
        Note over IS: Cancellation flag is set.<br/>Current item completes, then stops.
        IS-->>UI: Indexing Cancelled (partial index valid)
        UI->>User: Displays "Indexing Cancelled"<br/>"Partial index is usable"
        Note over UI: Button returns to "Start Indexing"
    end
```
