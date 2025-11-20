# Project Brief: ZoteroRAG Desk

## Executive Summary

ZoteroRAG Desk is a standalone desktop app that connects to a local Zotero library, uses cloud embeddings to build a local RAG index, and lets researchers semantically search, explore, and export relevant chunks or full papers. The primary problem it solves is the inefficiency researchers face when trying to perform semantic searches across their entire collection of PDFs in Zotero. The target market includes PhD students, senior researchers, and other tool-savvy academics who rely heavily on Zotero. The key value proposition is unlocking the full value of a researcher's library by enabling powerful, natural language search without requiring complex technical setup.

## Problem Statement

Researchers often manage hundreds or thousands of PDFs in Zotero, but finding specific information across these documents is a manual, time-consuming process that relies on basic keyword search and memory. This creates a significant bottleneck in literature reviews and research synthesis, slowing down the research process and leading to missed connections between papers. Existing solutions fall short because they are often web-based, require technical setup (like Python scripts), or don't integrate directly and safely with the local Zotero database. As the volume of published research grows, the need for tools that can intelligently search and synthesize information becomes increasingly critical.

## Proposed Solution

The proposed solution is a desktop GUI application (built with PyQt/Qt) that operates in a read-only mode on a user's local Zotero library. It extracts text from PDFs, uses a cloud embedding API to create a semantic index stored in a local vector database (like FAISS or Chroma), and provides a user-friendly interface for search and analysis.

**Key Differentiators:**
- **Desktop-first & Local-first:** All user data (PDFs, index) remains on the user's machine, respecting privacy.
- **Zero-friction setup:** Packaged as a standalone app, requiring no manual Python or environment configuration.
- **Flexible AI Usage:** Supports both in-app analysis via a user's own API key (BYOK) and an export-only workflow for use with external tools like ChatGPT.
- **Safe Zotero Integration:** Strictly read-only access to the Zotero database ensures no risk of data corruption.

The long-term vision is for this tool to become the go-to solution for any researcher wanting to have a "conversation" with their Zotero library, bridging the gap between document storage and knowledge discovery.

## Target Users

- **Primary User Segment: PhD/Student Researcher:** Manages a library of 500-3,000 papers, is a heavy Zotero user, and needs tools to accelerate and deepen their literature reviews.
- **Secondary User Segment: PI/Senior Researcher:** Has a large, legacy library of papers, values speed and privacy, and is unlikely to engage in complex technical setups.
- **Secondary User Segment: Tool-savvy Researcher:** Cares about having control over settings and is interested in tweaking parameters like chunking and filtering.

## Goals & Success Metrics

### Business Objectives
- Enable semantic leverage of Zotero libraries, allowing users to find relevant passages via natural language questions.
- Provide a low-friction setup with a simple "point at Zotero, click Index" workflow.
- Offer flexible AI usage through BYOK for in-app analysis or an export-only mode.

### User Success Metrics
- Users can complete initial indexing and their first search without needing to consult documentation.
- Users report that retrieved chunks are highly relevant to their queries.
- Users find it easy and intuitive to navigate from a search result to the full PDF.
- The export-to-ChatGPT function is straightforward and provides a useful, well-formatted prompt.

### Key Performance Indicators (KPIs)
- **Activation Rate:** Percentage of users who successfully complete indexing and perform at least one search.
- **Qualitative Feedback Score:** Average rating from user surveys on relevance, ease of use, and safety.
- **Adoption of BYOK vs. Export:** Ratio of users who configure an API key vs. those who exclusively use the export function.

## MVP Scope

### Core Features (Must Have)
- **Desktop Application:** A standalone GUI application for Windows, macOS, and Linux.
- **Zotero Integration:** Read-only access to the local `zotero.sqlite` database and associated PDF files in the `storage/` directory.
- **Cloud-based Indexing:** Use a cloud API to embed PDF text chunks and store them in a local vector database (FAISS/Chroma).
- **Semantic Search UI:** An interface to enter natural language queries and view results.
- **Result Visualization:** Display results as both a list of relevant text chunks and a list of the source papers, with clear metadata (author, year, etc.).
- **PDF Navigation:** A button to open the full PDF for any search result in the system's default viewer.
- **BYOK LLM Integration:** Optional in-app analysis using a user-provided OpenAI (or similar) API key.
- **ChatGPT Export:** A "copy to clipboard" function that formats the query and top results into a ready-to-paste prompt for external LLM services.

