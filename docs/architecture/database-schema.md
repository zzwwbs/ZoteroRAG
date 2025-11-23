# Database Schema

```sql
-- Table for Documents
CREATE TABLE IF NOT EXISTS documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    zotero_item_key TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL,
    authors TEXT, -- Stored as JSON string (e.g., '["Author One", "Author Two"]')
    year INTEGER,
    pdf_file_path TEXT NOT NULL,
    indexed_at TEXT NOT NULL, -- ISO 8601 format (YYYY-MM-DD HH:MM:SS.SSS)
    indexing_status TEXT NOT NULL DEFAULT 'not_indexed' -- ('not_indexed', 'indexed', 'no_pdf', 'pdf_error')
);

-- Index for efficient lookup by Zotero item key
CREATE INDEX IF NOT EXISTS idx_documents_zotero_item_key ON documents (zotero_item_key);

-- Table for Chunks
CREATE TABLE IF NOT EXISTS chunks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id INTEGER NOT NULL,
    content TEXT NOT NULL,
    page_number INTEGER NOT NULL,
    vector_id INTEGER NOT NULL UNIQUE, -- Corresponds to the ID in the FAISS index
    FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE
);

-- Index for efficient lookup of chunks by document
CREATE INDEX IF NOT EXISTS idx_chunks_document_id ON chunks (document_id);
-- Index for efficient lookup of chunks by vector_id (for FAISS integration)
CREATE INDEX IF NOT EXISTS idx_chunks_vector_id ON chunks (vector_id);


-- Table for Collections
CREATE TABLE IF NOT EXISTS collections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    zotero_collection_key TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    parent_id INTEGER, -- NULL for top-level collections
    FOREIGN KEY (parent_id) REFERENCES collections(id) ON DELETE SET NULL
);

-- Index for efficient lookup by Zotero collection key
CREATE INDEX IF NOT EXISTS idx_collections_zotero_collection_key ON collections (zotero_collection_key);
-- Index for efficient lookup of child collections
CREATE INDEX IF NOT EXISTS idx_collections_parent_id ON collections (parent_id);


-- Junction Table for Document-Collection Many-to-Many relationship
CREATE TABLE IF NOT EXISTS document_collections (
    document_id INTEGER NOT NULL,
    collection_id INTEGER NOT NULL,
    PRIMARY KEY (document_id, collection_id),
    FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE,
    FOREIGN KEY (collection_id) REFERENCES collections(id) ON DELETE CASCADE
);

-- Indexes for efficient lookup in the junction table
CREATE INDEX IF NOT EXISTS idx_doc_collections_document_id ON document_collections (document_id);
CREATE INDEX IF NOT EXISTS idx_doc_collections_collection_id ON document_collections (collection_id);
```
