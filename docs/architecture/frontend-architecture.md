# Frontend Architecture

## Component Architecture

The UI will be built using a composition of custom `QWidget` classes, organized into a **task-oriented tabbed interface** to improve usability and reduce clutter, as specified in the PRD (3.2, 6.1).

### Component Organization
The UI components will be organized into Python modules based on their function within the new tabbed structure:

```plaintext
src/
└── ui/
    ├── __init__.py
    ├── main_window.py          # Main application window with QTabWidget (Epic 6.1)
    ├── search_tab.py           # "Search" tab with controls, results, and bottom action buttons (Epic 9.1)
    ├── index_tab.py            # "Index" tab with library, indexing controls, status column, and summary (Epic 8)
    ├── analysis_tab.py         # "AI Analysis" tab, now an interactive chat interface (Epic 7)
    ├── settings_tab.py         # "Settings" tab for app configuration (including split API configs, Epic 7.1)
    ├── chunk_detail_dialog.py  # Non-modal dialog for full chunk viewing (Epic 6.4)
    ├── onboarding_view.py      # Initial setup/welcome screen
    └── widgets/                # Reusable custom widgets
        ├── __init__.py
        └── ...                 # TokenUsageWidget is now a controller, not a visible widget
```

### Component Template
Each major UI component will be a class inheriting from `QWidget` or a more specific Qt class. They will use signals to communicate events to the `MainWindow` controller.

```python
# Example: src/ui/search_tab.py (Epic 9.1 - Reorganized actions)
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, 
    QPushButton, QSpinBox, QLabel, QListWidget
)
from PySide6.QtCore import Signal

class SearchTab(QWidget):
    # Signal emitted when the user executes a search
    search_triggered = Signal(str, int)
    # Signal emitted when user double-clicks a chunk (Epic 6.4)
    chunk_detail_requested = Signal(object, int, int)  # chunk, index, total
    # Signals for bottom action buttons (Epic 9.1)
    open_in_zotero_requested = Signal()
    open_pdf_requested = Signal()
    copy_as_prompt_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.layout = QVBoxLayout(self)
        
        # Search controls layout (Epic 6.5 - grouped controls)
        search_controls_layout = QHBoxLayout()
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Enter your search query...")
        
        self.results_count_spinner = QSpinBox()
        self.results_count_spinner.setMinimum(1)
        self.results_count_spinner.setMaximum(100)
        self.results_count_spinner.setValue(5)
        self.results_count_spinner.setToolTip("Number of chunks to retrieve")
        
        self.search_button = QPushButton("Search")
        
        search_controls_layout.addWidget(self.search_bar, stretch=3)
        search_controls_layout.addWidget(QLabel("Results:"))
        search_controls_layout.addWidget(self.results_count_spinner)
        search_controls_layout.addWidget(self.search_button)

        # Add search controls to main layout
        self.layout.addLayout(search_controls_layout)
        
        # Add results views (papers, chunks) to the layout
        self.layout.addWidget(QLabel("Papers:"))
        self.paper_list = QListWidget()
        self.layout.addWidget(self.paper_list)
        
        self.layout.addWidget(QLabel("Chunks (double-click for full text):"))
        self.chunk_list = QListWidget()
        self.layout.addWidget(self.chunk_list)

        # Bottom action buttons (Epic 9.1)
        action_buttons_layout = QHBoxLayout()
        self.open_zotero_button = QPushButton("Open in Zotero")
        self.open_pdf_button = QPushButton("Open PDF")
        self.copy_prompt_button = QPushButton("Copy as Prompt") # Renamed from "Copy to ChatGPT"
        
        action_buttons_layout.addStretch() # Align buttons to the right
        action_buttons_layout.addWidget(self.open_zotero_button)
        action_buttons_layout.addWidget(self.open_pdf_button)
        action_buttons_layout.addWidget(self.copy_prompt_button)
        self.layout.addLayout(action_buttons_layout)

        # Connect signals
        self.search_button.clicked.connect(self._on_search)
        self.chunk_list.itemDoubleClicked.connect(self._on_chunk_double_clicked)
        self.copy_prompt_button.clicked.connect(self.copy_as_prompt_requested)
        # ... connect other action button signals ...

    def _on_search(self):
        query = self.search_bar.text()
        count = self.results_count_spinner.value()
        if query:
            self.search_triggered.emit(query, count)
    
    def _on_chunk_double_clicked(self, item):
        chunk_index = self.chunk_list.row(item)
        total_chunks = self.chunk_list.count()
        chunk_data = item.data(Qt.UserRole)
        self.chunk_detail_requested.emit(chunk_data, chunk_index, total_chunks)

```

