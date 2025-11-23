# 8. Next Steps

## 8.1. UX Expert Prompt

You are the UX Expert. Your task is to create the UI/UX architecture for the ZoteroRAG Desk application. Review this PRD, paying close attention to Section 3 (User Interface Design Goals) and the user stories in Section 6. Your deliverables should include wireframes for the core screens and a component style guide to ensure a consistent and intuitive user experience.

## 8.2. Architect Prompt

You are the Architect. Your task is to create the technical architecture for the ZoteroRAG Desk application. This complete and approved Product Requirements Document (PRD) is your primary source of truth. Your architecture must satisfy all functional and non-functional requirements, adhere to the technical assumptions, and provide a clear implementation plan for the epics and stories defined within. Produce an `architecture.md` document as your primary deliverable.

## Epic 6: UI/UX Enhancements & Usability Polish

### Expanded Goal:

This epic addresses critical usability issues identified after the initial MVP release, based on direct user feedback. The goal is to significantly improve the user experience by reorganizing the UI for clarity, providing users with more control and feedback, and increasing transparency. These changes will make the application more intuitive, efficient, and trustworthy, especially for users on low-resolution screens or with large libraries.

### Story 6.1: Implement Tab-Based Interface

As a **user**,
I want the **application's functions to be organized into separate tabs**,
so that **the interface is less cluttered and I can focus on one task at a time**.

#### Acceptance Criteria

1.  6.1.1: The main window is organized into a `QTabWidget` with four tabs: "Search", "Index", "AI Analysis", and "Settings".
2.  6.1.2: The "Search" tab contains the search bar, results views (papers and chunks), and the "Analyze with AI" button.
3.  6.1.3: The "Index" tab contains the Zotero library view, indexing scope controls, and the "Start/Cancel Indexing" button.
4.  6.1.4: The "AI Analysis" tab contains the view for displaying synthesized AI results and the token usage widget.
5.  6.1.5: The "Settings" tab is present as a placeholder for future application settings.
6.  6.1.6: The "Search" tab is disabled until the initial library indexing is complete.
7.  6.1.7: After a successful indexing operation, the UI automatically switches focus to the "Search" tab.

### Story 6.2: Add Indexing Cancellation

As a **user with a large library**,
I want to be able to **cancel an ongoing indexing process**,
so that **I don't have to force-quit the application if I start a long operation by mistake**.

#### Acceptance Criteria

1.  6.2.1: When indexing begins, the "Start Indexing" button changes to a "Cancel Indexing" button with a distinct visual style (e.g., red background).
2.  6.2.2: Clicking the "Cancel Indexing" button requests a safe stop of the indexing worker thread.
3.  6.2.3: The indexing process stops gracefully after completing the current in-flight item.
4.  6.2.4: The UI provides feedback that the cancellation is in progress and confirms when it is complete.
5.  6.2.5: The index remains in a valid, usable state, containing all items that were successfully processed before the cancellation.

### Story 6.3: Display Collection Paper Counts

As a **user**,
I want to **see the number of papers in each Zotero collection before I start indexing**,
so that **I can make an informed decision about the scope of the indexing job**.

#### Acceptance Criteria

1.  6.3.1: The "Entire Library" radio button in the Index tab displays the total number of papers (e.g., "Entire Library (1234 papers)").
2.  6.3.2: The collections dropdown list displays the paper count next to each collection's name (e.g., "Cognitive Psychology (87 papers)").
3.  6.3.3: The counts are retrieved via an efficient database query.
4.  6.3.4: Collections with zero papers are clearly marked (e.g., "History of Science (0 papers)").

### Story 6.4: Implement Non-Modal Chunk Detail Dialog

As a **user**,
I want to **view the full text of a search result chunk in a larger, more readable format**,
so that **I can evaluate its relevance without having to open the full PDF**.

#### Acceptance Criteria

1.  6.4.1: Double-clicking a chunk in the search results list opens a non-modal "Chunk Details" dialog.
2.  6.4.2: The dialog displays the full, unabridged text of the selected chunk in a scrollable text area.
3.  6.4.3: The dialog header shows the source document's title, and sub-headings show metadata like page number and relevance score.
4.  6.4.4: The dialog includes "Previous" and "Next" buttons (and keyboard shortcuts `←`/`→`) to navigate through the list of result chunks without closing the dialog.
5.  6.4.5: The dialog includes buttons to "Copy Text" and "Open PDF".

### Story 6.5: Reposition Chunk Count Selector

As a **user**,
I want the **control for selecting the number of search results to be located next to the search button**,
so that **it is easily discoverable and I can adjust it as I refine my search**.

#### Acceptance Criteria

