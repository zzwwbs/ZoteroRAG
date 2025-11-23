# Development Workflow

## Coding Standards

All code contributions must adhere to the guidelines specified in the `CONTRIBUTING.md` file located in the root of the repository. This document details our standards for code quality and consistency. Specifically:

*   **Code Formatting:** We use `black` for uncompromising code formatting to ensure a consistent style across the entire codebase.
*   **Linting:** `ruff` is employed for fast and efficient linting, catching common errors and enforcing best practices.
*   **Type Hinting:** All new Python code must include comprehensive type hints to improve readability, maintainability, and enable static analysis.
*   **Docstrings:** Functions, classes, and modules should be documented using Google-style docstrings to explain their purpose, arguments, and return values.

Before submitting any code, please ensure it complies with these standards. Automated checks are in place via CI/CD to enforce these guidelines.

## Local Development Setup

### Prerequisites
```bash
# Ensure Python 3.13 is installed
python3 --version
# Ensure Git is installed
git --version
```

### Initial Setup
```bash
# 1. Clone the repository
git clone https://github.com/your-org/zotero-rag-desk.git
cd zotero-rag-desk

# 2. Create and activate a Python virtual environment
python3.13 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# 3. Install project dependencies using poetry (or pip if poetry not used)
# Assuming pyproject.toml is configured for poetry or pip
pip install poetry # If poetry is not installed
poetry install     # Or: pip install -e .
```

### Development Commands
```bash
# Start all services (runs the main PySide6 application)
python -m zoterorag

# Start frontend only (same as starting all services for this monolithic app)
python -m zoterorag

# Start backend only (not applicable, core logic runs within the main app)
# N/A

# Run tests
pytest src/tests/
```

## Environment Configuration

### Required Environment Variables
Environment variables are primarily used for development-time flags or sensitive information that should not be hardcoded. For user-specific settings like API keys or Zotero paths, the `SettingsManager` component handles secure local storage.

```bash
# Frontend (.env.local) - Not directly applicable for PySide6, managed by SettingsManager
# N/A

# Backend (.env) - Not directly applicable, managed by SettingsManager
# N/A

# Shared (can be set in shell or via .env file loaded by a tool like python-dotenv for dev)
# ZOTERORAG_DEBUG=True
# Purpose: Enables verbose logging and debug features during development.
```

## Search and AI Analysis Workflow

This workflow describes how a user performs a search and then engages in an interactive chat session for AI analysis.

```mermaid
sequenceDiagram
    actor User
    participant UI as ZoteroRAG Desk App (UI)
    participant SS as SearchService
    participant EC as EmbeddingClient
    participant VDM as VectorDBManager
    participant MDM as MetadataDBManager
    participant AIS as AIService
    participant OAI as OpenAI-compatible API

    User->>UI: Enters search query and hits 'Enter'
    UI->>UI: Disables search button, shows loading indicator
    UI->>SS: search(query)
    activate SS

    SS->>EC: get_embedding(query)
    SS->>VDM: search_vectors(query_vector, k=50)
    SS->>MDM: get_chunks_by_vector_ids(vector_ids)
    SS->>MDM: get_documents_for_chunks(chunks)
    SS-->>UI: Returns formatted search results
    deactivate SS

    UI->>UI: Re-enables UI, displays results in Papers/Chunks view
    User->>UI: Reviews results, switches to AI Analysis Tab

    loop Interactive Chat Session (Epic 7)
        User->>UI: Enters chat message
        UI->>UI: Displays user message in chat history
        UI->>AIS: get_chat_response(history, include_context, top_chunks)
        activate AIS

        AIS->>OAI: POST /v1/chat/completions (prompt with history + optional context)
        activate OAI
        OAI-->>AIS: Returns synthesized answer
        deactivate OAI

        AIS-->>UI: Returns synthesized answer and token usage
        deactivate AIS

        UI->>UI: Displays AI response in chat history
    end
```
