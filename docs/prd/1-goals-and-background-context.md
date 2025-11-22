# 1. Goals and Background Context

## 1.1. Goals

*   Enable researchers to leverage their Zotero libraries semantically, finding relevant passages via natural language questions.
*   Provide a low-friction setup with a simple "point at Zotero, click Index" workflow, requiring no manual environment configuration.
*   Offer flexible AI usage through a Bring-Your-Own-Key (BYOK) model for in-app analysis or an export-only mode for use with external tools like ChatGPT.
*   Ensure user privacy by keeping all user data (PDFs, index) on the user's local machine, only sending text snippets to cloud APIs for embedding or analysis.
*   Bridge the gap between finding relevant snippets and reading the full context by providing a simple way to navigate from a search result to the full PDF.

## 1.2. Background Context

Researchers often manage hundreds or thousands of PDFs in Zotero, but finding specific information across these documents is a manual, time-consuming process that relies on basic keyword search and memory. This creates a significant bottleneck in literature reviews and research synthesis. Existing solutions often fall short as they are web-based, require complex technical setup, or do not integrate safely with a local Zotero database.

ZoteroRAG Desk solves this by providing a desktop-first, local-first application that operates in a read-only mode on the user's Zotero library. It extracts text from PDFs, uses a cloud embedding API to create a semantic index stored locally, and provides a user-friendly interface for search and analysis. This unlocks the full value of a researcher's library by enabling powerful, natural language search without compromising privacy or data integrity.

## 1.3. Change Log

| Date | Version | Description | Author |
| :--- | :--- | :--- | :--- |
| 2025-11-18 | 1.0 | Initial draft based on Project Brief and preliminary PRD. | John (PM) |
| 2025-11-22 | 1.1 | Added Epic 6 for UX enhancements based on user feedback. | John (PM) |