1.  6.5.1: The `QSpinBox` for selecting the number of chunks to retrieve is removed from its old location.
2.  6.5.2: The `QSpinBox` is positioned on the same row as the main search input field and search button.
3.  6.5.3: A label "Results:" is placed next to the spin box to clarify its purpose.
4.  6.5.4: The search function correctly uses the value from the newly positioned spin box.

### Story 6.6: Add API Token Usage Transparency

As a **user providing my own API key**,
I want to **see how many tokens are being used and the estimated cost**,
so that **I can manage my budget and trust the application's usage of the API**.

#### Acceptance Criteria

1.  6.6.1: All API calls (for embedding and AI analysis) record the number of tokens used.
2.  6.6.2: A `TokenUsageWidget` is added to the "AI Analysis" tab.
3.  6.6.3: The widget displays the total tokens consumed and the estimated cost in USD for the current session.
4.  6.6.4: The widget provides a breakdown of API calls by type (e.g., "Embedding Calls", "AI Analysis Calls").
5.  6.6.5: A persistent counter in the main window's status bar shows the running total estimated cost for the session.
6.  6.6.6: A clear disclaimer is included, stating that costs are estimates.

## Epic 7: Enhanced AI Configuration & Chat Experience

### Expanded Goal:
Enable flexible AI provider configuration and transform AI Analysis into an interactive chat interface with user-controlled retrieval.

### Story 7.1: Split API Configuration for Embedding vs Chat Models

As a **researcher**,
I want to **configure separate AI providers for embedding generation and chat analysis**,
so that **I can optimize my costs and use the best model for each purpose**.

#### Acceptance Criteria

1.  7.1.1: Settings include separate fields for embedding and chat configurations.
2.  7.1.2: Settings UI shows two distinct configuration sections.
3.  7.1.3: On first launch, existing settings are copied to both new configurations.
4.  7.1.4: `EmbeddingClient` uses `embedding_*` settings; `AIService` uses `chat_*` settings.
5.  7.1.5: Both configurations are validated before saving.

### Story 7.2: Move Analyze Button to AI Analysis Tab

As a **user**,
I want the **Analyze button to be located in the AI Analysis tab**,
so that **the interface is more intuitive**.

#### Acceptance Criteria

1.  7.2.1: "Analyze" button is removed from the Search tab.
2.  7.2.2: "Analyze Selected Papers" button is added to the AI Analysis tab.
3.  7.2.3: Button is disabled when no search results are available.
4.  7.2.4: Button triggers the same analysis workflow as before.

### Story 7.3: Remove Duplicate Token Usage from AI Analysis Tab

As a **user**,
I want to **see token usage information only in the status bar**,
so that **the interface is cleaner**.

#### Acceptance Criteria

1.  7.3.1: Token usage widget is removed from the AI Analysis tab.
2.  7.3.2: Status bar token usage display continues to work correctly.
3.  7.3.3: All token tracking functionality remains intact.

### Story 7.4: Convert AI Analysis to Chat Interface

As a **researcher**,
I want to **interact with AI through a chat interface**,
so that **I can have a natural, iterative conversation about my research**.

#### Acceptance Criteria

1.  7.4.1: A scrollable chat message area replaces the single text output.
2.  7.4.2: User and AI messages have distinct visual styling.
3.  7.4.3: A text input field and "Send" button are at the bottom of the tab.
4.  7.4.4: Clicking "Analyze Selected Papers" starts a new chat session.
5.  7.4.5: A loading indicator is shown while the AI is responding.

### Story 7.5: Implement Chat Message Handling & API Integration

As a **user**,
I want my **chat messages to be processed by AI with conversation context**,
so that **I can have meaningful back-and-forth discussions**.

#### Acceptance Criteria

1.  7.5.1: User input is captured, displayed in the chat, and the input field is cleared.
2.  7.5.2: Previous messages are included in the API request for context.
3.  7.5.3: `AIService` is called with the user message and conversation history.
4.  7.5.4: AI responses are displayed in the chat.
5.  7.5.5: Token usage is recorded for each chat exchange.

### Story 7.6: Add Retrieval Toggle & Chunk Count Control

As a **researcher**,
I want to **control whether AI retrieves paper context and how many chunks to include**,
so that **I can balance between detailed context and focused questions**.

#### Acceptance Criteria

1.  7.6.1: A checkbox to "Include search context" and a spinbox for "Number of chunks" (1-20) are added to the AI Analysis tab.
2.  7.6.2: When the toggle is ON, retrieved chunks are prepended to the conversation context.
3.  7.6.3: When the toggle is OFF, only the user's message and history are sent.
4.  7.6.4: The toggle state and chunk count are not persisted across application restarts (session-only).
5.  7.6.5: The default state is ON with 5 chunks.

