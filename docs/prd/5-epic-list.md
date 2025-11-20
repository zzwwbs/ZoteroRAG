# 5. Epic List

*   **Epic 1: Foundation & Zotero Integration:** Establish the core application structure, UI framework (PySide6), and read-only integration with the local Zotero database and PDF files, enabling basic PDF text extraction using PyMuPDF.
*   **Epic 2: Indexing & Local Vector Store:** Implement the text chunking, cloud embedding API calls (OpenAI by default), and local vector database (FAISS + SQLite) for storing embeddings and metadata, delivering the ability to build and incrementally update the semantic index.
*   **Epic 3: Semantic Search & Results Display:** Develop the natural language query processing, retrieval from the local vector store, and the UI for displaying relevant chunks and source papers, delivering the core semantic search functionality.
*   **Epic 4: AI Integration & Export Workflows:** Implement the BYOK LLM integration for in-app analysis and the various export functionalities (ChatGPT prompt, relevant PDF paths), delivering advanced interaction and sharing capabilities.
*   **Epic 5: Application Hardening & User Experience:** Focus on robust error handling, secure API key management, comprehensive settings, and packaging for cross-platform deployment, ensuring the application is reliable, secure, and user-friendly for release.
