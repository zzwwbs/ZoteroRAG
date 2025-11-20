# Scalability and Performance

As a local desktop application, "scalability" refers to the ability to handle large user libraries gracefully, rather than concurrent user load.

*   **Indexing Performance (NFR5):** The main performance bottleneck is the initial indexing.
    *   **Parallelism:** While the MVP will use a single background thread for simplicity, future optimizations could involve parallelizing PDF text extraction and API calls for embeddings to speed up the initial indexing run.
    *   **Batching:** The `EmbeddingClient` will batch multiple text chunks into a single API request to the `/v1/embeddings` endpoint, which is significantly more efficient than sending one request per chunk.
*   **Search Performance (NFR5):**
    *   **FAISS:** The choice of FAISS is critical for performance. It is highly optimized for fast similarity searches, even with millions of vectors. A query on a typical library should be sub-second.
    *   **Database Indexing:** The SQLite database schema includes indexes on all foreign keys and frequently queried columns (`zotero_item_key`, `document_id`, `vector_id`) to ensure fast metadata lookups after the initial vector search.
*   **Memory Management:**
    *   **Data Streaming:** During indexing, documents and chunks will be processed in a streaming fashion, not all loaded into memory at once.
    *   **FAISS Memory:** The FAISS index is loaded into memory for fast querying. For a library with 1 million chunks of 1536-dimensional embeddings (OpenAI `text-embedding-ada-002`), the index would require approximately 6 GB of RAM. This is acceptable for a power-user tool but will be documented as a system requirement.
