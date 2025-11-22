# Frontend Architecture

## Component Architecture

The UI will be built using a composition of custom `QWidget` classes, each responsible for a specific part of the user interface.

### Component Organization
The UI components will be organized into Python modules based on their function:

```plaintext
src/
└── ui/
    ├── __init__.py
    ├── main_window.py          # The main application window with QTabWidget (Epic 6.1)
    ├── search_tab.py           # Search tab with search bar and results (Epic 6.1, 6.5)
    ├── index_tab.py            # Index management tab (Epic 6.1, 6.2)
    ├── ai_analysis_tab.py      # AI analysis tab (Epic 6.1)
    ├── settings_tab.py         # Settings tab (Epic 6.1)
    ├── paper_list_view.py      # Widget to display the list of source papers
    ├── chunk_list_view.py      # Widget to display the list of text chunks
    ├── chunk_detail_dialog.py  # Non-modal chunk detail dialog (Epic 6.4)
    ├── token_usage_widget.py   # Token usage display widget (Epic 6.6)
    ├── onboarding_view.py      # The initial setup/welcome screen
    └── widgets/                # Reusable custom widgets (e.g., progress bars)
        ├── __init__.py
        └── ...
```

### Component Template
Each major UI component will be a class inheriting from `QWidget` or a more specific Qt class. They will use signals to communicate events to parent widgets or controllers.

```python
# Example: src/ui/search_tab.py (Epic 6.1, 6.4, 6.5)
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QSpinBox, QLabel
from PySide6.QtCore import Signal
from .chunk_detail_dialog import ChunkDetailDialog

class SearchTab(QWidget):
    # Signal emitted when the user executes a search
    search_triggered = Signal(str, int)  # query, k_value

    def __init__(self, parent=None):
        super().__init__(parent)

        self.layout = QVBoxLayout(self)
        
        # Search controls grouped together (Epic 6.5)
        search_controls = QHBoxLayout()
        self.search_bar = QLineEdit()
        self.search_button = QPushButton("Search")
        self.k_label = QLabel("Results:")
        self.k_spinbox = QSpinBox()
        self.k_spinbox.setRange(1, 100)
        self.k_spinbox.setValue(50)
        
        search_controls.addWidget(self.search_bar)
        search_controls.addWidget(self.k_label)
        search_controls.addWidget(self.k_spinbox)
        search_controls.addWidget(self.search_button)
        
        self.layout.addLayout(search_controls)
        
        # Results list (Epic 6.4: double-click opens dialog)
        self.chunk_list = ChunkListView()
        self.chunk_list.itemDoubleClicked.connect(self._on_chunk_double_click)
        self.layout.addWidget(self.chunk_list)
        
        # Connect search button
        self.search_button.clicked.connect(self._on_search)
        
        # Non-modal dialog reference (Epic 6.4)
        self.chunk_detail_dialog = None

    def _on_search(self):
        query = self.search_bar.text()
        k = self.k_spinbox.value()
        if query:
            self.search_triggered.emit(query, k)
    
    def _on_chunk_double_click(self, item):
        # Epic 6.4: Launch non-modal chunk detail dialog
        chunk = item.data(Qt.UserRole)  # Assuming chunk stored as item data
        if not self.chunk_detail_dialog:
            self.chunk_detail_dialog = ChunkDetailDialog(self)
        self.chunk_detail_dialog.show_chunk(chunk, self.chunk_list.get_all_chunks())
        self.chunk_detail_dialog.show()

```

## State Management Architecture

We will use a centralized state object combined with PySide6's native signals and slots mechanism, which is an implementation of the Observer pattern.

### State Structure
A Python `dataclass` will hold the application's shared state.

```python
# Example: src/ui/state.py
from dataclasses import dataclass, field
from typing import Optional, List

@dataclass
class AppState:
    zotero_path: Optional[str] = None
    is_indexing: bool = False
    indexing_progress: float = 0.0
    search_results: List[dict] = field(default_factory=list)
    selected_paper: Optional[dict] = None
    collection_paper_counts: dict[int, int] = field(default_factory=dict)  # Epic 6.3
    token_usage_history: List[TokenUsage] = field(default_factory=list)  # Epic 6.6
    current_session_cost: float = 0.0  # Epic 6.6
    # ... other state variables

# Example: src/config/models.py
@dataclass
class AppSettings:
    """Application settings stored in config file and OS keychain."""
    # Paths
    zotero_data_path: Optional[str] = None
    
    # API Configuration
    api_base_url: str = "https://api.openai.com/v1"
    embedding_model: str = "text-embedding-ada-002"
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
    
    # Note: API key is stored separately in OS keychain via keyring
```

