# 6. Epic Details

## Epic 1: Foundation & Zotero Integration

### Expanded Goal:

This epic aims to lay the groundwork for the ZoteroRAG Desk application by establishing the core desktop application framework and enabling fundamental interaction with the user's local Zotero library. It will ensure the application can correctly identify and access Zotero data, extract text from associated PDF files, and provide a basic user interface for initial setup and status monitoring, all while adhering to the read-only principle.

### Story 1.1: Setup Application Environment

As a **developer**,
I want to **set up the PySide6 application structure and build process**,
so that **I have a functional cross-platform desktop application shell**.

#### Acceptance Criteria

1.  1.1.1: A basic PySide6 window can be launched on Windows, macOS, and Linux.
2.  1.1.2: The application can be packaged into a standalone executable for each target OS.
3.  1.1.3: A basic "About" dialog is accessible from the application menu.

### Story 1.2: Zotero Directory Detection & Selection

As a **user**,
I want the app to **automatically detect my Zotero data directory, or allow me to select it manually**,
so that **the application can access my library**.

#### Acceptance Criteria

1.  1.2.1: On first launch, the application attempts to auto-detect the Zotero data directory.
2.  1.2.2: If auto-detection fails or is incorrect, the user is prompted to browse and select the directory.
3.  1.2.3: The selected Zotero directory path is persisted across application launches.
4.  1.2.4: The application displays a clear message indicating whether a valid Zotero directory is configured.

### Story 1.3: Read Zotero Database & List Items

As a **user**,
I want the app to **read my Zotero database in read-only mode and display a list of my library items**,
so that **I can see my Zotero data within the app**.

#### Acceptance Criteria

1.  1.3.1: The application successfully connects to the `zotero.sqlite` database in read-only mode.
2.  1.3.2: The application can retrieve and display a list of Zotero items (e.g., title, author, year).
3.  1.3.3: The application handles cases where the Zotero database is locked or corrupted gracefully, displaying an informative error.
4.  1.3.4: No write operations are performed on the `zotero.sqlite` database.

### Story 1.4: Extract Text from Attached PDFs

As a **user**,
I want the app to **identify PDF attachments for Zotero items and extract their text content using PyMuPDF**,
so that **the text can be prepared for indexing**.

#### Acceptance Criteria

1.  1.4.1: For each Zotero item with a PDF attachment, the application can locate the PDF file in the `storage/` directory.
2.  1.4.2: The application successfully extracts text content from a sample PDF using PyMuPDF.
3.  1.4.3: The application logs errors for PDFs from which text extraction fails, but continues processing other PDFs.
4.  1.4.4: The extracted text is available for subsequent processing steps.

## Epic 2: Indexing & Local Vector Store

### Expanded Goal:

This epic focuses on building the core data processing pipeline of the application. It will take the raw text extracted in Epic 1 and transform it into a searchable semantic index. This involves chunking the text, calling a cloud API to generate embeddings, and storing these embeddings along with their associated metadata in a local FAISS and SQLite database, ready for retrieval. **Crucially, this epic will also provide users with the control to index their library in manageable parts, such as by collection.**

### Story 2.1: Implement Local Data Storage

As a **developer**,
I want to **set up the local FAISS index and SQLite database**,
so that **I have a persistent storage solution for vector embeddings and their metadata**.

#### Acceptance Criteria

1.  2.1.1: The application can create and initialize an empty SQLite database with the required schema (for documents and chunks).
2.  2.1.2: The application can create and initialize an empty FAISS index.
3.  2.1.3: Both the SQLite database and the FAISS index are stored in a designated application data directory.
4.  2.1.4: The application can successfully save and load the FAISS index and connect to the SQLite database on startup.

### Story 2.2: Implement Text Chunking

As a **user**,
I want the application to **break down the extracted PDF text into smaller, overlapping chunks**,
so that **the text is suitable for generating meaningful embeddings**.

#### Acceptance Criteria

