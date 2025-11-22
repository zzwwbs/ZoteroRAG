# 3. User Interface Design Goals

## 3.1. Overall UX Vision

The user experience should be clean, direct, and trustworthy. The application should feel like a powerful utility that respects the user's focus and workflow, especially on screens with limited real estate. The core design principle is to minimize friction and scrolling by organizing tasks into logical, focused views. The interface should be simple enough to be used immediately, yet provide access to powerful features for those who need them.

## 3.2. Key Interaction Paradigms

The primary interaction model is being updated from a single, scrollable view to a **task-oriented tabbed interface** to improve usability and reduce clutter.

1.  **Tab-Based Main Window:** The main application window will use a `QTabWidget` to separate primary functions into distinct tabs. This prevents overcrowding and allows for a more focused workflow.
2.  **Centralized Search Controls:** The search bar and its related controls (like the number of chunks to retrieve) will be grouped together for intuitive access.
3.  **Enhanced Results Readability:** Search results (chunks) will have an improved preview format and a dedicated, non-modal dialog for reading full content without leaving the main application context.
4.  **Clear Action Buttons:** Buttons for primary actions like "Start Indexing" will provide clear visual feedback, changing state to "Cancel Indexing" during operation.

## 3.3. Core Screens and Views

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

## 3.4. Accessibility: WCAG AA

The application should adhere to WCAG 2.1 AA standards to ensure it is usable by people with a wide range of disabilities. This includes considerations for color contrast, keyboard navigation (including tab navigation and shortcuts in the chunk detail view), and screen reader compatibility.

## 3.5. Branding

The branding should be minimal and professional, suitable for an academic tool. The focus should be on clarity and readability rather than a distinct visual identity. A simple logo and a clean, neutral color palette are recommended.

## 3.6. Target Device and Platforms: Cross-Platform

The application will be a standalone desktop application with consistent functionality across Windows, macOS, and Linux. The new tabbed design is specifically intended to improve usability on lower-resolution screens (e.g., 1366x768).
