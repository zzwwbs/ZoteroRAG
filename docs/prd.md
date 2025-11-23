# ZoteroRAG Desk Product Requirements Document (PRD)

## 1. Goals and Background Context

### 1.1. Goals

*   Enable researchers to leverage their Zotero libraries semantically, finding relevant passages via natural language questions.
*   Provide a low-friction setup with a simple "point at Zotero, click Index" workflow, requiring no manual environment configuration.
*   Offer flexible AI usage through a Bring-Your-Own-Key (BYOK) model for in-app analysis or an export-only mode for use with external tools like ChatGPT.
*   Ensure user privacy by keeping all user data (PDFs, index) on the user's local machine, only sending text snippets to cloud APIs for embedding or analysis.
*   Bridge the gap between finding relevant snippets and reading the full context by providing a simple way to navigate from a search result to the full PDF.

### 1.2. Background Context

Researchers often manage hundreds or thousands of PDFs in Zotero, but finding specific information across these documents is a manual, time-consuming process that relies on basic keyword search and memory. This creates a significant bottleneck in literature reviews and research synthesis. Existing solutions often fall short as they are web-based, require complex technical setup, or do not integrate safely with a local Zotero database.

ZoteroRAG Desk solves this by providing a desktop-first, local-first application that operates in a read-only mode on the user's Zotero library. It extracts text from PDFs, uses a cloud embedding API to create a semantic index stored locally, and provides a user-friendly interface for search and analysis. This unlocks the full value of a researcher's library by enabling powerful, natural language search without compromising privacy or data integrity.

### 1.3. Change Log

| Date | Version | Description | Author |
| :--- | :--- | :--- | :--- |
| 2025-11-18 | 1.0 | Initial draft based on Project Brief and preliminary PRD. | John (PM) |
| 2025-11-22 | 1.1 | Added Epic 6 for UX enhancements based on user feedback. | John (PM) |
| 2025-11-22 | 1.2 | Added Epics 7, 8, and 9 for post-MVP UX and AI enhancements. | John (PM) |
| 2025-11-23 | 1.3 | Replaced PyMuPDF with pdfplumber and added Epic 10 for migration. | John (PM) |

## 2. Requirements

### 2.1. Functional

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

### 2.2. Non-Functional

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

## 3. User Interface Design Goals

### 3.1. Overall UX Vision

The user experience should be clean, direct, and trustworthy. The application should feel like a powerful utility that respects the user's focus and workflow, especially on screens with limited real estate. The core design principle is to minimize friction and scrolling by organizing tasks into logical, focused views. The interface should be simple enough to be used immediately, yet provide access to powerful features for those who need them.

### 3.2. Key Interaction Paradigms

The primary interaction model is being updated from a single, scrollable view to a **task-oriented tabbed interface** to improve usability and reduce clutter.

1.  **Tab-Based Main Window:** The main application window will use a `QTabWidget` to separate primary functions into distinct tabs. This prevents overcrowding and allows for a more focused workflow.
2.  **Centralized Search Controls:** The search bar and its related controls (like the number of chunks to retrieve) will be grouped together for intuitive access.
3.  **Enhanced Results Readability:** Search results (chunks) will have an improved preview format and a dedicated, non-modal dialog for reading full content without leaving the main application context.
4.  **Clear Action Buttons:** Buttons for primary actions like "Start Indexing" will provide clear visual feedback, changing state to "Cancel Indexing" during operation.

### 3.3. Core Screens and Views

The application's UI will be organized into the following tabs:

1.  **Search Tab:** This is the primary landing tab after indexing is complete. It will contain:
    *   The main search input bar and chunk count selector.
    *   The split-pane view for displaying "Papers" and "Chunks" from search results.
    *   The "Analyze with AI" button to trigger analysis.
2.  **Index Tab:** This tab is focused on library management and indexing. It will contain:
    *   The Zotero library overview.
    *   The indexing scope selector (Entire Library vs. Collections), which will display the number of papers for each option.
    *   The "Start/Cancel Indexing" button and progress indicators.
3.  **AI Analysis Tab:** This tab is dedicated to displaying the results of AI synthesis. It will contain:
    *   The full, synthesized answer from the LLM.
    *   The new API token usage widget, providing transparency on costs and consumption.
4.  **Settings Tab:** A dedicated, uncluttered space for all application settings, including Zotero path, API keys, and other future configuration options.
5.  **Chunk Detail View (Non-Modal Dialog):** Triggered by a double-click on a chunk in the search results. This dialog will:
    *   Display the full, formatted text of the chunk.
    *   Show detailed metadata (document title, page number, relevance score).
    *   Provide navigation to the previous/next chunk in the results list.
    *   Offer actions like "Copy Text" and "Open PDF".

### 3.4. Accessibility: WCAG AA

The application should adhere to WCAG 2.1 AA standards to ensure it is usable by people with a wide range of disabilities. This includes considerations for color contrast, keyboard navigation (including tab navigation and shortcuts in the chunk detail view), and screen reader compatibility.

### 3.5. Branding

The branding should be minimal and professional, suitable for an academic tool. The focus should be on clarity and readability rather than a distinct visual identity. A simple logo and a clean, neutral color palette are recommended.

### 3.6. Target Device and Platforms: Cross-Platform