### Out of Scope for MVP
- In-app web UI or any browser-based front-end.
- A direct Zotero plugin/addon.
- Multi-user or cloud-hosted modes.
- A built-in PDF viewer or annotation tools.
- Support for local/on-device LLM models.

## Post-MVP Vision

### Phase 2 Features
- Offline mode with local embedding models to enhance privacy and remove the internet dependency.
- A built-in PDF viewer that highlights the relevant snippets found by the search.
- Deeper Zotero integration, such as a button to open an item directly in the Zotero UI.
- Export to Markdown/Obsidian with backlinks to facilitate integration with other research workflows.

### Long-term Vision
To evolve into an indispensable research assistant that not only retrieves information but also helps synthesize it, identify research gaps, and suggest new connections within a user's library.

### Expansion Opportunities
- Integrate with other reference managers (e.g., Mendeley).
- Develop advanced retrieval options like LLM-based query expansion and re-ranking of results.

## Technical Considerations

### Platform Requirements
- **Target Platforms:** Windows, macOS, Linux.
- **Performance Requirements:** Queries should return results in under one second. Initial indexing of a large library may take several minutes, but the application must remain responsive during this process.

### Technology Preferences
- **Language:** Python
- **GUI:** PyQt5 / PySide6
- **PDF Extraction:** `pdfminer.six` / `pypdf` / `PyMuPDF`
- **Embeddings:** Cloud API (e.g., OpenAI embeddings)
- **Vector DB:** FAISS or Chroma (local index)

### Architecture Considerations
- **Service Architecture:** A monolithic desktop application structure is sufficient for the MVP.
- **Integration Requirements:** Read-only integration with the local Zotero SQLite database is a core requirement.
- **Security/Compliance:** API keys must be stored locally and securely (e.g., encrypted at rest). Clear privacy notices explaining what data is sent to cloud APIs are mandatory.

## Constraints & Assumptions

### Constraints
- **Technical:** The application relies on third-party cloud APIs for embeddings, introducing a dependency and potential cost. The solution must be a standalone desktop app, not a web service or Zotero plugin.
- **Resources:** Development will be constrained by the resources available for this project.

### Key Assumptions
- Users have their Zotero data stored locally on their machine.
- Users are willing to use a cloud service for embeddings in exchange for higher-quality search results.
- Users are comfortable with either providing their own API key (BYOK) or using an export-based workflow.
- The value of semantic search is high enough to justify the initial time investment required for indexing.

## Risks & Open Questions

### Key Risks
- **API Rate Limiting/Cost:** Heavy use or very large libraries could lead to high costs or rate-limiting from the embedding API provider.
- **PDF Parsing Failures:** The text extraction process may fail or produce garbled text for certain documents, leading to a poor user experience and incomplete search results.
- **User Trust:** Users may be hesitant to grant an application access to their Zotero library or to send document text to a cloud API, even with privacy assurances.

### Open Questions
- Which embedding provider offers the best balance of performance, cost, and quality for this specific use case?
- What are the optimal default settings for chunk size and overlap for academic papers?
- How should the UI gracefully handle cases where PDF text extraction fails for a document?

### Areas Needing Further Research
- A comparative analysis of embedding APIs (e.g., OpenAI, Cohere, Google).
- Best practices and robust libraries for parsing a wide variety of PDF formats and layouts.

## Appendices

### A. Research Summary
The initial product concept, user stories, and technical requirements are detailed in the `zotero-rag-prd.md` document, which served as the primary input for this brief.

## Next Steps

### Immediate Actions
1. Validate the core assumptions with a small group of target users (PhD students, researchers).
2. Develop a technical prototype focusing on the core indexing and search functionality.
3. Create wireframes for the main application UI to guide development.

### PM Handoff
This Project Brief provides the full context for ZoteroRAG Desk. Please start in 'PRD Generation Mode', review the brief thoroughly to work with the user to create the PRD section by section as the template indicates, asking for any necessary clarification or suggesting improvements.
