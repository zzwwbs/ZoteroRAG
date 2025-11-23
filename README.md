# Zotero RAG Desktop

PySide6 desktop client that turns your local Zotero library into a retrieval-augmented research assistant. The app indexes your PDFs locally, runs semantic search via FAISS, and can synthesize answers with any OpenAI-compatible API you configure.

## Highlights
- Guided onboarding detects your Zotero data directory or lets you pick it manually.
- Index whole libraries or specific collections; PDF text is extracted with pdfplumber, chunked, embedded, and stored locally in SQLite + FAISS.
- Semantic search across indexed papers with per-paper and per-chunk views, PDF opening, and export of matched PDFs.
- AI Analysis tab (optional) to summarize search results and chat with context-aware responses; one-click prompt export for ChatGPT.
- Configurable embedding/chat providers, base URLs, and models; API keys can be stored securely via the OS keyring when available.
- Local-first: settings, vector index, metadata DB, and logs live under `~/.zotero_rag`.

## Prerequisites
- Python 3.13+
- Zotero desktop with a local library and PDF attachments accessible from disk
- OpenAI-compatible embedding and chat endpoints + API keys (set in-app or via `OPENAI_API_KEY`)
- Qt/PySide6 runtime libraries (installed automatically via pip) and a `faiss-cpu` wheel compatible with your platform

Optional environment helpers:
- `ZOTERO_DATA_DIR` to point directly to your Zotero data directory (skips discovery)
- `ZOTERORAG_DEBUG=True` to enable verbose logging to `~/.zotero_rag/debug.log`

## Quick Start
1. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # or .venv\\Scripts\\activate on Windows
   ```
2. Install dependencies:
   ```bash
   pip install -e .
   ```
3. Launch the app:
   ```bash
   python -m zoterorag     # or: python main.py
   ```
4. Complete onboarding by selecting your Zotero data directory when prompted. The app will prepare local storage under `~/.zotero_rag`.

After installation you can also use the console script: `zoterorag`.

## Using the App
- **Index tab**: Choose to index the entire library or a specific collection. Progress, token usage, and per-item statuses (Indexed/No PDF/Skipped/Error) are shown. Indexing runs in the background and writes vectors + metadata locally.
- **Search tab**: Run semantic search across the indexed corpus. View results grouped by paper, inspect chunks, open PDFs, export matching PDFs to a folder, or copy a ChatGPT-ready prompt.
- **AI Analysis tab**: When enabled in Settings and with chat API credentials provided, synthesize answers for the current search results or chat with additional follow-up questions. Token usage is tracked in the status bar.
- **Settings tab**: Configure embedding and chat providers independently (base URL, model, API key), toggle AI analysis, set chunk sizes and default search counts, and update the Zotero path. API keys use the OS keyring when available, falling back to the local settings file.

## Configuration & Storage
- Local artifacts live in `~/.zotero_rag/`:
  - `settings.json`: persisted preferences (providers, models, Zotero path, UI options)
  - `zoterorag.db`: metadata, chunks, and token usage history
  - `zoterorag.faiss`: FAISS vector index
  - `debug.log`: rotating log file (DEBUG level when `ZOTERORAG_DEBUG=True`)
- `OPENAI_API_KEY` is used as a fallback for both embedding and chat keys if none are stored.
- Remove the files in `~/.zotero_rag` to reset the app and rebuild the index (back up first if you want to keep token history).

## Packaging Standalone Executables
PyInstaller is the supported bundler. From an environment with the dependencies installed, run:

```bash
python -m scripts.build --target macos
python -m scripts.build --target windows
python -m scripts.build --target linux
# or build multiple targets at once
python -m scripts.build --target macos windows
```

Outputs land in `dist/<target>/` with per-platform work directories in `build/<target>/`. Assets under `src/zoterorag/ui/assets` are bundled automatically when present. The `zr-build` console script is also available after installation. GitHub Releases will include pre-built bundles so users who prefer not to manage Python can download and run directly.

## Pre-built Bundles
- Platforms: macOS (`.app` + placeholder `.dmg`), Windows (`.exe`), and Linux (binary folder).
- Where: Published under GitHub Releases for each tagged version.
- Contents: Bundled UI, FAISS, and assets; uses local `~/.zotero_rag` for settings, index, and logs.
- Usage: Download the archive for your OS, extract/install, and launch the app. You’ll still need local Zotero data and valid embedding/chat API keys.
- Notes: macOS bundles are unsigned/not notarized; expect Gatekeeper prompts. Use right-click → Open or sign/notarize locally if your environment requires it.

## Development & Testing
- Install dev/test tools (e.g., pytest) alongside the app:
  ```bash
  pip install -e . pytest
  ```
- Run the test suite:
  ```bash
  pytest
  ```
- For headless environments, add `QT_QPA_PLATFORM=offscreen` when running UI tests.

## AI-Driven Development Notes
- Built with an agentic BMAD workflow: planning and documentation by Gemini 2.5 Pro, implementation by Codex (GPT-5.1), and QA by Claude Sonnet 4.5.
- AI-generated code can surface subtle issues (edge cases, platform-specific packaging, dependency drift). Please open issues with reproduction steps so we can harden the app.
- GitHub Releases will ship polished bundles for macOS/Windows/Linux alongside source for users who prefer not to manage Python environments.

## Contributing
Pull requests are welcome. See `CONTRIBUTING.md` for guidelines and workflow details.