1.  2.2.1: A text chunking function is implemented that splits text into segments of 600 tokens (default, configurable via settings between 400-1000 tokens).
2.  2.2.2: The chunking function includes a 100-token overlap between chunks (configurable via settings between 50-200 tokens).
3.  2.2.3: Each chunk is associated with its source document ID and page number.
4.  2.2.4: The chunking process can handle very short documents (< 100 tokens) without creating empty chunks and very long documents (> 100,000 tokens) without memory issues.
5.  2.2.5: The chunking algorithm uses sentence boundaries where possible to avoid splitting mid-sentence.

### Story 2.3: Implement Cloud Embedding Generation

As a **developer**,
I want to **implement a service that sends text chunks to the OpenAI embedding API and retrieves the resulting vectors**,
so that **I can generate embeddings for my text**.

#### Acceptance Criteria

1.  2.3.1: The application can make a successful API call to the OpenAI embeddings endpoint with a sample text chunk.
2.  2.3.2: The application correctly handles API authentication using a user-provided key (from a temporary config, as full settings are in a later epic).
3.  2.3.3: The application includes error handling for common API issues (e.g., network errors, invalid API key, rate limiting).
4.  2.3.4: The embedding vector is successfully received and can be used in the next step.

### Story 2.4: Implement Indexing Scope Selection

As a **user with a large library**,
I want to **choose what to index (e.g., my entire library, a specific Zotero collection, or selected items)**,
so that **I can manage the indexing time and cost**.

#### Acceptance Criteria

1.  2.4.1: The UI presents options to start indexing for: the entire library, a selected Zotero collection, or a selection of items.
2.  2.4.2: The application can retrieve the list of Zotero collections and display them to the user.
3.  2.4.3: The user's choice of scope is passed to the indexing engine.

### Story 2.5: Build and Update the Index

As a **developer**,
I want an **indexing engine that can process a given set of Zotero items**,
so that **the library can be indexed in user-defined scopes (full library, collection, or selection)**.

#### Acceptance Criteria

1.  2.5.1: An indexing engine receives a list of Zotero items to process based on the user's selected scope.
2.  2.5.2: For each item in the scope, the engine runs the workflow (text extraction -> chunking -> embedding -> storage).
3.  2.5.3: The UI displays real-time progress of the indexing process for the selected scope.
4.  2.5.4: The engine can detect already-indexed items within the scope and skip them to support incremental updates.

## Epic 3: Semantic Search & Results Display

### Expanded Goal:

This epic delivers the core value proposition of the application: semantic search. It will enable users to ask natural language questions, have those questions converted into embeddings, and see the most relevant results retrieved from their local index. The focus is on creating a fluid and intuitive user interface for exploring the search results, both as individual text chunks and as a list of source papers.

### Story 3.1: Implement Search Bar and Query Embedding

As a **user**,
I want **a search bar where I can type my question**,
so that **I can initiate a semantic search**.

#### Acceptance Criteria

1.  3.1.1: The main UI includes a prominent text input field for search queries.
2.  3.1.2: When a user executes a search, the application sends the query text to the configured cloud embedding API.
3.  3.1.3: The application receives the resulting query embedding vector.
4.  3.1.4: The UI indicates that a search is in progress.

### Story 3.2: Implement Vector Search and Retrieval

As a **developer**,
I want to **use the query embedding to search the local FAISS index and retrieve the most relevant text chunks**,
so that **I can find the best matches for the user's question**.

#### Acceptance Criteria

1.  3.2.1: The application performs a similarity search on the FAISS index using the query embedding.
2.  3.2.2: The search returns a list of the top K most similar chunk IDs (where K is configurable).
3.  3.2.3: The application then retrieves the full metadata for these chunks from the SQLite database.
4.  3.2.4: The retrieval process is performant, returning results in under a second for a typical query.

### Story 3.3: Implement Results Display UI

As a **user**,
I want to **see the search results displayed clearly in a split-pane view**,
so that **I can easily explore the relevant papers and text snippets**.

