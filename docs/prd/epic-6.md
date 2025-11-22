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
