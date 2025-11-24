# Contributing to Zotero RAG Desktop

Thanks for your interest in contributing! This project was built with AI assistance, and we welcome both human and AI-generated contributions.

## 🐛 Reporting Bugs

**Before submitting:**
- Check existing issues to avoid duplicates
- Update to the latest version to see if it's already fixed

**When reporting, please include:**
- OS version (macOS 14.x, Windows 11, etc.)
- Python version (`python --version`)
- Installation method (pip, prebuilt executable)
- Steps to reproduce
- Expected vs actual behavior
- Logs from `~/.zotero_rag/debug.log` (redact API keys!)

## 💡 Suggesting Features

Open an issue with:
- Clear description of the feature
- Use case / problem it solves
- Mockups or examples (if UI-related)

## 🔧 Pull Requests

### Setup
```bash
# Fork and clone
git clone https://github.com/YOUR_USERNAME/zotero-rag-desk.git
cd zotero-rag-desk

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# Install in editable mode
pip install -e .
pip install pytest  # for running tests
```

### Development Workflow
1. Create a feature branch: `git checkout -b feature-name`
2. Make your changes
3. Add/update tests if needed
4. Run tests: `pytest`
5. Commit with clear messages
6. Push and open a PR

### Code Standards
- Follow PEP 8 style guidelines
- Add docstrings for public methods
- Include type hints where helpful
- Keep PRs focused (one feature/fix per PR)

### Testing
- Add tests for new features
- Ensure existing tests pass: `pytest`
- For UI changes, test on your target OS
- Headless testing: `QT_QPA_PLATFORM=offscreen pytest`

## 🤖 AI-Generated Code

This project was built with AI assistance. If you use AI tools:
- ✅ Review all AI-generated code before submitting
- ✅ Test thoroughly - AI can miss edge cases
- ✅ Add comments explaining non-obvious logic
- ✅ Mention in PR if substantial AI generation used

## 📝 Documentation

- Update README.md for user-facing changes
- Add inline comments for complex logic
- Update docstrings when changing function signatures

## 🎯 Priority Areas

We especially welcome contributions in:
- Platform-specific testing (macOS/Windows/Linux)
- UI/UX improvements
- Performance optimizations
- Documentation improvements
- Additional embedding/LLM provider support

## 📜 License

By contributing, you agree your contributions will be licensed under the MIT License.

## ❓ Questions?

Open a discussion or issue - we're happy to help!
