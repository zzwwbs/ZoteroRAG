# Deployment and Release Management

This section addresses the requirement for a portable, self-contained application (NFR7).

*   **Packaging (PyInstaller):** The primary build tool will be `PyInstaller`. A build script (`scripts/build.py`) will be created to automate the process of generating executables for each target platform.
    *   **Windows:** An `.exe` file, likely bundled into an MSI installer.
    *   **macOS:** A `.app` bundle, distributed inside a `.dmg` disk image. The application will be code-signed and notarized to comply with macOS security policies.
    *   **Linux:** An AppImage, which provides a distribution-agnostic package.
*   **CI/CD (GitHub Actions):** A workflow will be set up in `.github/workflows/ci.yaml`.
    *   **On Pull Request:** The workflow will run `pytest` to execute all unit and integration tests with minimum 80% code coverage requirement. Tests must pass on all three platforms (Windows, macOS, Linux).
    *   **On Push to Main:** The workflow will run linting (`ruff`), type checking (`mypy`), and security scanning (`bandit`).
    *   **On Tag (e.g., `v1.0.0`):** The workflow will trigger the `scripts/build.py` script on Windows, macOS, and Linux runners. It will then automatically create a new GitHub Release and upload the generated installers/packages as release assets.
    *   **Test Requirements:** Unit tests must complete in under 2 minutes. Integration tests in under 5 minutes.
*   **Release Versioning:** The project will use Semantic Versioning (SemVer).