The application will be a standalone desktop application with consistent functionality across Windows, macOS, and Linux. The new tabbed design is specifically intended to improve usability on lower-resolution screens (e.g., 1366x768).

## 4. Technical Assumptions

### 4.1. Repository Structure: Monorepo

For a standalone desktop application, a monorepo structure is assumed. This simplifies dependency management, build processes, and code sharing between different components of the application (e.g., core logic, GUI).

### 4.2. Service Architecture: Monolith

The MVP will be built as a monolithic desktop application. This aligns with the project brief's statement that "A monolithic desktop application structure is sufficient for the MVP." This approach simplifies deployment and reduces initial architectural complexity.

### 4.3. Testing Requirements: Unit + Integration

Testing will include both unit tests for individual components and integration tests to ensure that different parts of the application (e.g., PDF extraction, Zotero integration, vector DB interaction) work correctly together. This provides a balanced approach to quality assurance for a desktop application.

### 4.4. Additional Technical Assumptions and Requests

*   **Language:** Python 3.13+
*   **GUI Framework:** PySide6
*   **PDF Extraction Library:** pdfplumber
*   **Cloud Embedding API:** OpenAI embeddings as default, with the ability for users to configure other compatible API endpoints.
*   **Local Vector Database:** FAISS
*   **Local Metadata Storage:** SQLite (for storing chunk metadata and Zotero item information, complementing FAISS for vector storage)
*   **LLM Integration (BYOK):** OpenAI Chat/Responses API (or similar, configurable by user)
*   **Packaging:** Self-contained installers/bundles for Windows, macOS, and Linux (e.g., using PyInstaller or similar tools)
*   **API Key Storage:** Secure local storage of API keys, using OS-specific credential management systems (keyring library).

## 5. Epic List

*   **Epic 1: Foundation & Zotero Integration:** Establish the core application structure, UI framework (PySide6), and read-only integration with the local Zotero database and PDF files, enabling basic PDF text extraction using pdfplumber.
*   **Epic 2: Indexing & Local Vector Store:** Implement the text chunking, cloud embedding API calls (OpenAI by default), and local vector database (FAISS + SQLite) for storing embeddings and metadata, delivering the ability to build and incrementally update the semantic index.
*   **Epic 3: Semantic Search & Results Display:** Develop the natural language query processing, retrieval from the local vector store, and the UI for displaying relevant chunks and source papers, delivering the core semantic search functionality.
*   **Epic 4: AI Integration & Export Workflows:** Implement the BYOK LLM integration for in-app analysis and the various export functionalities (ChatGPT prompt, relevant PDF paths), delivering advanced interaction and sharing capabilities.
*   **Epic 5: Application Hardening & User Experience:** Focus on robust error handling, secure API key management, comprehensive settings, and packaging for cross-platform deployment, ensuring the application is reliable, secure, and user-friendly for release.
*   **Epic 6: UI/UX Enhancements & Usability Polish:** Implement significant UI/UX improvements based on user feedback, including a tab-based interface, indexing cancellation, improved data visibility, and enhanced result readability.
*   **Epic 7: Enhanced AI Configuration & Chat Experience:** Enable flexible AI provider configuration and transform AI Analysis into an interactive chat interface with user-controlled retrieval.
*   **Epic 8: Indexing & Search UX Improvements:** Improve visibility of indexing status and optimize post-indexing workflow by adding real-time status tracking, indexing summaries, and better default navigation.
*   **Epic 9: Search Tab Action Reorganization:** Improve Search tab button layout and labeling clarity by moving action buttons to the bottom and renaming the ChatGPT export button.

## 5.1. Out of Scope for MVP

The following features and capabilities are explicitly **out of scope** for the MVP release:

*   **Real-time Zotero Synchronization:** Automatic detection and indexing of new/modified PDFs as they are added to Zotero. The MVP requires manual re-indexing.
*   **Multi-Library Support:** Managing multiple separate Zotero libraries within the application.
*   **Advanced Search Filters:** Filtering by publication date, author, journal, or Zotero tags/collections after search.
*   **Custom Embedding Models:** While the API is OpenAI-compatible, the MVP will not include UI for selecting or configuring alternative models with different dimensions.
*   **Collaborative Features:** Sharing libraries, search results, or annotations with other users.
*   **Mobile Applications:** iOS or Android versions of the application.
*   **Cloud Synchronization:** Syncing the index across multiple devices via cloud storage.
*   **Annotation and Note-Taking:** Adding highlights, notes, or comments to PDFs within the application.
*   **Citation Management:** Exporting citations in various formats or managing bibliographies.
*   **Bulk Operations:** Batch deletion, re-indexing of selected items, or bulk metadata editing.
*   **Plugin System:** Extensibility via third-party plugins or extensions.
*   **Advanced Analytics:** Usage statistics, search history tracking, or recommendation engines.

## 6. Epic Details

### Epic 1: Foundation & Zotero Integration

#### Expanded Goal:

This epic aims to lay the groundwork for the ZoteroRAG Desk application by establishing the core desktop application framework and enabling fundamental interaction with the user's local Zotero library. It will ensure the application can correctly identify and access Zotero data, extract text from associated PDF files, and provide a basic user interface for initial setup and status monitoring, all while adhering to the read-only principle.

#### Story 1.1: Setup Application Environment

