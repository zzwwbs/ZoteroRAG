# ZoteroRAG Desk – Product Requirements Document (PRD)

## 1. Product Overview

**Working name:**  
ZoteroRAG Desk (placeholder)

**One-line description:**  
A standalone desktop app that connects to a local Zotero library, uses cloud embeddings to build a local RAG index, and lets researchers semantically search, explore, and export relevant chunks or full papers for deeper analysis (either in-app via BYOK or externally via ChatGPT).

**Key characteristics:**

- Desktop GUI (PyQt/Qt or similar) – **no web UI**, **no Zotero add-on**.
- Reads Zotero’s local data (read-only), extracts PDFs, calls **cloud embedding API** to embed chunks.
- Stores embeddings + metadata in a **local vector database**.
- Lets users:
  - Search in natural language.
  - See relevant chunks + papers.
  - Open full PDFs.
  - Either:
    - Analyse in-app via their **own LLM API key (BYOK)**, or
    - Export context as text (and/or file list) to paste into **ChatGPT or another service**.


## 2. Goals & Success Criteria

### 2.1 Primary Goals

1. **Semantic leverage of Zotero libraries**  
   Users can ask questions in natural language and get relevant passages and papers from their Zotero library.

2. **Bridge to full documents for literature review**  
   From useful snippets, users can easily jump to the **full original PDFs** to read the “full story”.

3. **Low-friction setup**  
   No manual Python setup. Users install a desktop app, point it at Zotero, click “Index”.

4. **Flexible AI usage**  
   - BYOK for in-app answers (OpenAI or similar).  
   - Export-only mode for users who prefer to work entirely in ChatGPT’s UI.

5. **Respect privacy while using cloud embeddings**  
   - Only text needed for embeddings and (optionally) LLM answers is sent to the cloud.  
   - All embeddings and indices are stored locally.

### 2.2 Success Metrics (qualitative)

- Users can complete initial indexing and run their first semantic search without reading docs.
- Users report that:
  - Retrieved chunks are relevant.
  - It’s easy to open full PDFs from results.
  - Export for ChatGPT is straightforward.
- No reports of Zotero data corruption.


## 3. Target Users & Personas

- **PhD/Student Researcher** – 500–3,000 papers, heavy Zotero user, wants help with lit reviews.
- **PI/Senior Researcher** – large legacy library, values speed + privacy.
- **Tool-savvy Researcher** – cares about settings and may tweak chunking / filters.


## 4. Scope

### 4.1 In-Scope (v1)

- Standalone **desktop application** (Win/macOS/Linux) with native-like GUI.
- Integration with **local Zotero** via:
  - Reading `zotero.sqlite` (read-only).
  - Mapping items → PDF attachments under `storage/`.
- **Cloud embedding API** usage:
  - For initial index build and incremental updates.
  - For query embeddings.
- **Local vector DB** for retrieval (FAISS/Chroma or similar).
- Retrieval result views:
  - Chunk-level view.
  - Grouped by document/paper.
- Navigation:
  - From chunk → all chunks in that paper for the query.
  - From chunk/paper → open full PDF in system viewer.
- Optional **BYOK** LLM integration for in-app answers.
- Export flows:
  - **Copyable prompt** (question + chunks + instructions) for ChatGPT.
  - Optionally export file paths / list of original documents.

### 4.2 Out-of-Scope (v1)

- No in-app web UI (no browser-based front-end).
- No direct Zotero plugin/addon.
- No multi-user cloud mode.
- No built-in PDF annotation or full-featured viewer (open with system viewer instead).
- No local LLM model in v1 (optional future enhancement).


## 5. Key User Stories

### 5.1 Setup & Indexing

- As a user, I want the app to **detect my Zotero data directory**, or let me select it easily.
- As a user, I want to **start indexing** with one button and see progress.
- As a user, I want to know that the app is **read-only** on Zotero and won’t damage my library.
- As a user, I accept that indexing uses the internet (cloud embeddings), but I want clarity on what is sent.

### 5.2 Search & Browsing

- As a user, I want to ask a question like “How do these papers define structural causal models?” and see:
  - A list of **relevant papers**, and
  - Key **snippets/chunks** from those papers.
