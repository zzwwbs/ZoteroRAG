# Contributing to ZoteroRAG Desk

First off, thank you for considering contributing to ZoteroRAG Desk! Your help is greatly appreciated.

This document outlines the coding standards and practices for this project to ensure consistency, readability, and quality. All contributions, whether from human developers or AI agents, are expected to adhere to these guidelines.

## Coding Standards

### 1. Code Formatting (Black)

All Python code in this repository is formatted using the `black` code formatter with its default settings. Before committing any changes, please ensure your code is formatted by running `black` on your changed files.

```bash
# Install black if you haven't already
pip install black

# Format the entire source directory
black src/
```

### 2. Linting and Style (Ruff)

We use `ruff` for linting and enforcing style consistency beyond what `black` provides. `ruff` is extremely fast and helps catch common errors, style issues, and automatically sorts imports.

Your code must pass `ruff` checks without any errors.

```bash
# Install ruff if you haven't already
pip install ruff

# Check the source directory for issues
ruff check src/

# Ruff can also fix many issues automatically
ruff check src/ --fix
```

### 3. Type Hinting

All function and method signatures **must** include type hints for all arguments and return values, as specified in PEP 484. This is crucial for code clarity, static analysis, and AI agent comprehension.

**Correct:**
```python
def get_document(doc_id: int) -> Document | None:
    # ... implementation
```

**Incorrect:**
```python
def get_document(doc_id):
    # ... implementation
```

### 4. Docstrings (Google Style)

All public modules, classes, functions, and methods should have a docstring that follows the [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html#3.8-comments-and-docstrings).

A good docstring provides a brief summary of the object's purpose and includes descriptions of arguments, return values, and any exceptions raised.

**Example:**
```python
def search(self, query: str, top_k: int = 10) -> list[dict]:
    """Performs a semantic search and returns formatted results.

    Args:
        query: The natural language query from the user.
        top_k: The maximum number of results to return.

    Returns:
        A list of dictionaries, where each dictionary represents a
        formatted search result.
    """
    # ... implementation
```

### 5. Commit Messages

Please write clear and concise commit messages. The first line should be a short summary (50 characters or less), followed by a blank line and then a more detailed explanation if necessary.

---

By following these guidelines, you help us maintain a high-quality and maintainable codebase. Thank you!
