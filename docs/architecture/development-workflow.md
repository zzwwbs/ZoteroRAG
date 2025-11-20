# Development Workflow

## Coding Standards

All code contributions must adhere to the guidelines specified in the `CONTRIBUTING.md` file located in the root of the repository. This document details our standards for code formatting (`black`), linting (`ruff`), type hinting, and docstrings. Before submitting any code, please ensure it complies with these standards.

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

This workflow describes how a user performs a search and optionally uses the AI analysis feature.

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
    activate EC
    EC->>OAI: POST /v1/embeddings (query)
    activate OAI
    OAI-->>EC: Returns query_vector
    deactivate OAI
    EC-->>SS: Returns query_vector
    deactivate EC

    SS->>VDM: search_vectors(query_vector, k=50)
    activate VDM
    VDM-->>SS: Returns list of vector_ids
    deactivate VDM

    SS->>MDM: get_chunks_by_vector_ids(vector_ids)
    activate MDM
    MDM-->>SS: Returns list of Chunk objects
    deactivate MDM

    SS->>MDM: get_documents_for_chunks(chunks)
    activate MDM
    MDM-->>SS: Returns enriched Document info
    deactivate MDM

    SS-->>UI: Returns formatted search results
    deactivate SS

    UI->>UI: Re-enables UI, displays results in Papers/Chunks view
    User->>UI: Reviews results

    alt Optional: User clicks "Analyze with AI"
        UI->>AIS: analyze_chunks(query, top_chunks)
        activate AIS

        AIS->>OAI: POST /v1/chat/completions (prompt with query + chunks)
        activate OAI
        OAI-->>AIS: Returns synthesized answer
        deactivate OAI

        AIS-->>UI: Returns synthesized answer
        deactivate AIS

        UI->>User: Displays AI-generated summary with citations
    end
```