## State Management Architecture

We will use a centralized state object combined with PySide6's native signals and slots mechanism, which is an implementation of the Observer pattern.

### State Structure
A Python `dataclass` will hold the application's shared state.

```python
# Example: src/ui/state.py
from dataclasses import dataclass, field
from typing import Optional, List
from ..core.data.models import TokenUsage

@dataclass
class AppState:
    zotero_path: Optional[str] = None
    is_indexing: bool = False
    indexing_progress: float = 0.0
    search_results: List[dict] = field(default_factory=list)
    selected_paper: Optional[dict] = None
    token_usage_history: List[TokenUsage] = field(default_factory=list)
    current_session_cost: float = 0.0
    chat_history: List[dict] = field(default_factory=list) # Epic 7.4 - For chat interface
    # ... other state variables

# Example: src/config/models.py
@dataclass
class AppSettings:
    """Application settings stored in config file and OS keychain."""
    # Paths
    zotero_data_path: Optional[str] = None
    
    # Embedding API Configuration (Epic 7.1)
    embedding_api_base_url: str = "https://api.openai.com/v1"
    embedding_model: str = "text-embedding-ada-002"
    
    # Chat API Configuration (Epic 7.1)
    chat_api_base_url: str = "https://api.openai.com/v1"
    chat_model: str = "gpt-4"
    
    # Chunking Configuration
    chunk_size: int = 600  # tokens
    chunk_overlap: int = 100  # tokens
    
    # Search Configuration
    default_search_results: int = 50
    
    # Feature Flags
    enable_ai_analysis: bool = False
    
    # UI Preferences
    theme: str = "light"  # light, dark, auto
    
    # Note: API keys are stored separately in OS keychain via keyring
```

### State Management Patterns
*   **Centralized State:** A single instance of `AppState` will be managed by the `MainWindow`.
*   **Observer Pattern (Signals & Slots):**
    1.  The `MainWindow` will own the state object.
    2.  When a background service (like `IndexingService`) updates the state, it will emit a signal with the new state.
    3.  The `MainWindow` will have a slot connected to this signal. When the slot receives the new state, it updates its `AppState` instance.
    4.  The `MainWindow` then passes the relevant parts of the state down to child widgets (the active tab), which then re-render themselves.

## Routing Architecture

"Routing" in this desktop application refers to switching between the initial onboarding view and the main tabbed interface.

### Route Organization
A `QStackedWidget` in the `MainWindow` will manage the top-level views (onboarding vs. main tabs). The main interface itself will be a `QTabWidget`.

```python
# Example: src/ui/main_window.py
from PySide6.QtWidgets import QMainWindow, QStackedWidget, QTabWidget
from .onboarding_view import OnboardingView
from .search_tab import SearchTab
from .index_tab import IndexTab
from .analysis_tab import AnalysisTab
from .settings_tab import SettingsTab
from ..config.settings_manager import SettingsManager

class MainWindow(QMainWindow):
    def __init__(self, settings_manager: SettingsManager):
        super().__init__()
        self.settings = settings_manager

        self.stacked_widget = QStackedWidget()
        self.onboarding_view = OnboardingView()
        self.main_tabs = QTabWidget()

        # Create and add tabs
        self.search_tab = SearchTab()
        self.index_tab = IndexTab()
        self.analysis_tab = AnalysisTab()
        self.settings_tab = SettingsTab()

        self.main_tabs.addTab(self.search_tab, "Search")
        self.main_tabs.addTab(self.index_tab, "Index")
        self.main_tabs.addTab(self.analysis_tab, "AI Analysis")
        self.main_tabs.addTab(self.settings_tab, "Settings")

        self.stacked_widget.addWidget(self.onboarding_view)
        self.stacked_widget.addWidget(self.main_tabs)

        self.setCentralWidget(self.stacked_widget)

        self.show_initial_view()

    def show_initial_view(self):
        # Logic to check if Zotero path is set
        if not self.settings.get_zotero_path():
            self.stacked_widget.setCurrentWidget(self.onboarding_view)
        else:
            self.stacked_widget.setCurrentWidget(self.main_tabs)
            # Default to the Search tab on launch (Epic 8.4)
            self.main_tabs.setCurrentWidget(self.search_tab)
            
            # Disable search tab until indexing is complete
            if not self.is_indexing_complete(): # is_indexing_complete is a placeholder
                self.search_tab.setEnabled(False)
                # Optionally, switch to Index tab if no index exists, but don't auto-switch after indexing
                if not self.search_tab.isEnabled():
                    self.main_tabs.setCurrentWidget(self.index_tab)

```