#### Acceptance Criteria

1.  3.3.1: The UI is divided into two main panels: a "Papers" view and a "Chunks" view.
2.  3.3.2: The "Papers" view lists the unique source documents for the retrieved chunks, showing title, authors, year, and the number of matching chunks.
3.  3.3.3: The "Chunks" view displays the text of each relevant snippet, along with its source paper and page number.
4.  3.3.4: Initially, the "Chunks" view shows all retrieved chunks, sorted by relevance.

### Story 3.4: Implement Interactive Results Filtering

As a **user**,
I want to be able to **click on a paper in the "Papers" view to filter the "Chunks" view**,
so that **I can focus on the results from a single document**.

#### Acceptance Criteria

1.  3.4.1: Clicking a paper in the "Papers" view updates the "Chunks" view to show only the chunks from that selected paper.
2.  3.4.2: The UI provides a clear way to remove the filter and return to viewing all chunks.
3.  3.4.3: The application includes a button next to each paper and/or chunk to "Open full PDF", which opens the corresponding PDF file in the system's default viewer.

## Epic 4: AI Integration & Export Workflows

### Expanded Goal:

This epic extends the core search functionality by enabling users to act upon their retrieved information. It will implement the optional in-app AI analysis using a user-provided API key, allowing for synthesized answers with citations. Additionally, it will provide robust export options, including a formatted prompt for external LLMs like ChatGPT and the ability to **export the actual PDF files into a new folder**, enhancing the utility and flexibility of the application.

### Story 4.1: Implement BYOK LLM API Configuration

As a **user**,
I want to **securely enter and manage my OpenAI (or compatible) API key within the application settings**,
so that **I can enable in-app AI analysis**.

#### Acceptance Criteria

1.  4.1.1: A dedicated section in the application settings allows users to input their LLM API key.
2.  4.1.2: The API key is stored securely (e.g., encrypted at rest) and never transmitted externally by the application itself.
3.  4.1.3: A "Test Connection" button verifies the validity of the entered API key without performing a full analysis.
4.  4.1.4: A toggle switch allows users to enable/disable in-app AI analysis, which is off by default.

### Story 4.2: Implement In-App AI Analysis

As a **user**,
when in-app AI analysis is enabled, I want to **click a button to get a synthesized answer based on my query and the retrieved chunks**,
so that **I can quickly understand the key insights**.

#### Acceptance Criteria

1.  4.2.1: An "Analyze with AI" button is visible and enabled when an API key is configured and in-app analysis is toggled on.
2.  4.2.2: Clicking the button sends the user's query and a selection of top retrieved chunks to the configured LLM API.
3.  4.2.3: The application displays the LLM's synthesized answer in a dedicated area of the UI.
4.  4.2.4: The synthesized answer includes inline citations that map back to the source papers and chunks.
5.  4.2.5: The application handles API errors (e.g., rate limits, invalid response) gracefully, displaying informative messages.

### Story 4.3: Implement ChatGPT Export (Text Prompt)

As a **user**,
I want a **"Copy to ChatGPT" button that formats my query and relevant chunks into a ready-to-paste prompt**,
so that **I can easily continue my analysis in an external LLM**.

#### Acceptance Criteria

1.  4.3.1: A "Copy to ChatGPT" button is available on the search results screen.
2.  4.3.2: Clicking the button generates a text block containing the original query, a clear instruction for the LLM, and a numbered list of top N chunks with their metadata.
3.  4.3.3: The generated text block is automatically copied to the user's clipboard.
4.  4.3.4: A brief notification confirms that the content has been copied.

### Story 4.4: Implement PDF File Export

As a **user**,
I want to **export the actual PDF files from my search results to a new folder**,
so that **I have a self-contained collection of relevant papers for sharing or external use**.

#### Acceptance Criteria