As a **developer**,
I want to **set up the PySide6 application structure and build process**,
so that **I have a functional cross-platform desktop application shell**.

##### Acceptance Criteria

1.  1.1.1: A basic PySide6 window can be launched on Windows, macOS, and Linux.
2.  1.1.2: The application can be packaged into a standalone executable for each target OS.
3.  1.1.3: A basic "About" dialog is accessible from the application menu.

#### Story 1.2: Zotero Directory Detection & Selection

As a **user**,
I want the app to **automatically detect my Zotero data directory, or allow me to select it manually**,
so that **the application can access my library**.

##### Acceptance Criteria

1.  1.2.1: On first launch, the application attempts to auto-detect the Zotero data directory.
2.  1.2.2: If auto-detection fails or is incorrect, the user is prompted to browse and select the directory.
3.  1.2.3: The selected Zotero directory path is persisted across application launches.
4.  1.2.4: The application displays a clear message indicating whether a valid Zotero directory is configured.

#### Story 1.3: Read Zotero Database & List Items

As a **user**,
I want the app to **read my Zotero database in read-only mode and display a list of my library items**,
so that **I can see my Zotero data within the app**.

##### Acceptance Criteria

1.  1.3.1: The application successfully connects to the `zotero.sqlite` database in read-only mode.
2.  1.3.2: The application can retrieve and display a list of Zotero items (e.g., title, author, year).
3.  1.3.3: The application handles cases where the Zotero database is locked or corrupted gracefully, displaying an informative error.
4.  1.3.4: No write operations are performed on the `zotero.sqlite` database.

#### Story 1.4: Extract Text from Attached PDFs

As a **user**,
I want the app to **identify PDF attachments for Zotero items and extract their text content using pdfplumber**,
so that **the text can be prepared for indexing**.

##### Acceptance Criteria

1.  1.4.1: For each Zotero item with a PDF attachment, the application can locate the PDF file in the `storage/` directory.
2.  1.4.2: The application successfully extracts text content from a sample PDF using pdfplumber.
3.  1.4.3: The application logs errors for PDFs from which text extraction fails, but continues processing other PDFs.
4.  1.4.4: The extracted text is available for subsequent processing steps.

### Epic 2: Indexing & Local Vector Store

#### Expanded Goal:

This epic focuses on building the core data processing pipeline of the application. It will take the raw text extracted in Epic 1 and transform it into a searchable semantic index. This involves chunking the text, calling a cloud API to generate embeddings, and storing these embeddings along with their associated metadata in a local FAISS and SQLite database, ready for retrieval. **Crucially, this epic will also provide users with the control to index their library in manageable parts, such as by collection.**

#### Story 2.1: Implement Local Data Storage

As a **developer**,
I want to **set up the local FAISS index and SQLite database**,
so that **I have a persistent storage solution for vector embeddings and their metadata**.

##### Acceptance Criteria

1.  2.1.1: The application can create and initialize an empty SQLite database with the required schema (for documents and chunks).
2.  2.1.2: The application can create and initialize an empty FAISS index.
3.  2.1.3: Both the SQLite database and the FAISS index are stored in a designated application data directory.
4.  2.1.4: The application can successfully save and load the FAISS index and connect to the SQLite database on startup.

#### Story 2.2: Implement Text Chunking

As a **user**,
I want the application to **break down the extracted PDF text into smaller, overlapping chunks**,
so that **the text is suitable for generating meaningful embeddings**.

##### Acceptance Criteria

1.  2.2.1: A text chunking function is implemented that splits text into segments of 600 tokens (default, configurable via settings between 400-1000 tokens).
2.  2.2.2: The chunking function includes a 100-token overlap between chunks (configurable via settings between 50-200 tokens).
3.  2.2.3: Each chunk is associated with its source document ID and page number.
4.  2.2.4: The chunking process can handle very short documents (< 100 tokens) without creating empty chunks and very long documents (> 100,000 tokens) without memory issues.
5.  2.2.5: The chunking algorithm uses sentence boundaries where possible to avoid splitting mid-sentence.

#### Story 2.3: Implement Cloud Embedding Generation

As a **developer**,
I want to **implement a service that sends text chunks to the OpenAI embedding API and retrieves the resulting vectors**,
so that **I can generate embeddings for my text**.

##### Acceptance Criteria

1.  2.3.1: The application can make a successful API call to the OpenAI embeddings endpoint with a sample text chunk.
2.  2.3.2: The application correctly handles API authentication using a user-provided key (from a temporary config, as full settings are in a later epic).
3.  2.3.3: The application includes error handling for common API issues (e.g., network errors, invalid API key, rate limiting).
4.  2.3.4: The embedding vector is successfully received and can be used in the next step.

#### Story 2.4: Implement Indexing Scope Selection

As a **user with a large library**,
I want to **choose what to index (e.g., my entire library, a specific Zotero collection, or selected items)**,
so that **I can manage the indexing time and cost**.

##### Acceptance Criteria

1.  2.4.1: The UI presents options to start indexing for: the entire library, a selected Zotero collection, or a selection of items.
2.  2.4.2: The application can retrieve the list of Zotero collections and display them to the user.
3.  2.4.3: The user's choice of scope is passed to the indexing engine.

#### Story 2.5: Build and Update the Index