### "Protected Route" Pattern
This pattern translates to enabling/disabling UI elements based on application state. For example, the "Search" tab will be disabled until the initial indexing is complete. The "Analyze with AI" button will be disabled until a valid API key is entered. This is managed by simple conditional logic in the UI components.

## Frontend Services Layer

This layer is the bridge between the UI components and the core Python logic services.

### API Client Setup
UI components will not call services directly. Instead, the `MainWindow` will hold instances of the core services and expose methods for the UI to call. To keep the UI responsive, all long-running service calls will be executed in background threads using `QThreadPool`.

### Service Example
This example shows how the `SearchTab` can trigger a search, which the `MainWindow` then runs in a background thread.

```python
# In src/ui/main_window.py
from PySide6.QtCore import QRunnable, QThreadPool, Slot, Signal, QObject
from PySide6.QtWidgets import QMainWindow
from ..core.services.search_service import SearchService

# Worker for running a task in the background
class Worker(QRunnable):
    def __init__(self, fn, *args, **kwargs):
        super().__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

    @Slot()
    def run(self):
        try:
            result = self.fn(*self.args, **self.kwargs)
            self.signals.result.emit(result)
        except Exception as e:
            self.signals.error.emit(str(e))
        finally:
            self.signals.finished.emit()

class WorkerSignals(QObject):
    result = Signal(object)
    error = Signal(str)
    finished = Signal()

class MainWindow(QMainWindow):
    search_complete = Signal(list)
    # ... (previous __init__ content)

    def __init__(self, settings_manager: SettingsManager):
        super().__init__()
        # ... setup UI and tabs ...
        self.settings = settings_manager
        self.search_service = SearchService(
            # ... inject dependencies for SearchService
        )
        self.thread_pool = QThreadPool()

        # Connect search trigger from SearchTab to our handler
        self.search_tab.search_triggered.connect(self.on_search)
        # Connect our completion signal to a UI update slot
        self.search_complete.connect(self.update_search_results)

    @Slot(str, int)
    def on_search(self, query, count):
        # Disable UI elements, show loading indicator
        worker = Worker(self._execute_search, query, count)
        worker.signals.result.connect(self.search_complete.emit)
        worker.signals.error.connect(self.handle_search_error)
        worker.signals.finished.connect(self.search_finished)
        self.thread_pool.start(worker)

    def _execute_search(self, query, count):
        return self.search_service.search(query, k=count)

    @Slot(list)
    def update_search_results(self, results):
        # Update AppState and pass results to child widgets
        # Re-enable UI, hide loading indicator
        print(f"Search results received: {len(results)} items")
        self.search_tab.display_results(results) # Example method

    @Slot(str)
    def handle_search_error(self, error_message):
        print(f"Search error: {error_message}")
        # Display error to user
        pass

    @Slot()
    def search_finished(self):
        print("Search worker finished.")
        # Clean up, re-enable UI elements
        pass
```

## Accessibility Considerations

The application is committed to adhering to WCAG 2.1 AA standards, as specified in the PRD. PySide6 (Qt) provides a strong foundation for building accessible desktop applications.

*   **Native Accessibility Features:** Leverage Qt's built-in accessibility features, including keyboard navigation, focus management, and integration with platform-specific screen readers (e.g., NVDA on Windows, VoiceOver on macOS).
*   **Standard Widget Usage:** Prioritize the use of standard Qt widgets where possible, as they often come with inherent accessibility support.
*   **Custom Widget Accessibility:** For any custom widgets, ensure they provide appropriate accessible names, descriptions, and roles.
*   **Keyboard Navigation:** All interactive elements must be reachable and operable via keyboard. Provide clear visual focus indicators.
*   **Color Contrast:** Ensure sufficient color contrast ratios for all text and graphical elements to meet WCAG AA requirements.
*   **Screen Reader Testing:** Regularly test the application with common screen readers to identify and address accessibility barriers.
*   **Accessibility in Design:** Accessibility will be a consideration during the design and review phases of UI components, not an afterthought.