### State Management Patterns
*   **Centralized State:** A single instance of `AppState` will be managed by the `MainWindow`.
*   **Observer Pattern (Signals & Slots):**
    1.  The `MainWindow` will own the state object.
    2.  When a background service (like `IndexingService`) updates the state, it will emit a signal with the new state.
    3.  The `MainWindow` will have a slot connected to this signal. When the slot receives the new state, it updates its `AppState` instance.
    4.  The `MainWindow` then passes the relevant parts of the state down to child widgets (like `PaperListView` and `ChunkListView`), which then re-render themselves.

## Routing Architecture

"Routing" in this desktop application refers to switching between different views (e.g., onboarding vs. main search interface).

### Route Organization
A `QStackedWidget` in the `MainWindow` will be used to manage different full-screen views.

```python
# Example: src/ui/main_window.py
# ... imports
from PySide6.QtWidgets import QMainWindow, QStackedWidget
from .onboarding_view import OnboardingView
from .search_view import SearchView
from ..config.settings_manager import SettingsManager # Assuming SettingsManager is accessible

class MainWindow(QMainWindow):
    def __init__(self, settings_manager: SettingsManager):
        super().__init__()
        self.settings = settings_manager # Inject settings manager

        self.stacked_widget = QStackedWidget()
        self.onboarding_view = OnboardingView()
        self.search_view = SearchView()

        self.stacked_widget.addWidget(self.onboarding_view)
        self.stacked_widget.addWidget(self.search_view)

        self.setCentralWidget(self.stacked_widget)

        self.show_onboarding_if_needed()

    def show_onboarding_if_needed(self):
        # Logic to check if Zotero path is set
        if not self.settings.get_zotero_path(): # Assuming get_zotero_path() exists
            self.stacked_widget.setCurrentWidget(self.onboarding_view)
        else:
            self.stacked_widget.setCurrentWidget(self.search_view)
```

### "Protected Route" Pattern
This pattern translates to enabling/disabling UI elements based on application state. For example, the "Analyze with AI" button will be disabled until a valid API key is entered in the settings. This is managed by simple conditional logic in the UI components.

## Frontend Services Layer

This layer is the bridge between the UI components and the core Python logic services.

### API Client Setup
UI components will not call services directly. Instead, the `MainWindow` will hold instances of the core services and expose methods for the UI to call. To keep the UI responsive, all long-running service calls will be executed in background threads using `QThreadPool`.

### Service Example
This example shows how the `SearchView` can trigger a search, which the `MainWindow` then runs in a background thread.

```python
# In src/ui/main_window.py
from PySide6.QtCore import QRunnable, QThreadPool, Slot, Signal
from PySide6.QtWidgets import QMainWindow, QStackedWidget # ... other imports
from ..core.services.search_service import SearchService # Assuming SearchService is available

# Worker for running a task in the background
class Worker(QRunnable):
    def __init__(self, fn, *args, **kwargs):
        super().__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals() # Custom signals for worker

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
    # ... (previous __init__ content)

    def __init__(self, settings_manager: SettingsManager):
        super().__init__()
        self.settings = settings_manager
        self.search_service = SearchService(
            # ... inject dependencies for SearchService
            None, None, None, None # Placeholder for now
        )
        self.thread_pool = QThreadPool()

        # Connect search trigger from SearchView to our handler
        self.search_view.search_triggered.connect(self.on_search)
        # Connect our completion signal to a UI update slot
        self.search_complete.connect(self.update_search_results)

    @Slot(str)
    def on_search(self, query):
        # Disable UI elements, show loading indicator
        worker = Worker(self._execute_search, query)
        worker.signals.result.connect(self.search_complete.emit)
        worker.signals.error.connect(self.handle_search_error) # Connect error signal
        worker.signals.finished.connect(self.search_finished) # Connect finished signal
        self.thread_pool.start(worker)

    def _execute_search(self, query):
        return self.search_service.search(query)

    @Slot(list)
    def update_search_results(self, results):
        # Update AppState and pass results to child widgets
        # Re-enable UI, hide loading indicator
        print(f"Search results received: {len(results)} items")
        pass

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