As a **developer**,
I want an **indexing engine that can process a given set of Zotero items**,
so that **the library can be indexed in user-defined scopes (full library, collection, or selection)**.

##### Acceptance Criteria

1.  2.5.1: An indexing engine receives a list of Zotero items to process based on the user's selected scope.
2.  2.5.2: For each item in the scope, the engine runs the workflow (text extraction -> chunking -> embedding -> storage).
3.  2.5.3: The UI displays real-time progress of the indexing process for the selected scope.
4.  2.5.4: The engine can detect already-indexed items within the scope and skip them to support incremental updates.

### Epic 3: Semantic Search & Results Display

#### Expanded Goal:

This epic delivers the core value proposition of the application: semantic search. It will enable users to ask natural language questions, have those questions converted into embeddings, and see the most relevant results retrieved from their local index. The focus is on creating a fluid and intuitive user interface for exploring the search results, both as individual text chunks and as a list of source papers.

#### Story 3.1: Implement Search Bar and Query Embedding

As a **user**,
I want **a search bar where I can type my question**,
so that **I can initiate a semantic search**.

##### Acceptance Criteria

1.  3.1.1: The main UI includes a prominent text input field for search queries.
2.  3.1.2: When a user executes a search, the application sends the query text to the configured cloud embedding API.
3.  3.1.3: The application receives the resulting query embedding vector.
4.  3.1.4: The UI indicates that a search is in progress.

#### Story 3.2: Implement Vector Search and Retrieval

As a **developer**,
I want to **use the query embedding to search the local FAISS index and retrieve the most relevant text chunks**,
so that **I can find the best matches for the user's question**.

##### Acceptance Criteria

1.  3.2.1: The application performs a similarity search on the FAISS index using the query embedding.
2.  3.2.2: The search returns a list of the top K most similar chunk IDs (where K is configurable).
3.  3.2.3: The application then retrieves the full metadata for these chunks from the SQLite database.
4.  3.2.4: The retrieval process is performant, returning results in under a second for a typical query.

#### Story 3.3: Implement Results Display UI

As a **user**,
I want to **see the search results displayed clearly in a split-pane view**,
so that **I can easily explore the relevant papers and text snippets**.

##### Acceptance Criteria

1.  3.3.1: The UI is divided into two main panels: a "Papers" view and a "Chunks" view.
2.  3.3.2: The "Papers" view lists the unique source documents for the retrieved chunks, showing title, authors, year, and the number of matching chunks.
3.  3.3.3: The "Chunks" view displays the text of each relevant snippet, along with its source paper and page number.
4.  3.3.4: Initially, the "Chunks" view shows all retrieved chunks, sorted by relevance.

#### Story 3.4: Implement Interactive Results Filtering

As a **user**,
I want to be able to **click on a paper in the "Papers" view to filter the "Chunks" view**,
so that **I can focus on the results from a single document**.

##### Acceptance Criteria

1.  3.4.1: Clicking a paper in the "Papers" view updates the "Chunks" view to show only the chunks from that selected paper.
2.  3.4.2: The UI provides a clear way to remove the filter and return to viewing all chunks.
3.  3.4.3: The application includes a button next to each paper and/or chunk to "Open full PDF", which opens the corresponding PDF file in the system's default viewer.

### Epic 4: AI Integration & Export Workflows

#### Expanded Goal:

This epic extends the core search functionality by enabling users to act upon their retrieved information. It will implement the optional in-app AI analysis using a user-provided API key, allowing for synthesized answers with citations. Additionally, it will provide robust export options, including a formatted prompt for external LLMs like ChatGPT and the ability to **export the actual PDF files into a new folder**, enhancing the utility and flexibility of the application.

#### Story 4.1: Implement BYOK LLM API Configuration

As a **user**,
I want to **securely enter and manage my OpenAI (or compatible) API key within the application settings**,
so that **I can enable in-app AI analysis**.

##### Acceptance Criteria

1.  4.1.1: A dedicated section in the application settings allows users to input their LLM API key.
2.  4.1.2: The API key is stored securely (e.g., encrypted at rest) and never transmitted externally by the application itself.
3.  4.1.3: A "Test Connection" button verifies the validity of the entered API key without performing a full analysis.
4.  4.1.4: A toggle switch allows users to enable/disable in-app AI analysis, which is off by default.

#### Story 4.2: Implement In-App AI Analysis

As a **user**,
when in-app AI analysis is enabled, I want to **click a button to get a synthesized answer based on my query and the retrieved chunks**,
so that **I can quickly understand the key insights**.

##### Acceptance Criteria

1.  4.2.1: An "Analyze with AI" button is visible and enabled when an API key is configured and in-app analysis is toggled on.
2.  4.2.2: Clicking the button sends the user's query and a selection of top retrieved chunks to the configured LLM API.
3.  4.2.3: The application displays the LLM's synthesized answer in a dedicated area of the UI.
4.  4.2.4: The synthesized answer includes inline citations that map back to the source papers and chunks.
5.  4.2.5: The application handles API errors (e.g., rate limits, invalid response) gracefully, displaying informative messages.

#### Story 4.3: Implement ChatGPT Export (Text Prompt)

As a **user**,
I want a **"Copy to ChatGPT" button that formats my query and relevant chunks into a ready-to-paste prompt**,
so that **I can easily continue my analysis in an external LLM**.

##### Acceptance Criteria

