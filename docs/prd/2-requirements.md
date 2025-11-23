# 2. Requirements

## 2.1. Functional

1.  **FR1 (Setup):** The application must auto-detect the user's Zotero data directory. If detection fails, it must provide a manual selection option.
2.  **FR2 (Indexing):** The application must provide a one-click action to initiate the indexing of all PDFs in the Zotero library. This process must show clear progress and be performed in the background.
3.  **FR3 (Incremental Updates):** The application must support incremental indexing to process only new or modified Zotero items since the last scan.
4.  **FR4 (Search):** The application must provide a search interface for users to enter natural language queries.
5.  **FR5 (Results - Chunks):** Search results must be displayed as a list of relevant text chunks, each with associated metadata (source paper title, authors, year, page number).
6.  **FR6 (Results - Papers):** The application must also display a grouped list of unique source papers from which the result chunks were extracted.
7.  **FR7 (Navigation):** Users must be able to open the full PDF for any search result in the system's default PDF viewer.
8.  **FR8 (BYOK Analysis):** The application must allow users to optionally provide their own OpenAI-compatible API key to perform in-app synthesis of search results. This feature must be disabled by default.
9.  **FR9 (Export - Chunks):** The application must provide a "copy to clipboard" function that formats the user's query and the top N search results into a prompt ready for use in external LLMs like ChatGPT.
10. **FR10 (Export - PDFs):** The application must provide an option to export/copy the actual PDF files from search results to a new user-specified folder.
11. **FR11 (Cancel Indexing):** The application must provide a mechanism for the user to cancel an in-progress indexing operation.
12. **FR12 (Indexing Metadata):** The UI must display the number of papers contained within each Zotero collection and in the entire library to help users estimate indexing scope.
13. **FR13 (Chunk Readability):** The application must provide a detailed, readable view for a selected search result chunk, showing its full text content and metadata.
14. **FR14 (API Usage Transparency):** The application must display estimated token usage and costs associated with cloud API calls (for both embedding and AI analysis).

## 2.2. Non-Functional

1.  **NFR1 (Safety):** All interactions with the Zotero database (`zotero.sqlite`) and its associated `storage/` directory must be strictly **read-only**.
2.  **NFR2 (Privacy):** All user data, including the Zotero library, PDFs, and the generated vector index, must be stored exclusively on the user's local machine.
3.  **NFR3 (Security):** User-provided API keys must be stored locally and securely (e.g., encrypted at rest).
4.  **NFR4 (Transparency):** The application must clearly inform the user what data (text chunks, queries) is being sent to third-party cloud APIs and for what purpose (embedding, analysis).
5.  **NFR5 (Performance):** Once the index is built, query responses should be returned in under one second for libraries up to 10,000 documents (approximately 500,000 chunks). For larger libraries (up to 50,000 documents), queries should return in under 3 seconds. The application must remain responsive during initial indexing, with UI updates every 100 documents processed.
6.  **NFR6 (Usability):** The core workflow (indexing and first search) must be intuitive enough for a user to complete without consulting documentation.
7.  **NFR7 (Portability):** The application must be packaged as a standalone, self-contained executable for Windows, macOS, and Linux, requiring no external dependencies or environment setup.
8.  **NFR8 (Error Handling):** The application must gracefully handle common errors, such as PDF parsing failures or network issues when calling cloud APIs, without crashing.
9.  **NFR9 (Observability):** The application must maintain structured logs with appropriate levels (DEBUG, INFO, WARNING, ERROR) for diagnostics, stored locally with automatic rotation after 10MB or 7 days.
10. **NFR10 (Offline Capability):** Core functionality (browsing indexed content, viewing results, exporting) must work without internet connectivity. Only indexing and AI analysis require network access.
