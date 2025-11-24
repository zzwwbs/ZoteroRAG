# Publish Plan (Public Branch + Releases)

This plan describes how to publish a lean, user-facing `public` branch and attach prebuilt binaries for macOS and Windows releases, while keeping full dev assets on `main`.

## Branching Model
- Keep `main` as the full development branch (all docs, tests, scripts).
- Maintain a persistent `public` branch for users. Do not recreate it each time; refresh it as needed.

## What to Include on `public`
- `src/` (runtime code)
- `pyproject.toml`, `README.md` (user-focused), `LICENSE`
- Minimal assets required at runtime
- Optional: a small smoke-test subset (`tests/core` and `tests/test_zotero_manager.py`) if desired

## What to Exclude on `public`
- **BMAD and AI agent directories:** `.bmad-core/`, `.claude/`, `.gemini/`, `.cursor/`, `.trae/`, `.ai/` (internal dev workflows)
- **Internal docs:** `docs/prd/`, `docs/architecture/`, `docs/stories/`, `docs/project/`, `docs/qa/`, `zotero-rag-prd.md`
- **Dev documentation:** `docs/publish-plan.md`, `docs/brief.md`, `docs/ux-enhancements-specification.md`, `AGENTS.md`
- **Dev/benchmark scripts:** `scripts/benchmarking/`, tuning scripts, profiling scripts
- **UI-heavy tests:** `tests/ui/` (requires PySide6 setup, not suitable for lean distribution)
- **Test artifacts:** `tests/test.pdf` (large file), `profile.out`
- **Local data/logs:** `__queuestorage__/`, build outputs
- **Build artifacts:** `build/`, `dist/`, `*.egg-info`, `*.spec`
- **Virtual envs/caches:** `.venv/`, `__pycache__/`, `.pytest_cache/`, `.mypy_cache/`
- **IDE configs:** `.vscode/`, `.idea/`, `.DS_Store`
- **Dev configs:** `opencode.jsonc`

## Preparing the `public` Branch (First Time)
```bash
git checkout -b public

# Use the prune script for consistent cleanup
chmod +x scripts/prune_public.sh
./scripts/prune_public.sh

# Review changes
git status

# Verify no secrets leaked
git log --all --full-history -- '*settings.json' '*api*key*'

# Commit and push
git add -A
git commit -m "Prepare public branch with lean distribution"
git push origin public

# Set public as default branch on GitHub (in repository settings)
```

## Refreshing `public` After Main Changes
```bash
git checkout public
git fetch origin
git merge origin/main     # or rebase if preferred

# Reapply pruning using the script
./scripts/prune_public.sh

# Review and commit
git status
git add -A
git commit -m "Refresh public branch from main"   # if changes present
git push origin public
```

## GitHub Releases with Prebuilt Apps
1. Build locally per platform:
   - macOS: produce signed/notarized `.app` packaged as `.dmg` or zipped bundle.
   - Windows: produce `.exe`/MSI or zipped folder.
   - Name artifacts clearly: `zotero-rag-desk-macOS-universal-vX.Y.Z.dmg`, `zotero-rag-desk-windows-x64-vX.Y.Z.exe`.
2. Tag and release:
   ```bash
   git tag vX.Y.Z
   git push origin vX.Y.Z
   ```
   Then draft a GitHub Release for that tag, attach both artifacts, and add SHA256 checksums plus release notes.
3. (Optional) Automate with GitHub Actions:
   - Workflow triggers on tag push.
   - Matrix build: `macos-latest`, `windows-latest`.
   - Run your PyInstaller build script.
   - Upload artifacts to the GitHub Release using `actions/upload-release-asset`.
   - Include signing/notarization steps for macOS if needed (store secrets in repo settings).

## Checklist Before Publishing

### Security & Licensing
- [ ] LICENSE file exists (MIT) and committed to both branches
- [ ] No API keys, tokens, or secrets in code or git history
- [ ] Run: `git log --all --full-history -- '*settings.json' '*api*key*'` (should be empty)
- [ ] All dependencies' licenses are compatible (MIT, BSD, Apache 2.0)
- [ ] SECURITY.md created with API key security guidance
- [ ] README mentions keyring usage and API key best practices

### Documentation
- [ ] README.md updated with badges (License, Python version, etc.)
- [ ] Installation instructions tested on clean machine
- [ ] Prerequisites clearly listed
- [ ] CONTRIBUTING.md exists (use CONTRIBUTING.public.md for public branch)

### Public Branch Cleanup
- [ ] BMAD directories removed: `.bmad-core/`, `.claude/`, `.gemini/`, `.cursor/`, `.trae/`
- [ ] Internal docs removed: `docs/prd/`, `docs/architecture/`, `docs/stories/`, `docs/project/`, `docs/qa/`
- [ ] Dev scripts removed: `scripts/benchmarking/`, tuning/profiling scripts
- [ ] UI tests removed: `tests/ui/` (require PySide6 setup)
- [ ] Large test files removed: `tests/test.pdf` if > 1MB
- [ ] Personal configs removed: `.vscode/`, `.idea/`, `.DS_Store`
- [ ] Dev configs removed: `AGENTS.md`, `opencode.jsonc`, `zotero-rag-prd.md`
- [ ] Prune script executed: `./scripts/prune_public.sh`

### Testing
- [ ] Run smoke tests on `main`
- [ ] Core tests work on `public` branch
- [ ] Fresh clone of `public` branch installs and runs successfully
- [ ] Prebuilt executables launch on target platforms

### GitHub Repository Setup
- [ ] Set `public` as default branch
- [ ] Add repository description (short, under 100 chars)
- [ ] Add topics/tags: `python`, `pyside6`, `faiss`, `zotero`, `rag`, `semantic-search`, `desktop-app`
- [ ] Enable Issues
- [ ] Enable Discussions (optional)
- [ ] Configure branch protection for `public` (optional but recommended)

### Release Preparation
- [ ] Version number set in `src/zoterorag/__version__.py`
- [ ] Tag created: `git tag -a v1.0.0 -m "Initial public release"`
- [ ] Release notes drafted
- [ ] Prebuilt binaries tested on target OS versions
- [ ] SHA256 checksums generated and included
- [ ] Known issues documented in release notes
- [ ] macOS Gatekeeper workaround documented