1.  4.3.1: A "Copy to ChatGPT" button is available on the search results screen.
2.  4.3.2: Clicking the button generates a text block containing the original query, a clear instruction for the LLM, and a numbered list of top N chunks with their metadata.
3.  4.3.3: The generated text block is automatically copied to the user's clipboard.
4.  4.3.4: A brief notification confirms that the content has been copied.

#### Story 4.4: Implement PDF File Export

As a **user**,
I want to **export the actual PDF files from my search results to a new folder**,
so that **I have a self-contained collection of relevant papers for sharing or external use**.

##### Acceptance Criteria

1.  4.4.1: An "Export PDFs" button is available on the search results screen.
2.  4.4.2: Clicking the button prompts the user to select a destination folder for the export.
3.  4.4.3: The application creates a new subfolder in the selected destination (e.g., named with the current date/time or a user-provided name).
4.  4.4.4: The application copies all unique PDF files corresponding to the search results into the newly created subfolder.
5.  4.4.5: A notification confirms that the files have been successfully exported and provides the path to the new folder.

### Epic 5: Application Hardening & User Experience

#### Expanded Goal:

This epic focuses on transforming the functional prototype into a robust, reliable, and user-friendly product ready for release. It encompasses critical non-functional requirements such as comprehensive error handling, secure management of sensitive user data like API keys, and the creation of a polished, cross-platform installer. The goal is to ensure a stable, secure, and intuitive experience for all users, making the application easy to install, configure, and use.

#### Story 5.1: Implement Comprehensive Error Handling & Logging

As a **developer**,
I want to **implement a robust error handling and logging mechanism throughout the application**,
so that **unexpected issues can be gracefully managed and diagnosed**.

##### Acceptance Criteria

1.  5.1.1: All critical operations (e.g., Zotero DB access, PDF extraction, API calls, index operations) include `try-except` blocks or equivalent error handling.
2.  5.1.2: User-facing error messages are clear, concise, and actionable, avoiding technical jargon.
3.  5.1.3: Detailed technical errors are logged to a file (e.g., `debug.log`) with timestamps and relevant context.
4.  5.1.4: The application remains stable and responsive even when non-critical errors occur.

#### Story 5.2: Implement Secure API Key Management

As a **user**,
I want my **API keys to be stored and used securely**,
so that **my credentials are protected from unauthorized access**.

##### Acceptance Criteria

1.  5.2.1: API keys are encrypted at rest using an appropriate, platform-specific method (e.g., OS keychain, encrypted file).
2.  5.2.2: API keys are never exposed in plain text in logs or configuration files.
3.  5.2.3: The application only accesses API keys when actively making an API call.
4.  5.2.4: Users are clearly informed about how their API keys are stored and used.

#### Story 5.3: Develop Cross-Platform Installers

As a **user**,
I want a **simple, self-contained installer for my operating system**,
so that **I can easily install and run the ZoteroRAG Desk application without manual setup**.

##### Acceptance Criteria

1.  5.3.1: Standalone installers (e.g., `.exe` for Windows, `.dmg` for macOS, AppImage for Linux) are generated.
2.  5.3.2: The installers include all necessary Python runtime and application dependencies.
3.  5.3.3: Installation is a straightforward, wizard-driven process requiring minimal user interaction.
4.  5.3.4: The installed application launches successfully and functions as expected on each target OS.

#### Story 5.4: Implement Comprehensive Settings UI

As a **user**,
I want a **clear and organized settings interface**,
so that **I can easily configure all application parameters, including Zotero path, embedding provider, chunking options, and API keys**.

##### Acceptance Criteria

1.  5.4.1: A dedicated "Settings" window or tab is accessible from the main application.
2.  5.4.2: All configurable parameters identified in previous epics (e.g., Zotero path, API keys, chunk size, embedding model) are present and clearly labeled.
3.  5.4.3: Changes to settings are saved persistently and applied correctly.
4.  5.4.4: Tooltips or inline help text explain complex settings.

#### Story 5.5: Implement User Onboarding & First-Run Experience

As a **new user**,
I want a **guided first-run experience**,
so that **I can quickly set up the application and understand its core functionality without needing to read documentation**.

##### Acceptance Criteria

1.  5.5.1: On the very first launch, a clear onboarding flow guides the user through Zotero directory selection and initial indexing.
2.  5.5.2: Key privacy and cloud usage disclaimers are presented and acknowledged by the user during onboarding.
3.  5.5.3: The onboarding flow culminates in the user being able to perform their first semantic search.
4.  5.5.4: The application provides visual cues or hints for key features (e.g., "Click here to start indexing").

## 7. Checklist Results Report

### Executive Summary

*   **Overall PRD Completeness:** 95%
*   **MVP Scope Appropriateness:** Just Right
*   **Readiness for Architecture Phase:** Ready
*   **Most Critical Gaps or Concerns:** The PRD is comprehensive. The only minor gaps are the lack of an explicit "Out of Scope" section (though this is implied by the defined epics) and detailed operational requirements like monitoring, which can be defined during the architecture phase.

### Category Analysis Table