1.  4.4.1: An "Export PDFs" button is available on the search results screen.
2.  4.4.2: Clicking the button prompts the user to select a destination folder for the export.
3.  4.4.3: The application creates a new subfolder in the selected destination (e.g., named with the current date/time or a user-provided name).
4.  4.4.4: The application copies all unique PDF files corresponding to the search results into the newly created subfolder.
5.  4.4.5: A notification confirms that the files have been successfully exported and provides the path to the new folder.

## Epic 5: Application Hardening & User Experience

### Expanded Goal:

This epic focuses on transforming the functional prototype into a robust, reliable, and user-friendly product ready for release. It encompasses critical non-functional requirements such as comprehensive error handling, secure management of sensitive user data like API keys, and the creation of a polished, cross-platform installer. The goal is to ensure a stable, secure, and intuitive experience for all users, making the application easy to install, configure, and use.

### Story 5.1: Implement Comprehensive Error Handling & Logging

As a **developer**,
I want to **implement a robust error handling and logging mechanism throughout the application**,
so that **unexpected issues can be gracefully managed and diagnosed**.

#### Acceptance Criteria

1.  5.1.1: All critical operations (e.g., Zotero DB access, PDF extraction, API calls, index operations) include `try-except` blocks or equivalent error handling.
2.  5.1.2: User-facing error messages are clear, concise, and actionable, avoiding technical jargon.
3.  5.1.3: Detailed technical errors are logged to a file (e.g., `debug.log`) with timestamps and relevant context.
4.  5.1.4: The application remains stable and responsive even when non-critical errors occur.

### Story 5.2: Implement Secure API Key Management

As a **user**,
I want my **API keys to be stored and used securely**,
so that **my credentials are protected from unauthorized access**.

#### Acceptance Criteria

1.  5.2.1: API keys are encrypted at rest using an appropriate, platform-specific method (e.g., OS keychain, encrypted file).
2.  5.2.2: API keys are never exposed in plain text in logs or configuration files.
3.  5.2.3: The application only accesses API keys when actively making an API call.
4.  5.2.4: Users are clearly informed about how their API keys are stored and used.

### Story 5.3: Develop Cross-Platform Installers

As a **user**,
I want a **simple, self-contained installer for my operating system**,
so that **I can easily install and run the ZoteroRAG Desk application without manual setup**.

#### Acceptance Criteria

1.  5.3.1: Standalone installers (e.g., `.exe` for Windows, `.dmg` for macOS, AppImage for Linux) are generated.
2.  5.3.2: The installers include all necessary Python runtime and application dependencies.
3.  5.3.3: Installation is a straightforward, wizard-driven process requiring minimal user interaction.
4.  5.3.4: The installed application launches successfully and functions as expected on each target OS.

### Story 5.4: Implement Comprehensive Settings UI

As a **user**,
I want a **clear and organized settings interface**,
so that **I can easily configure all application parameters, including Zotero path, embedding provider, chunking options, and API keys**.

#### Acceptance Criteria

1.  5.4.1: A dedicated "Settings" window or tab is accessible from the main application.
2.  5.4.2: All configurable parameters identified in previous epics (e.g., Zotero path, API keys, chunk size, embedding model) are present and clearly labeled.
3.  5.4.3: Changes to settings are saved persistently and applied correctly.
4.  5.4.4: Tooltips or inline help text explain complex settings.

### Story 5.5: Implement User Onboarding & First-Run Experience

As a **new user**,
I want a **guided first-run experience**,
so that **I can quickly set up the application and understand its core functionality without needing to read documentation**.

#### Acceptance Criteria

1.  5.5.1: On the very first launch, a clear onboarding flow guides the user through Zotero directory selection and initial indexing.
2.  5.5.2: Key privacy and cloud usage disclaimers are presented and acknowledged by the user during onboarding.
3.  5.5.3: The onboarding flow culminates in the user being able to perform their first semantic search.
4.  5.5.4: The application provides visual cues or hints for key features (e.g., "Click here to start indexing").