## Epic 8: Indexing & Search UX Improvements

### Expanded Goal:
Improve visibility of indexing status and optimize the post-indexing workflow by adding real-time status tracking, indexing summaries, and better default navigation.

### Story 8.1: Add Indexing Status Column to Paper List

As a **user**,
I want to **see the indexing status of each paper at a glance**,
so that **I can quickly identify which papers are indexed or have issues**.

#### Acceptance Criteria

1.  8.1.1: A new "Status" column is added to the paper list in the Index tab.
2.  8.1.2: The column displays one of four statuses: "Not Indexed", "Indexed", "No PDF", "PDF Error".
3.  8.1.3: Each status has a distinct icon and color (e.g., ✅ for Indexed).
4.  8.1.4: The status for each paper is persisted in the local database.

### Story 8.2: Update Indexing Status in Real-Time

As a **user**,
I want to **see each paper's status update in real-time as indexing progresses**,
so that **I can monitor progress and identify problems immediately**.

#### Acceptance Criteria

1.  8.2.1: As the `IndexingService` processes each paper, its status is updated in the UI.
2.  8.2.2: The UI remains responsive during the indexing process.
3.  8.2.3: Statuses for "Indexed", "No PDF", and "PDF Error" are correctly assigned.
4.  8.2.4: Re-indexing a paper correctly updates its status.

### Story 8.3: Display Indexing Summary After Completion

As a **user**,
I want to **see a summary of indexing results after completion**,
so that **I understand what was processed and can quickly identify any issues**.

#### Acceptance Criteria

1.  8.3.1: A summary appears below the "Start Indexing" button after the process completes.
2.  8.3.2: The summary shows counts for "Indexed", "No PDF", and "Errors".
3.  8.3.3: The summary persists until the next indexing operation begins.
4.  8.3.4: The summary is not persisted across application sessions.

### Story 8.4: Remove Auto-Tab-Switch & Set Default Tab

As a **user**,
I want to **stay on the Index tab after indexing to review results**, and I want the **app to open to the Search tab by default**.

#### Acceptance Criteria

1.  8.4.1: After indexing completes, the application remains on the Index tab.
2.  8.4.2: On application launch, the UI defaults to the Search tab.
3.  8.4.3: Manual tab switching is unaffected.

## Epic 9: Search Tab Action Reorganization

### Expanded Goal:
Improve the Search tab's button layout and labeling clarity by moving action buttons to the bottom and renaming the ChatGPT export button for better usability.

### Story 9.1: Move Action Buttons & Rename Copy Button

As a **user**,
I want the **action buttons at the bottom of the Search tab with clear labels**,
so that **the interface is cleaner and I can easily find the actions I need**.

#### Acceptance Criteria



1.  9.1.1: Action buttons ("Open in Zotero", "Open PDF", "Copy as Prompt") are moved to the bottom of the Search tab.

2.  9.1.2: The "Copy to ChatGPT" button is renamed to "Copy as Prompt".

3.  9.1.3: The layout is clean with appropriate spacing.

4.  9.1.4: Button enabled/disabled logic is preserved.

5.  9.1.5: All button functionality is preserved.



## Epic 10: PDF Library Migration



### Expanded Goal:



This epic addresses the need to migrate the PDF extraction library from PyMuPDF to pdfplumber to resolve licensing issues. The goal is to replace the existing implementation while ensuring that text extraction quality, performance, and error handling remain consistent with the original requirements.



### Story 10.1: Replace PDF Extraction Implementation



As a **developer**,

I want to **replace the PyMuPDF-based text extraction with a pdfplumber-based implementation**,

so that **the project complies with licensing requirements**.



#### Acceptance Criteria



1.  10.1.1: All code referencing `PyMuPDF` is removed and replaced with `pdfplumber` equivalents.

2.  10.1.2: The application successfully extracts text content from a sample PDF using `pdfplumber`.

3.  10.1.3: The application logs errors for PDFs from which text extraction fails but continues processing other PDFs.

4.  10.1.4: The extracted text is available for subsequent processing steps in the same format as the previous implementation.



### Story 10.2: Verify Performance and Stability



As a **user**,

I want to **ensure that the new PDF extraction library performs efficiently and does not introduce instability**,

so that **the application remains responsive and reliable**.



#### Acceptance Criteria



1.  10.2.1: PDF extraction performance with `pdfplumber` is benchmarked and found to be comparable to `PyMuPDF` for a representative set of documents.

2.  10.2.2: Memory usage during PDF processing does not significantly increase.

3.  10.2.3: Integration tests for the indexing process pass successfully with the new library.

4.  10.2.4: Error handling for corrupted or unreadable PDFs is robust.