| Category | Status | Critical Issues |
| :--- | :--- | :--- |
| 1. Problem Definition & Context | PASS | None. |
| 2. MVP Scope Definition | PARTIAL | Lacks an explicit "Out of Scope for MVP" section for maximum clarity. |
| 3. User Experience Requirements | PASS | None. |
| 4. Functional Requirements | PASS | None. |
| 5. Non-Functional Requirements | PASS | None. |
| 6. Epic & Story Structure | PASS | None. |
| 7. Technical Guidance | PASS | None. |
| 8. Cross-Functional Requirements | PARTIAL | Operational requirements (e.g., monitoring, alerting) are not detailed. |
| 9. Clarity & Communication | PASS | None. |

### Top Issues by Priority

*   **BLOCKERS:** None.
*   **HIGH:** None.
*   **MEDIUM:**
    *   It would improve clarity to add a dedicated "Out of Scope for MVP" section to the PRD to prevent scope creep.
    *   The Architect should be tasked with defining specific monitoring and operational requirements.
*   **LOW:** None.

### MVP Scope Assessment

The MVP scope, as defined by the five epics, is well-sized. It delivers a complete, end-to-end workflow that validates the core value proposition of the product. The breakdown is logical and allows for incremental delivery. No features seem excessive for an MVP, and no essential features appear to be missing.

### Technical Readiness

The technical constraints and guidance are clear and specific, providing a strong foundation for the Architect. The choice of a monolithic architecture and the specific technologies (PySide6, PyMuPDF, FAISS, SQLite) give clear direction. No major technical risks have been left unaddressed for this stage.

### Recommendations

1.  **Proceed to Architecture:** The document is ready for the Architect to begin their work.
2.  **Architect Tasking:** The Architect should be explicitly tasked with defining the monitoring and alerting strategy as part of their work.
3.  **Documentation Update:** Consider adding an "Out of Scope" section to the PRD for future reference.

### Final Decision

*   **READY FOR ARCHITECT**: The PRD and epics are comprehensive, properly structured, and ready for architectural design.

## 8. Next Steps

### 8.1. UX Expert Prompt

You are the UX Expert. Your task is to create the UI/UX architecture for the ZoteroRAG Desk application. Review this PRD, paying close attention to Section 3 (User Interface Design Goals) and the user stories in Section 6. Your deliverables should include wireframes for the core screens and a component style guide to ensure a consistent and intuitive user experience.

### 8.2. Architect Prompt

You are the Architect. Your task is to create the technical architecture for the ZoteroRAG Desk application. This complete and approved Product Requirements Document (PRD) is your primary source of truth. Your architecture must satisfy all functional and non-functional requirements, adhere to the technical assumptions, and provide a clear implementation plan for the epics and stories defined within. Produce an `architecture.md` document as your primary deliverable.

### Epic 6: UI/UX Enhancements & Usability Polish

#### Expanded Goal:

This epic addresses critical usability issues identified after the initial MVP release, based on direct user feedback. The goal is to significantly improve the user experience by reorganizing the UI for clarity, providing users with more control and feedback, and increasing transparency. These changes will make the application more intuitive, efficient, and trustworthy, especially for users on low-resolution screens or with large libraries.

#### Story 6.1: Implement Tab-Based Interface

As a **user**,
I want the **application's functions to be organized into separate tabs**,
so that **the interface is less cluttered and I can focus on one task at a time**.

##### Acceptance Criteria

1.  6.1.1: The main window is organized into a `QTabWidget` with four tabs: "Search", "Index", "AI Analysis", and "Settings".
2.  6.1.2: The "Search" tab contains the search bar, results views (papers and chunks), and the "Analyze with AI" button.
3.  6.1.3: The "Index" tab contains the Zotero library view, indexing scope controls, and the "Start/Cancel Indexing" button.
4.  6.1.4: The "AI Analysis" tab contains the view for displaying synthesized AI results and the token usage widget.
5.  6.1.5: The "Settings" tab is present as a placeholder for future application settings.
6.  6.1.6: The "Search" tab is disabled until the initial library indexing is complete.
7.  6.1.7: After a successful indexing operation, the UI automatically switches focus to the "Search" tab.

#### Story 6.2: Add Indexing Cancellation

As a **user with a large library**,
I want to be able to **cancel an ongoing indexing process**,
so that **I don't have to force-quit the application if I start a long operation by mistake**.

##### Acceptance Criteria

1.  6.2.1: When indexing begins, the "Start Indexing" button changes to a "Cancel Indexing" button with a distinct visual style (e.g., red background).
2.  6.2.2: Clicking the "Cancel Indexing" button requests a safe stop of the indexing worker thread.
3.  6.2.3: The indexing process stops gracefully after completing the current in-flight item.
4.  6.2.4: The UI provides feedback that the cancellation is in progress and confirms when it is complete.
5.  6.2.5: The index remains in a valid, usable state, containing all items that were successfully processed before the cancellation.

#### Story 6.3: Display Collection Paper Counts

As a **user**,
I want to **see the number of papers in each Zotero collection before I start indexing**,
so that **I can make an informed decision about the scope of the indexing job**.

##### Acceptance Criteria

1.  6.3.1: The "Entire Library" radio button in the Index tab displays the total number of papers (e.g., "Entire Library (1234 papers)").
2.  6.3.2: The collections dropdown list displays the paper count next to each collection's name (e.g., "Cognitive Psychology (87 papers)").
3.  6.3.3: The counts are retrieved via an efficient database query.
4.  6.3.4: Collections with zero papers are clearly marked (e.g., "History of Science (0 papers)").

