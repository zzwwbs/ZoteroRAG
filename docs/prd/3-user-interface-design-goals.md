# 3. User Interface Design Goals

## 3.1. Overall UX Vision

The user experience should be clean, direct, and trustworthy. The application should feel like a powerful utility that respects the user's focus and workflow. The core design principle is to minimize friction between the user's question and the relevant insights within their library. The interface should be simple enough to be used immediately without a tutorial, yet provide access to powerful features for those who need them.

## 3.2. Key Interaction Paradigms

The primary interaction will be a familiar search-and-browse model:

1.  **A Central Search Bar:** A persistent, prominent search bar for entering natural language queries.
2.  **A Split-Pane Results View:** A two-panel layout to display results. One panel will list the source papers, and the other will show the specific text chunks from the selected paper. This allows for easy context switching between a high-level overview and detailed snippets.
3.  **Modal/Separate Screen for Settings:** Configuration options (like API keys and Zotero path) will be handled in a dedicated settings window to keep the main search interface uncluttered.

## 3.3. Core Screens and Views

1.  **Onboarding / Setup Screen:** A simple, one-time screen to detect or set the Zotero library path and initiate the first-time indexing. It must clearly communicate the read-only nature of the app and its use of cloud services.
2.  **Main Search View:** The primary screen of the application, featuring the search bar and the split-pane view for papers and chunks. This view will also contain the main action buttons ("Analyze with BYOK", "Export for ChatGPT").
3.  **Settings Screen:** A separate window for managing the Zotero path, API keys, and other application settings.

## 3.4. Accessibility: WCAG AA

The application should adhere to WCAG 2.1 AA standards to ensure it is usable by people with a wide range of disabilities. This includes considerations for color contrast, keyboard navigation, and screen reader compatibility.

## 3.5. Branding

The branding should be minimal and professional, suitable for an academic tool. The focus should be on clarity and readability rather than a distinct visual identity. A simple logo and a clean, neutral color palette are recommended.

## 3.6. Target Device and Platforms: Cross-Platform

The application will be a standalone desktop application with consistent functionality across Windows, macOS, and Linux.