- As a user, I want to see **which paper, section, and pages** each snippet comes from.
- As a user, I want to open the **full PDF** for any relevant paper.

### 5.3 Chunk vs Whole Document

- As a user, I want to skim short **snippets** in the app.
- As a user, I want a quick **“Open PDF”** button to read the whole document.
- As a user, I may want to mark several papers as **selected for this lit review**.

### 5.4 BYOK LLM (In-App Answers)

- As a user, I want to optionally **enter my OpenAI (or similar) API key**.
- As a user, after seeing relevant chunks/papers, I want to click **“Analyse here with my API key”** and get:
  - A synthesized answer,
  - With citations mapping back to my papers.
- As a user, I want to be able to **disable** any external LLM calls and still use retrieval + export.

### 5.5 Export to External Services

- As a user, I want to click **“Export for ChatGPT”** and get:
  - My question,
  - Top N snippets with titles/authors/years/sections,
  - A short instruction prompt.
  - All formatted and copied to my clipboard.
- As a user, I want to export a list of **selected documents** (paths or metadata) to manage or upload elsewhere.


## 6. System Architecture (High-Level)

### 6.1 Components

1. **Desktop GUI Application**
   - Built with a desktop GUI framework (e.g. PyQt/PySide).
   - Provides onboarding, search UI, result visualization, settings.

2. **Ingestion & Embedding Module**  
   Responsibilities:
   - Read Zotero DB (`zotero.sqlite`) in **read-only** mode.
   - Discover PDF attachments in `storage/`.
   - Extract text from PDFs.
   - Chunk text into segments with metadata.
   - **Call cloud embedding API** to embed chunks and queries.
   - Store embeddings + metadata in a local vector DB.

3. **Local Vector Store**  
   Possible: FAISS, Chroma, or similar.  
   Responsibilities:
   - Store chunk embeddings & metadata locally (on disk).
   - Provide fast nearest-neighbour search (similarity search).
   - Support simple filters (e.g. by document ID, year).

4. **LLM Integration (BYOK, optional)**  
   Responsibilities:
   - Wrap calls to external LLM API (e.g. OpenAI Chat/Responses).
   - Given query + retrieved chunks, produce a coherent answer with citations.
   - Only active if user has configured an API key and allowed external calls.

5. **Export Engine**  
   Responsibilities:
   - Given query + retrieved chunks, generate a well-formatted text block for ChatGPT.
   - Include question, instructions, and numbered snippets with metadata.
   - Provide file path exports for selected documents.

### 6.2 Data Flow

1. **Setup**
   - App detects or user selects Zotero directory.
   - App confirms read-only usage and explains cloud embedding usage.

2. **Indexing (Using Cloud Embeddings)**
   - For each Zotero item with a PDF:
     - Extract text.
     - Detect section headings if possible.
     - Chunk into ~500–800 token segments with overlap.
     - Attach metadata (zotero key, title, authors, year, section, pages, pdf path).
     - Send chunk text to cloud embedding API → receive embedding vector.
     - Store `{embedding, metadata}` in local vector DB.
   - Store `last_indexed_at` and Zotero item modified time to support incremental indexing.

3. **Query & Retrieval**
   - User enters question.
   - App sends question text to cloud embedding API → query embedding.
   - Local vector DB returns top-k similar chunks.
   - App groups chunks by paper and displays:
     - per-chunk view,
     - per-paper grouped view.

4. **In-App Answer (BYOK)**
   - If BYOK configured and user clicks “Analyse here”:
     - App prepares a context with top N chunks (deduplicated, limited per paper).
     - Calls LLM API with system prompt + user question + context.
     - Shows answer with citations.

5. **Export**
   - On “Export for ChatGPT”:
     - App generates formatted text bundling question + top chunks.
     - Copies to clipboard.
   - Optional: export file list (paths) or open OS file manager.


## 7. Functional Requirements

### 7.1 Onboarding & Settings

- **FR1**: Auto-detect Zotero data directory; allow manual selection.
- **FR2**: Display clear notice that Zotero DB is accessed **read-only**.
- **FR3**: Settings include:
  - Zotero path (view & change).
  - Embedding provider configuration (e.g. API base URL, model name).
  - BYOK LLM API key (e.g. OpenAI key) + “Test connection” button.
  - Chunk size & overlap (basic presets).
  - Max number of chunks per query for display and for LLM.