#### Story 6.4: Implement Non-Modal Chunk Detail Dialog

As a **user**,
I want to **view the full text of a search result chunk in a larger, more readable format**,
so that **I can evaluate its relevance without having to open the full PDF**.

##### Acceptance Criteria

1.  6.4.1: Double-clicking a chunk in the search results list opens a non-modal "Chunk Details" dialog.
2.  6.4.2: The dialog displays the full, unabridged text of the selected chunk in a scrollable text area.
3.  6.4.3: The dialog header shows the source document's title, and sub-headings show metadata like page number and relevance score.
4.  6.4.4: The dialog includes "Previous" and "Next" buttons (and keyboard shortcuts `←`/`→`) to navigate through the list of result chunks without closing the dialog.
5.  6.4.5: The dialog includes buttons to "Copy Text" and "Open PDF".

#### Story 6.5: Reposition Chunk Count Selector

As a **user**,
I want the **control for selecting the number of search results to be located next to the search button**,
so that **it is easily discoverable and I can adjust it as I refine my search**.

##### Acceptance Criteria

1.  6.5.1: The `QSpinBox` for selecting the number of chunks to retrieve is removed from its old location.
2.  6.5.2: The `QSpinBox` is positioned on the same row as the main search input field and search button.
3.  6.5.3: A label "Results:" is placed next to the spin box to clarify its purpose.
4.  6.5.4: The search function correctly uses the value from the newly positioned spin box.

#### Story 6.6: Add API Token Usage Transparency

As a **user providing my own API key**,
I want to **see how many tokens are being used and the estimated cost**,
so that **I can manage my budget and trust the application's usage of the API**.

##### Acceptance Criteria

1.  6.6.1: All API calls (for embedding and AI analysis) record the number of tokens used.
2.  6.6.2: A `TokenUsageWidget` is added to the "AI Analysis" tab.
3.  6.6.3: The widget displays the total tokens consumed and the estimated cost in USD for the current session.
4.  6.6.4: The widget provides a breakdown of API calls by type (e.g., "Embedding Calls", "AI Analysis Calls").
5.  6.6.5: A persistent counter in the main window's status bar shows the running total estimated cost for the session.
6.  6.6.6: A clear disclaimer is included, stating that costs are estimates.

### Epic 7: Enhanced AI Configuration & Chat Experience

#### Expanded Goal:
Enable flexible AI provider configuration and transform AI Analysis into an interactive chat interface with user-controlled retrieval.

#### Story 7.1: Split API Configuration for Embedding vs Chat Models

As a **researcher**,
I want to **configure separate AI providers for embedding generation and chat analysis**,
so that **I can optimize my costs and use the best model for each purpose**.

##### Acceptance Criteria

1.  7.1.1: Settings include separate fields for embedding and chat configurations.
2.  7.1.2: Settings UI shows two distinct configuration sections.
3.  7.1.3: On first launch, existing settings are copied to both new configurations.
4.  7.1.4: `EmbeddingClient` uses `embedding_*` settings; `AIService` uses `chat_*` settings.
5.  7.1.5: Both configurations are validated before saving.

#### Story 7.2: Move Analyze Button to AI Analysis Tab

As a **user**,
I want the **Analyze button to be located in the AI Analysis tab**,
so that **the interface is more intuitive**.

##### Acceptance Criteria

1.  7.2.1: "Analyze" button is removed from the Search tab.
2.  7.2.2: "Analyze Selected Papers" button is added to the AI Analysis tab.
3.  7.2.3: Button is disabled when no search results are available.
4.  7.2.4: Button triggers the same analysis workflow as before.

#### Story 7.3: Remove Duplicate Token Usage from AI Analysis Tab

As a **user**,
I want to **see token usage information only in the status bar**,
so that **the interface is cleaner**.

##### Acceptance Criteria

1.  7.3.1: Token usage widget is removed from the AI Analysis tab.
2.  7.3.2: Status bar token usage display continues to work correctly.
3.  7.3.3: All token tracking functionality remains intact.

#### Story 7.4: Convert AI Analysis to Chat Interface

As a **researcher**,
I want to **interact with AI through a chat interface**,
so that **I can have a natural, iterative conversation about my research**.

##### Acceptance Criteria

1.  7.4.1: A scrollable chat message area replaces the single text output.
2.  7.4.2: User and AI messages have distinct visual styling.
3.  7.4.3: A text input field and "Send" button are at the bottom of the tab.
4.  7.4.4: Clicking "Analyze Selected Papers" starts a new chat session.
5.  7.4.5: A loading indicator is shown while the AI is responding.

#### Story 7.5: Implement Chat Message Handling & API Integration

As a **user**,
I want my **chat messages to be processed by AI with conversation context**,
so that **I can have meaningful back-and-forth discussions**.

##### Acceptance Criteria

1.  7.5.1: User input is captured, displayed in the chat, and the input field is cleared.
2.  7.5.2: Previous messages are included in the API request for context.
3.  7.5.3: `AIService` is called with the user message and conversation history.
4.  7.5.4: AI responses are displayed in the chat.
5.  7.5.5: Token usage is recorded for each chat exchange.

#### Story 7.6: Add Retrieval Toggle & Chunk Count Control

