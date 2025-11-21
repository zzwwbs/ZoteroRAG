# Zotero RAG Desktop Shell

Minimal PySide6 shell for the Zotero Research Assistant Generator (RAG) desktop experience.

## Running from Source
1. Create a Python 3.13+ virtual environment and activate it:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # or .venv\\Scripts\\activate on Windows
   ```
2. Install the project dependencies:
   ```bash
   pip install -e .
   ```
3. Launch the application:
   ```bash
   python main.py
   ```
   This will open the window with the File menu that exposes the About dialog.

## Packaging Standalone Executables
PyInstaller is the supported bundling tool for each platform. Prepare the environment as described above, then run:

```bash
python -m scripts.build --target windows
python -m scripts.build --target macos
python -m scripts.build --target linux
```

Each invocation drives `PyInstaller` with supplemental work/dist directories under `build/<target>` and `dist/<target>`. You can run multiple targets at once by listing them after `--target`.

If you run `python -m scripts.build` without `--target`, it builds for the current OS only. Assets under `src/zoterorag/ui/assets` are bundled automatically when present. On macOS the script also creates a placeholder `.dmg` alongside the `.app` bundle; integrate codesign/notarization there as needed.

## Directory Highlights
- `src/zoterorag/`: Application package with `main` launcher and UI scaffolding.
- `main.py`: Application entry point compatible with both direct execution and packaging workflows.
- `scripts/build.py`: Convenience script invoking `PyInstaller` per targeted platform.

## Testing
Manual verification is expected for the foundational UI and packaging flows. Automated tests will come later once core functionality stabilizes.