- **FR4**: Separate toggles:
  - “Use cloud embeddings for indexing and search” (required in v1).
  - “Allow LLM calls for in-app answers” (off by default until BYOK is configured).

### 7.2 Ingestion & Indexing

- **FR5**: Scan Zotero DB for items with at least one PDF attachment.
- **FR6**: For each PDF:
  - Extract text reliably; handle errors gracefully (log and continue).
  - Optionally detect headings (using heuristic patterns like numbered headings or all-caps lines).
- **FR7**: Chunk text into segments:
  - Default: 500–800 tokens per chunk, ~100 tokens overlap.
  - Prepend paper title + section heading to each chunk string before embedding.
- **FR8**: For each chunk:
  - Request embedding from cloud embedding API.
  - Store embedding & metadata in local vector DB.
- **FR9**: Provide UI feedback:
  - Progress bar (# docs / # chunks indexed).
  - “Indexing in progress” indicator.
- **FR10**: Support incremental updates:
  - Detect new / modified Zotero items.
  - Re-index only those items when user triggers “Update index”.

### 7.3 Search & Retrieval

- **FR11**: Main search input for natural language queries.
- **FR12**: For each query:
  - Call cloud embedding API to embed query.
  - Use local vector DB to retrieve top K chunks (configurable).
- **FR13**: Display results in two synchronized views:
  1. **Chunk view**:
     - Shows snippet text (e.g., first 2–3 sentences).
     - Shows paper title, authors, year.
     - Shows section label and page range when available.
  2. **Paper view**:
     - Lists unique papers with:
       - Title, authors, year.
       - Number of matching chunks.
       - Aggregate relevance score.
- **FR14**: Allow user to click a paper to:
  - Filter chunk view to that paper’s chunks for this query.
  - Show “Open full PDF” button.
- **FR15**: “Open full PDF” opens the PDF in the system default viewer.

### 7.4 BYOK LLM Integration (In-App Answers)

- **FR16**: Settings allow user to input an LLM API key (e.g. OpenAI) securely.
- **FR17**: When a key is present and external calls allowed:
  - Enable “Analyse here with my API key” button.
- **FR18**: On click:
  - Select top N chunks across papers (e.g., 10–20, with max M per paper).
  - Construct a prompt:
    - System: instruct model as a careful literature assistant.
    - User: includes original question + numbered snippets with metadata.
  - Call LLM API.
- **FR19**: Display the answer with:
  - Inline citations like `[Smith 2022, Sec 3.2]` mapped from chunk metadata.
  - A bibliography-style list underneath using Zotero metadata.
- **FR20**: If no key is configured:
  - The “Analyse here” button is disabled or shows a tooltip: “Configure an API key in Settings”.

### 7.5 Export for External Services

- **FR21**: Provide a button “Export for ChatGPT” on the results screen.
- **FR22**: On click:
  - Generate a text block containing:
    - Question.
    - Instructions (e.g. “Use only the excerpts below; cite as [Author Year].”).
    - Top N chunks with metadata, in a numbered list.
  - Copy text block to clipboard.
  - Show a small notification: “Exported to clipboard. Paste into ChatGPT.”
- **FR23**: Provide a “Export document list” option:
  - For selected papers, export:
    - Title, authors, year, Zotero key, pdf_path.
  - As:
    - Copyable plain text, and/or
    - Optional CSV file.


## 8. Non-Functional Requirements

### 8.1 Performance

- Initial indexing of ~2,000 PDFs:
  - May take tens of minutes (due to PDF parsing + API calls).
  - App must show progress and remain responsive.
- Query latency:
  - Embedding call + local retrieval should feel snappy:
    - Target: <1s for typical queries once index is built.
- RAM usage:
  - Model itself runs remotely; local app only needs enough RAM for vector DB & metadata (a few hundred MB for large libraries is acceptable).

### 8.2 Reliability & Safety

- All Zotero interactions are **read-only**:
  - No writes to `zotero.sqlite` or `storage/`.
- Index corruption:
  - Index stored separately; if corrupted, can be deleted and rebuilt without affecting Zotero.
- Robust error handling for:
  - Network failures (embedding / LLM calls).
  - API rate limits (backoff, error messaging).
  - PDF parsing failures.

### 8.3 Privacy & Security

- Explain clearly during onboarding:
  - Which text is sent to cloud embedding + LLM APIs (chunks and/or queries).
  - That PDFs and embeddings are stored locally.
- API keys should be:
  - Stored only locally (never transmitted anywhere else).
  - Preferably encrypted at rest if feasible.
- Provide a **“privacy mode”** toggle in settings:
  - When off: no LLM calls allowed (only embeddings).
  - Future: optional “fully local embeddings” mode (v2).

### 8.4 Portability & Packaging

- Ship as self-contained installers/bundles:
  - Windows: .exe / installer.
  - macOS: .dmg / .app.
  - Linux: AppImage or similar.
- Include Python runtime and dependencies; no external env required.

### 8.5 Usability

- Avoid jargon in main UI (“semantic search”, “embeddings”) – instead say “smart search” / “meaning-based search”.
- Provide tooltips & short inline explanations for:
  - Why indexing takes time.
  - Why internet is needed for indexing & questions.
  - What “Analyse here with my API key” does vs “Export for ChatGPT”.


## 9. Data Model (Core Entities)

### 9.1 Document (Paper)

- `doc_id` (internal)
- `zotero_key`
- `title`
- `authors`
- `year`
- `venue`
- `collections` (Zotero collections)
- `tags`
- `pdf_path`
- `zotero_modified_at`
- `last_indexed_at`

### 9.2 Chunk

- `chunk_id`

- `doc_id`
- `text` (chunk content)
- `section_label`
- `page_start`
- `page_end`
- `embedding_vector` (stored in vector DB; may also store in local file/DB)
- `created_at`

### 9.3 Query

- `query_id`
- `query_text`
- `timestamp`
- Optionally: list of retrieved `chunk_ids` for diagnostics.


## 10. UI / Screen Concepts

### 10.1 Onboarding

- Fields:
  - Zotero directory (auto-detected if possible).
- Buttons:
  - “Use detected path” / “Browse…”
  - “Start indexing (uses internet)”
- Text:
  - Brief explanation of what indexing does and that it uses a cloud embedding service.
  - Note that no changes are made to Zotero database.

### 10.2 Main Screen

**Top bar:**

- Search box (“Ask your library a question…”).
- Buttons:
  - “Search”
  - “Settings”
  - “Analyse here (BYOK)” (greyed out until key configured)
  - “Export for ChatGPT”

**Left pane: Papers**

- List of papers:
  - Title (bold)
  - Authors, year
  - # of matching snippets
  - Relevance indicator
- Filters:
  - Year range slider
  - Show only selected / all

**Right pane: Snippets for selected query**

- List of chunks:
  - Snippet text (2–3 sentences)
  - Section label
  - Pages
  - Buttons:
    - “Show all snippets from this paper”
    - “Open full PDF”

**Bottom bar:**

- Status text (e.g. “Index up to date as of 2025-11-18”, or “Indexing 134/2000 documents…”).

### 10.3 Settings

- Zotero path (with “re-detect” and “change”).
- Embedding settings:
  - Info text: “Uses cloud embeddings; requires internet.”
  - Optional model name / region if needed.
- LLM settings:
  - API key field.
  - “Test connection” button.
  - Toggle “Allow in-app AI answers (external API calls)”.
- Index settings:
  - Show # docs, # chunks, approx size.
  - Button “Rebuild index from scratch”.


## 11. Technical Stack (Intent)

- **Language:** Python
- **GUI:** PyQt5 / PySide6 or similar
- **PDF Extraction:** `pdfminer.six` / `pypdf` / `PyMuPDF`
- **Embeddings:** Cloud API (e.g. OpenAI embeddings) via HTTPS
- **Vector DB:** FAISS or Chroma (local serialized index)
- **LLM (optional BYOK):** OpenAI Chat/Responses or similar


## 12. Future Enhancements

- Offline mode with **local embedding models**.
- Built-in PDF viewer with highlighted snippets.
- Deeper Zotero integration: open item directly in Zotero UI.
- Export to markdown/Obsidian with back-links.
- Advanced retrieval options: LLM-based query expansion, re-ranking.