As a **researcher**,
I want to **control whether AI retrieves paper context and how many chunks to include**,
so that **I can balance between detailed context and focused questions**.

##### Acceptance Criteria

1.  7.6.1: A checkbox to "Include search context" and a spinbox for "Number of chunks" (1-20) are added to the AI Analysis tab.
2.  7.6.2: When the toggle is ON, retrieved chunks are prepended to the conversation context.
3.  7.6.3: When the toggle is OFF, only the user's message and history are sent.
4.  7.6.4: The toggle state and chunk count are not persisted across application restarts (session-only).
5.  7.6.5: The default state is ON with 5 chunks.

### Epic 8: Indexing & Search UX Improvements

#### Expanded Goal:
Improve visibility of indexing status and optimize the post-indexing workflow by adding real-time status tracking, indexing summaries, and better default navigation.

#### Story 8.1: Add Indexing Status Column to Paper List

As a **user**,
I want to **see the indexing status of each paper at a glance**,
so that **I can quickly identify which papers are indexed or have issues**.

##### Acceptance Criteria

1.  8.1.1: A new "Status" column is added to the paper list in the Index tab.
2.  8.1.2: The column displays one of four statuses: "Not Indexed", "Indexed", "No PDF", "PDF Error".
3.  8.1.3: Each status has a distinct icon and color (e.g., ✅ for Indexed).
4.  8.1.4: The status for each paper is persisted in the local database.

#### Story 8.2: Update Indexing Status in Real-Time

As a **user**,
I want to **see each paper's status update in real-time as indexing progresses**,
so that **I can monitor progress and identify problems immediately**.

##### Acceptance Criteria

1.  8.2.1: As the `IndexingService` processes each paper, its status is updated in the UI.
2.  8.2.2: The UI remains responsive during the indexing process.
3.  8.2.3: Statuses for "Indexed", "No PDF", and "PDF Error" are correctly assigned.
4.  8.2.4: Re-indexing a paper correctly updates its status.

#### Story 8.3: Display Indexing Summary After Completion

As a **user**,
I want to **see a summary of indexing results after completion**,
so that **I understand what was processed and can quickly identify any issues**.

##### Acceptance Criteria

1.  8.3.1: A summary appears below the "Start Indexing" button after the process completes.
2.  8.3.2: The summary shows counts for "Indexed", "No PDF", and "Errors".
3.  8.3.3: The summary persists until the next indexing operation begins.
4.  8.3.4: The summary is not persisted across application sessions.

#### Story 8.4: Remove Auto-Tab-Switch & Set Default Tab

As a **user**,
I want to **stay on the Index tab after indexing to review results**, and I want the **app to open to the Search tab by default**.

##### Acceptance Criteria

1.  8.4.1: After indexing completes, the application remains on the Index tab.
2.  8.4.2: On application launch, the UI defaults to the Search tab.
3.  8.4.3: Manual tab switching is unaffected.

### Epic 9: Search Tab Action Reorganization

#### Expanded Goal:
Improve the Search tab's button layout and labeling clarity by moving action buttons to the bottom and renaming the ChatGPT export button for better usability.

#### Story 9.1: Move Action Buttons & Rename Copy Button

As a **user**,
I want the **action buttons at the bottom of the Search tab with clear labels**,
so that **the interface is cleaner and I can easily find the actions I need**.

##### Acceptance Criteria



1.  9.1.1: Action buttons ("Open in Zotero", "Open PDF", "Copy as Prompt") are moved to the bottom of the Search tab.

2.  9.1.2: The "Copy to ChatGPT" button is renamed to "Copy as Prompt".

3.  9.1.3: The layout is clean with appropriate spacing.

4.  9.1.4: Button enabled/disabled logic is preserved.

5.  9.1.5: All button functionality is preserved.



### Epic 10: PDF Library Migration



#### Expanded Goal:



This epic addresses the need to migrate the PDF extraction library from PyMuPDF to pdfplumber to resolve licensing issues. The goal is to replace the existing implementation while ensuring that text extraction quality, performance, and error handling remain consistent with the original requirements.



#### Story 10.1: Replace PDF Extraction Implementation



As a **developer**,

I want to **replace the PyMuPDF-based text extraction with a pdfplumber-based implementation**,

so that **the project complies with licensing requirements**.



##### Acceptance Criteria



1.  10.1.1: All code referencing `PyMuPDF` is removed and replaced with `pdfplumber` equivalents.

2.  10.1.2: The application successfully extracts text content from a sample PDF using `pdfplumber`.

3.  10.1.3: The application logs errors for PDFs from which text extraction fails but continues processing other PDFs.

4.  10.1.4: The extracted text is available for subsequent processing steps in the same format as the previous implementation.



#### Story 10.2: Verify Performance and Stability



As a **user**,

I want to **ensure that the new PDF extraction library performs efficiently and does not introduce instability**,

so that **the application remains responsive and reliable**.



##### Acceptance Criteria



1.  10.2.1: PDF extraction performance with `pdfplumber` is benchmarked and found to be comparable to `PyMuPDF` for a representative set of documents.

2.  10.2.2: Memory usage during PDF processing does not significantly increase.

3.  10.2.3: Integration tests for the indexing process pass successfully with the new library.

4.  10.2.4: Error handling for corrupted or unreadable PDFs is robust.
