# ZoteroRAG Desktop: UX Enhancements Specification

**Version:** 1.0  
**Date:** November 22, 2025  
**Author:** UX Expert (Sally)  
**Status:** Approved - Ready for PRD Creation

---

## Executive Summary

Following completion of all 5 epics and comprehensive manual testing, 6 critical UX issues have been identified that significantly impact usability, especially on low-resolution screens. This specification document provides detailed solutions for each issue, implementation guidance, and success metrics.

**Total Estimated Effort:** 9.5-13.5 hours across 2 sprints  
**Priority Breakdown:** 3 P0 (Critical), 2 P1 (High), 1 P2 (Medium)  
**Risk Level:** Low - Minimal breaking changes, well-understood problems

---

## Problem Statement

### Current State

The ZoteroRAG Desktop application is functionally complete with all 5 epics delivered and 60 tests passing. However, manual testing revealed significant usability challenges:

### Identified Issues

**Issue 1: Cramped Single-View Layout**
- **Problem:** All 12 UI components stacked vertically in single scrollable view
- **Evidence:** `main_window.py` lines 130-142 show all widgets added to single QVBoxLayout
- **Impact:** Requires extensive scrolling, especially difficult on screens with resolution ≤1366x768
- **User Quote:** "all content are packed in the same view, which makes it difficult to view, especially for screen with low resolution"

**Issue 2: No Indexing Cancellation**
- **Problem:** Once indexing starts, no way to stop the operation
- **Evidence:** `main_window.py` lines 258-265 show worker starts with no cancel mechanism, button becomes disabled
- **Impact:** Users with large libraries forced to wait or force-quit application
- **User Quote:** "there seems no way to stop indexing, it would be helpful if the user can stop indexing if they accidently start index entire library"

**Issue 3: Missing Collection Paper Counts**
- **Problem:** Collection dropdown shows only names, no indication of size
- **Evidence:** `indexing_scope_view.py` lines 55-57 display only `collection.name`
- **Impact:** Users cannot estimate indexing time or make informed decisions
- **User Quote:** "it would be good to show the number of papers in specific collection so user have a better idea if they want to index collection"

**Issue 4: Poor Chunk Readability**
- **Problem:** Search result chunks displayed in single-line format with only 120 character preview
- **Evidence:** `chunk_list_view.py` line 35: `preview = match.chunk.content[:120].replace("\n", " ")`
- **Impact:** Cannot evaluate chunk relevance without opening PDF, missing context
- **User Quote:** "it would be better to have a better view to see the chunk returned from the search, right now every chunk is shown in the single line which make it difficult to view"

**Issue 5: Chunk Count Selector Placement**
- **Problem:** QSpinBox for chunk count located at bottom of layout, far from search controls
- **Evidence:** `main_window.py` line 139 (chunk count) far from line 131 (search view)
- **Impact:** Not obvious what the control affects, poor discoverability
- **User Quote:** "the choice of number of chunks should be put closer to the search button so the user can adjust when search"

**Issue 6: No API Token Usage Transparency**
- **Problem:** No visibility into OpenAI API token consumption or estimated costs
- **Evidence:** No usage tracking in `AppState`, `EmbeddingClient`, or `AIService`
- **Impact:** Users cannot manage API budget, builds mistrust
- **User Quote:** "it would be good to provide some information about token used for api service to improve the transparency"

---

## Proposed Solutions

### Enhancement 1: Tab-Based Interface (Priority: P0)

**Goal:** Reorganize UI into focused, task-oriented tabs to reduce scrolling and improve space utilization

**Solution Overview:**
Replace the single vertical layout with a QTabWidget containing 4 tabs:
1. **Search Tab:** Search interface, results (papers and chunks), AI analysis trigger
2. **Index Tab:** Indexing scope selection and progress
3. **AI Analysis Tab:** Full AI analysis results with token usage tracking
4. **Settings Tab:** Application settings (future extensibility)

**Technical Implementation:**

```python
# In MainWindow.__init__
self._tab_widget = QTabWidget()
self.setCentralWidget(self._tab_widget)

# Search Tab
search_tab = QWidget()
search_layout = QVBoxLayout(search_tab)
search_layout.addWidget(self._search_view)
search_layout.addWidget(QLabel("Search Results:"))
search_layout.addWidget(self._paper_list_view)
search_layout.addWidget(QLabel("Matching Chunks:"))
search_layout.addWidget(self._chunk_list_view)
search_layout.addWidget(self._analyze_button)
self._tab_widget.addTab(search_tab, "Search")

# Index Tab
index_tab = QWidget()
index_layout = QVBoxLayout(index_tab)
index_layout.addWidget(QLabel("Zotero Library:"))
index_layout.addWidget(self._library_view)
index_layout.addWidget(self._indexing_scope_view)
index_layout.addStretch()
self._tab_widget.addTab(index_tab, "Index")

# AI Analysis Tab
ai_tab = QWidget()
ai_layout = QVBoxLayout(ai_tab)
ai_layout.addWidget(QLabel("AI Analysis Results:"))
ai_layout.addWidget(self._analysis_label)
ai_layout.addWidget(self._token_usage_widget)  # New widget for Enhancement 6
ai_layout.addStretch()
self._tab_widget.addTab(ai_tab, "AI Analysis")

# Settings Tab (placeholder)
settings_tab = QWidget()
self._tab_widget.addTab(settings_tab, "Settings")
```

**User Experience Enhancements:**
- **Automatic Navigation:** After indexing completes, automatically switch to Search tab
- **Tab Badges:** Show unread count on AI Analysis tab when new results available
- **Disabled States:** Disable Search tab until library is indexed
- **Tooltips:** Clear tooltips on each tab explaining their purpose

**Success Metrics:**
- Reduce required scrolling by ~80% on 1366x768 screens
- All primary workflows accessible within single screen view
- User testing shows 90%+ can navigate without guidance

**Estimated Effort:** 3-4 hours

---

### Enhancement 2: Indexing Cancellation (Priority: P0)

**Goal:** Allow users to safely cancel long-running indexing operations

**Solution Overview:**
Add cancellation capability to IndexingService with safe worker interrupt mechanism

**Technical Implementation:**

```python
# In IndexingService
class IndexingService:
    def __init__(self, ...):
        self._cancel_requested = False
    
    def cancel_indexing(self) -> None:
        """Request cancellation of current indexing operation."""
        self._cancel_requested = True
    
    def index_entire_library(self, progress_callback=None) -> None:
        self._cancel_requested = False
        papers = self._zotero_manager.get_all_papers()
        
        for i, paper in enumerate(papers):
            if self._cancel_requested:
                logger.info(f"Indexing cancelled by user at {i}/{len(papers)}")
                break
            # ... process paper ...
            if progress_callback:
                progress_callback(i + 1, len(papers))

# In IndexingScopeView
def __init__(self, ...):
    self._start_button = QPushButton("Start Indexing")
    self._start_button.clicked.connect(self._on_start_clicked)

def _on_start_clicked(self) -> None:
    if self._busy:
        # Cancel mode
        self.cancel_requested.emit()
    else:
        # Start mode
        scope = self._get_selected_scope()
        self.start_requested.emit(scope)

def set_busy(self, busy: bool) -> None:
    self._busy = busy
    if busy:
        self._start_button.setText("Cancel Indexing")
        self._start_button.setStyleSheet("QPushButton { background-color: #ff6b6b; }")
    else:
        self._start_button.setText("Start Indexing")
        self._start_button.setStyleSheet("")
    self._entire_radio.setEnabled(not busy)
    self._update_collection_controls()

# In MainWindow
def _start_indexing_task(self, scope: dict) -> None:
    worker = _IndexingRunnable(self._indexing_service, scope)
    worker.signals.progress.connect(self._handle_indexing_progress)
    worker.signals.finished.connect(self._on_indexing_finished)
    self._indexing_scope_view.cancel_requested.connect(
        lambda: self._indexing_service.cancel_indexing()
    )
    self._indexing_scope_view.set_busy(True)
    self._thread_pool.start(worker)

def _on_indexing_finished(self) -> None:
    self._indexing_scope_view.set_busy(False)
    # Disconnect cancel signal
    self._indexing_scope_view.cancel_requested.disconnect()
```

**User Experience:**
- Button transforms to "Cancel Indexing" with red background when indexing starts
- Progress bar continues to show current progress
- Status message: "Cancelling indexing..." appears immediately
- Partial index remains usable (indexed papers are retained)
- After cancellation, button returns to "Start Indexing"

**Success Metrics:**
- Users can cancel within 2 seconds of clicking cancel
- Partial indexes are valid and searchable
- No crashes or data corruption from cancellation

**Estimated Effort:** 1-2 hours

---

### Enhancement 3: Collection Paper Counts (Priority: P1)

**Goal:** Display the number of papers in each collection to aid decision-making

**Solution Overview:**
Query paper counts from database and display in collection dropdown

**Technical Implementation:**

```python
# In Collection dataclass (data/models.py)
@dataclass
class Collection:
    id: int
    name: str
    zotero_collection_key: str
    item_count: int = 0  # New field

# In ZoteroManager
def get_collections_with_counts(self) -> list[Collection]:
    """Get all collections with paper counts."""
    query = """
        SELECT 
            c.collectionID,
            c.collectionName,
            c.key,
            COUNT(ci.itemID) as item_count
        FROM collections c
        LEFT JOIN collectionItems ci ON c.collectionID = ci.collectionID
        LEFT JOIN items i ON ci.itemID = i.itemID
        WHERE i.itemTypeID = 2  -- 2 is typically 'document'
        GROUP BY c.collectionID
        ORDER BY c.collectionName
    """
    result = self._db.execute(query)
    return [
        Collection(
            id=row[0],
            name=row[1],
            zotero_collection_key=row[2],
            item_count=row[3]
        )
        for row in result
    ]

# In IndexingScopeView
def set_collections(self, collections: list[Collection]) -> None:
    self._collections = collections
    self._collection_combo.clear()
    
    for collection in collections:
        label = f"{collection.name} ({collection.item_count} papers)"
        self._collection_combo.addItem(label, userData=collection)
    
    self._update_collection_controls()

# Update "Entire Library" radio button label
def _update_entire_library_label(self) -> None:
    total_papers = self._zotero_manager.get_total_paper_count()
    self._entire_radio.setText(f"Entire Library ({total_papers} papers)")
```

**User Experience:**
- Collection dropdown shows: "Collection Name (47 papers)"
- "Entire Library" radio shows: "Entire Library (1,234 papers)"
- Counts update when library changes
- Empty collections show "(0 papers)" with gray text

**Success Metrics:**
- Users can quickly identify large vs small collections
- Reduces accidental indexing of entire library
- Improves decision-making for scope selection

**Estimated Effort:** 1 hour

---

### Enhancement 4: Non-Modal Chunk Detail Dialog (Priority: P0)

**Goal:** Provide full, readable view of chunk content with context and metadata

**Solution Overview:**
Create a non-modal dialog that opens on double-click, showing full chunk content with navigation and actions

**Technical Implementation:**

```python
# New file: ui/chunk_detail_dialog.py
class ChunkDetailDialog(QDialog):
    """Non-modal dialog for displaying full chunk details."""
    
    def __init__(self, chunks: list[tuple[Chunk, Document]], initial_index: int, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Chunk Details")
        self.setModal(False)  # Non-modal allows interaction with main window
        self.resize(800, 600)
        
        self._chunks = chunks
        self._current_index = initial_index
        
        layout = QVBoxLayout(self)
        
        # Header with metadata
        self._header_label = QLabel()
        self._header_label.setStyleSheet("font-weight: bold; font-size: 12pt;")
        layout.addWidget(self._header_label)
        
        self._metadata_label = QLabel()
        self._metadata_label.setStyleSheet("color: #666; font-size: 10pt;")
        layout.addWidget(self._metadata_label)
        
        # Full chunk content (scrollable)
        self._content_text = QTextEdit()
        self._content_text.setReadOnly(True)
        self._content_text.setLineWrapMode(QTextEdit.WidgetWidth)
        layout.addWidget(self._content_text)
        
        # Navigation and action buttons
        button_layout = QHBoxLayout()
        
        self._prev_button = QPushButton("← Previous (←)")
        self._prev_button.clicked.connect(self._show_previous)
        button_layout.addWidget(self._prev_button)
        
        self._next_button = QPushButton("Next (→) →")
        self._next_button.clicked.connect(self._show_next)
        button_layout.addWidget(self._next_button)
        
        button_layout.addStretch()
        
        self._copy_button = QPushButton("Copy Text (Ctrl+C)")
        self._copy_button.clicked.connect(self._copy_content)
        button_layout.addWidget(self._copy_button)
        
        self._open_pdf_button = QPushButton("Open PDF")
        self._open_pdf_button.clicked.connect(self._open_pdf)
        button_layout.addWidget(self._open_pdf_button)
        
        close_button = QPushButton("Close (Esc)")
        close_button.clicked.connect(self.close)
        button_layout.addWidget(close_button)
        
        layout.addLayout(button_layout)
        
        # Position label
        self._position_label = QLabel()
        self._position_label.setAlignment(Qt.AlignCenter)
        self._position_label.setStyleSheet("color: #999; font-size: 9pt;")
        layout.addWidget(self._position_label)
        
        self._update_display()
    
    def keyPressEvent(self, event):
        """Handle keyboard shortcuts."""
        if event.key() == Qt.Key_Left:
            self._show_previous()
        elif event.key() == Qt.Key_Right:
            self._show_next()
        elif event.key() == Qt.Key_Escape:
            self.close()
        elif event.modifiers() == Qt.ControlModifier and event.key() == Qt.Key_C:
            self._copy_content()
        else:
            super().keyPressEvent(event)
    
    def _update_display(self):
        chunk, doc = self._chunks[self._current_index]
        
        # Header
        title = doc.title if doc else "Unknown Document"
        self._header_label.setText(title)
        
        # Metadata
        metadata_parts = []
        if hasattr(chunk, 'page_number') and chunk.page_number:
            metadata_parts.append(f"Page {chunk.page_number}")
        if hasattr(chunk, 'score'):
            metadata_parts.append(f"Relevance: {chunk.score:.2%}")
        metadata_parts.append(f"Length: {len(chunk.content)} characters")
        self._metadata_label.setText(" • ".join(metadata_parts))
        
        # Full content
        self._content_text.setPlainText(chunk.content)
        
        # Navigation buttons
        self._prev_button.setEnabled(self._current_index > 0)
        self._next_button.setEnabled(self._current_index < len(self._chunks) - 1)
        
        # Position
        self._position_label.setText(
            f"Chunk {self._current_index + 1} of {len(self._chunks)}"
        )
    
    def _show_previous(self):
        if self._current_index > 0:
            self._current_index -= 1
            self._update_display()
    
    def _show_next(self):
        if self._current_index < len(self._chunks) - 1:
            self._current_index += 1
            self._update_display()
    
    def _copy_content(self):
        chunk, _ = self._chunks[self._current_index]
        QApplication.clipboard().setText(chunk.content)
    
    def _open_pdf(self):
        chunk, doc = self._chunks[self._current_index]
        if doc and doc.pdf_path:
            # Emit signal or call method to open PDF
            pass

# In ChunkListView - update display and add handler
def update_matches(self, matches: list[SearchMatch]) -> None:
    self._list.clear()
    self._matches = matches
    
    for match in matches:
        doc = match.document
        
        # Enhanced preview: 2-3 lines instead of 1
        preview = match.chunk.content[:200].replace("\n", " ")
        if len(match.chunk.content) > 200:
            preview += "..."
        
        title = doc.title if doc else "Unknown document"
        
        # Show score if available
        score_text = f"({match.score:.0%})" if hasattr(match, 'score') else ""
        
        item_text = f"{score_text} {title}\n{preview}"
        
        item = QListWidgetItem(item_text)
        item.setData(Qt.UserRole, (match.chunk, doc))
        self._list.addItem(item)
    
    # Add double-click handler
    self._list.itemDoubleClicked.connect(self._on_item_double_clicked)

def _on_item_double_clicked(self, item: QListWidgetItem) -> None:
    """Open chunk detail dialog on double-click."""
    clicked_index = self._list.row(item)
    
    # Prepare all chunks for navigation
    chunks = [(match.chunk, match.document) for match in self._matches]
    
    # Create and show non-modal dialog
    dialog = ChunkDetailDialog(chunks, clicked_index, self)
    dialog.show()
    dialog.raise_()
    dialog.activateWindow()
```

**User Experience:**
- List items show 2-3 lines of preview (200 chars) with relevance score
- Double-click opens non-modal dialog with full content
- Dialog shows document title, page number, relevance score, character count
- Previous/Next buttons navigate between chunks without closing dialog
- Keyboard shortcuts: ←/→ for navigation, Esc to close, Ctrl+C to copy
- Non-modal allows referencing main window while reading chunks
- Visual affordance: "(Double-click for full text)" hint in status bar when hovering

**Success Metrics:**
- 1600% increase in visible text (120 → 2000+ characters)
- Users can read full context without opening PDF
- Navigation between chunks takes <1 second
- 90%+ of users discover double-click functionality within first use

**Estimated Effort:** 2-3 hours

---

### Enhancement 5: Reposition Chunk Count Selector (Priority: P2)

**Goal:** Move chunk count control closer to search button for better discoverability

**Solution Overview:**
Move QSpinBox from bottom of layout to SearchView next to search button

**Technical Implementation:**

```python
# In SearchView
def __init__(self, parent=None):
    super().__init__(parent)
    
    layout = QVBoxLayout(self)
    
    # Search input row
    input_layout = QHBoxLayout()
    
    self._search_input = QLineEdit()
    self._search_input.setPlaceholderText("Ask a question about your research...")
    input_layout.addWidget(self._search_input, stretch=1)
    
    # Add chunk count selector HERE
    chunk_layout = QHBoxLayout()
    chunk_layout.addWidget(QLabel("Results:"))
    self._chunk_count = QSpinBox()
    self._chunk_count.setRange(1, 20)
    self._chunk_count.setValue(5)
    self._chunk_count.setToolTip("Number of chunks to retrieve")
    chunk_layout.addWidget(self._chunk_count)
    input_layout.addLayout(chunk_layout)
    
    self._search_button = QPushButton("Search")
    input_layout.addWidget(self._search_button)
    
    layout.addLayout(input_layout)
    
    # ... rest of SearchView layout ...

def get_chunk_count(self) -> int:
    """Get the selected chunk count."""
    return self._chunk_count.value()

# In MainWindow - remove chunk count from main layout
# Update search handler to get count from SearchView
def _perform_search(self) -> None:
    query = self._search_view.get_query()
    chunk_count = self._search_view.get_chunk_count()  # Get from SearchView
    # ... rest of search logic ...
```

**User Experience:**
- Chunk count selector appears on same row as search input
- Label "Results:" clarifies purpose
- Tooltip explains: "Number of chunks to retrieve"
- Visually grouped with search controls
- Default value: 5 chunks

**Success Metrics:**
- Users understand control purpose without guidance
- Discoverability increases from ~30% to 90%
- Adjustment rate increases (users actively changing value)

**Estimated Effort:** 30 minutes

---

### Enhancement 6: API Token Usage Transparency (Priority: P1)

**Goal:** Provide visibility into OpenAI API token consumption and estimated costs

**Solution Overview:**
Implement token usage tracking with display widget showing consumption metrics

**Technical Implementation:**

```python
# New dataclass in data/models.py
@dataclass
class TokenUsage:
    timestamp: datetime
    operation: str  # 'embedding', 'ai_analysis'
    model: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    estimated_cost_usd: float

# In AppState
class AppState:
    def __init__(self):
        # ... existing fields ...
        self.token_usage_history: list[TokenUsage] = []
        self.token_usage_updated = Signal(TokenUsage)  # New signal
    
    def record_token_usage(self, usage: TokenUsage) -> None:
        self.token_usage_history.append(usage)
        self.token_usage_updated.emit(usage)
    
    def get_total_tokens(self) -> int:
        return sum(u.total_tokens for u in self.token_usage_history)
    
    def get_total_cost(self) -> float:
        return sum(u.estimated_cost_usd for u in self.token_usage_history)
    
    def get_session_summary(self) -> dict:
        return {
            'total_tokens': self.get_total_tokens(),
            'total_cost': self.get_total_cost(),
            'embedding_calls': len([u for u in self.token_usage_history if u.operation == 'embedding']),
            'ai_analysis_calls': len([u for u in self.token_usage_history if u.operation == 'ai_analysis'])
        }

# In EmbeddingClient
def get_embeddings(self, texts: list[str]) -> list[list[float]]:
    response = self._client.embeddings.create(
        model=self._model,
        input=texts
    )
    
    # Record usage
    usage = TokenUsage(
        timestamp=datetime.now(),
        operation='embedding',
        model=self._model,
        prompt_tokens=response.usage.prompt_tokens,
        completion_tokens=0,
        total_tokens=response.usage.total_tokens,
        estimated_cost_usd=self._calculate_cost(response.usage.total_tokens, 'embedding')
    )
    self.usage_recorded.emit(usage)  # New signal
    
    return [data.embedding for data in response.data]

def _calculate_cost(self, tokens: int, operation: str) -> float:
    # Pricing as of Nov 2025 (approximate)
    if operation == 'embedding':
        # text-embedding-3-small: $0.02 / 1M tokens
        return (tokens / 1_000_000) * 0.02
    elif operation == 'ai_analysis':
        # GPT-4: ~$0.03/1K input + $0.06/1K output (simplified average)
        return (tokens / 1_000) * 0.045
    return 0.0

# New widget: ui/token_usage_widget.py
class TokenUsageWidget(QWidget):
    """Widget displaying API token usage and costs."""
    
    def __init__(self, state: AppState, parent=None):
        super().__init__(parent)
        self._state = state
        
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("API Usage Tracking")
        title.setStyleSheet("font-weight: bold; font-size: 11pt;")
        layout.addWidget(title)
        
        # Disclaimer
        disclaimer = QLabel(
            "Note: Token counts and costs are approximate estimates. "
            "Check your OpenAI dashboard for exact billing."
        )
        disclaimer.setStyleSheet("color: #666; font-size: 9pt; font-style: italic;")
        disclaimer.setWordWrap(True)
        layout.addWidget(disclaimer)
        
        # Metrics grid
        metrics_layout = QGridLayout()
        
        metrics_layout.addWidget(QLabel("Session Total:"), 0, 0)
        self._total_tokens_label = QLabel("0 tokens")
        metrics_layout.addWidget(self._total_tokens_label, 0, 1)
        
        metrics_layout.addWidget(QLabel("Estimated Cost:"), 1, 0)
        self._total_cost_label = QLabel("$0.00")
        self._total_cost_label.setStyleSheet("font-weight: bold; color: #2ecc71;")
        metrics_layout.addWidget(self._total_cost_label, 1, 1)
        
        metrics_layout.addWidget(QLabel("Embedding Calls:"), 2, 0)
        self._embedding_calls_label = QLabel("0")
        metrics_layout.addWidget(self._embedding_calls_label, 2, 1)
        
        metrics_layout.addWidget(QLabel("AI Analysis Calls:"), 3, 0)
        self._ai_calls_label = QLabel("0")
        metrics_layout.addWidget(self._ai_calls_label, 3, 1)
        
        layout.addLayout(metrics_layout)
        
        # Details button
        details_button = QPushButton("View Detailed History")
        details_button.clicked.connect(self._show_details)
        layout.addWidget(details_button)
        
        layout.addStretch()
        
        # Connect to state updates
        self._state.token_usage_updated.connect(self._update_display)
        
        self._update_display()
    
    def _update_display(self):
        summary = self._state.get_session_summary()
        
        self._total_tokens_label.setText(f"{summary['total_tokens']:,} tokens")
        self._total_cost_label.setText(f"${summary['total_cost']:.4f}")
        self._embedding_calls_label.setText(str(summary['embedding_calls']))
        self._ai_calls_label.setText(str(summary['ai_analysis_calls']))
        
        # Color code cost
        cost = summary['total_cost']
        if cost < 0.10:
            color = "#2ecc71"  # Green
        elif cost < 0.50:
            color = "#f39c12"  # Orange
        else:
            color = "#e74c3c"  # Red
        self._total_cost_label.setStyleSheet(f"font-weight: bold; color: {color};")
    
    def _show_details(self):
        # Open dialog with detailed usage history table
        pass

# In MainWindow - add status bar counter
def __init__(self):
    # ... existing init ...
    
    # Status bar token counter
    self._token_counter_label = QLabel("API Usage: $0.00")
    self._token_counter_label.setToolTip("Click to view details")
    self._token_counter_label.mousePressEvent = lambda e: self._show_token_details()
    self.statusBar().addPermanentWidget(self._token_counter_label)
    
    # Connect to state
    self._state.token_usage_updated.connect(self._update_status_bar_usage)

def _update_status_bar_usage(self, usage: TokenUsage):
    total_cost = self._state.get_total_cost()
    self._token_counter_label.setText(f"API Usage: ${total_cost:.4f}")
```

**User Experience:**
- Status bar shows: "API Usage: $0.00" (updates in real-time)
- AI Analysis tab contains full TokenUsageWidget with breakdown
- Widget shows:
  - Total tokens consumed this session
  - Estimated cost in USD
  - Number of embedding calls
  - Number of AI analysis calls
- "View Detailed History" button opens table with:
  - Timestamp
  - Operation type
  - Model used
  - Token counts
  - Cost per operation
- Clear disclaimer about approximate nature
- Color-coded cost indicator (green < $0.10, orange < $0.50, red ≥ $0.50)

**Success Metrics:**
- Users aware of API costs before heavy usage
- Reduced surprise billing complaints
- Increased user trust through transparency
- Users can make informed decisions about usage

**Estimated Effort:** 2-3 hours

---

## Implementation Plan

### Phase 1: Critical UX Improvements (Sprint 1)

**Priority:** P0 enhancements that directly impact core usability

**Stories:**
1. **Story 6.1:** Implement tab-based interface (3-4 hours)
2. **Story 6.2:** Add indexing cancellation (1-2 hours)
3. **Story 6.4:** Implement non-modal chunk detail dialog (2-3 hours)

**Total Effort:** 6-9 hours  
**Sprint Goal:** Solve the 3 most critical UX pain points (cramped layout, no control, poor readability)

**Testing Focus:**
- Test on various screen resolutions (1366x768, 1280x720, 1024x768)
- Verify tab navigation flows smoothly
- Test cancellation at various stages of indexing
- Verify chunk dialog navigation and keyboard shortcuts
- Ensure no regressions in existing 60 tests

### Phase 2: Polish & Transparency (Sprint 2)

**Priority:** P1-P2 enhancements that improve usability and build trust

**Stories:**
4. **Story 6.3:** Show collection paper counts (1 hour)
5. **Story 6.6:** Add API token usage transparency (2-3 hours)
6. **Story 6.5:** Reposition chunk count selector (30 minutes)

**Total Effort:** 3.5-4.5 hours  
**Sprint Goal:** Add metadata visibility and polish user experience

**Testing Focus:**
- Verify collection count accuracy
- Test token tracking for all operations
- Verify cost calculations are reasonable
- Test chunk count selector in new position
- Full regression testing

### Overall Timeline

**Total Estimated Effort:** 9.5-13.5 hours (approximately 2 work days)  
**Recommended Approach:** 2 sprints of ~1 week each with testing between phases

---

## Success Metrics

### Quantitative Metrics

**Issue 1 - Layout:**
- Reduce required scrolling by 80% on 1366x768 screens
- Increase screen real estate utilization from ~40% to ~85%
- All primary workflows accessible within single screen view

**Issue 2 - Cancellation:**
- Cancel response time < 2 seconds
- 100% of long operations cancellable
- Zero data corruption from cancellations

**Issue 3 - Collection Counts:**
- 100% of collections show accurate paper counts
- Reduce accidental full library indexing by 60%

**Issue 4 - Chunk Readability:**
- Increase visible text from 120 to 2000+ characters (1600% increase)
- Reduce PDF opens by 50% (users can evaluate chunks without opening)
- Double-click discovery rate > 90% within first session

**Issue 5 - Chunk Count Placement:**
- Increase discoverability from ~30% to 90%
- Increase adjustment rate by 3x (users actively changing value)

**Issue 6 - Token Transparency:**
- 100% of API operations tracked
- Cost estimation accuracy within ±20% of actual billing
- User awareness of costs increases to 100%

### Qualitative Metrics

- User testing shows improved confidence navigating application
- Reduced support requests about "can't find" or "how to stop"
- Positive user feedback on transparency and control
- No increase in bug reports or regressions

---

## Technical Considerations

### Architecture Impact

**Low Risk Changes:**
- Tab interface is additive (existing layout replaced but components unchanged)
- Cancellation adds flag checking (existing logic preserved)
- Token tracking is observational (doesn't affect core functionality)
- Chunk dialog is separate window (existing list unchanged)

**Medium Risk Changes:**
- Collection counts require new database query (test SQL carefully)
- Moving chunk count selector requires wiring changes (verify all connections)

**No Breaking Changes:**
- All existing APIs remain unchanged
- No changes to data models (except additions)
- No changes to file formats or storage

### Performance Considerations

- **Tab switching:** Instant (widgets already created)
- **Collection count query:** ~10-50ms for typical libraries (<1000 collections)
- **Token tracking:** Negligible overhead (~1ms per operation)
- **Chunk dialog:** Renders on demand, no preloading required
- **Cancel checking:** Adds ~1ms per indexed paper (negligible)

### Testing Strategy

**Unit Tests:**
- Test cancellation flag logic
- Test token cost calculations
- Test collection count query accuracy
- Test chunk dialog navigation logic

**Integration Tests:**
- Test tab navigation flows
- Test cancellation during actual indexing
- Test token tracking across services
- Test chunk dialog with real search results

**Manual Testing:**
- Test on multiple screen resolutions
- Test keyboard shortcuts in chunk dialog
- Test cancellation at various stages
- Verify cost estimates match OpenAI billing
- Test with large libraries (>1000 papers)

**Regression Testing:**
- Ensure all 60 existing tests still pass
- Verify no performance degradation
- Verify no new memory leaks
- Verify all existing functionality intact

---

## Risks & Mitigation

### Risk 1: Tab Interface Confuses Users

**Probability:** Low  
**Impact:** Medium  
**Mitigation:**
- Add clear tooltips on each tab
- Implement automatic navigation (after indexing → Search tab)
- Add visual indicators (badges, disabled states)
- Include onboarding hints in first-run experience
- User testing before final release

### Risk 2: Non-Modal Dialog Feels Disconnected

**Probability:** Low  
**Impact:** Low  
**Mitigation:**
- Use clear window title: "Chunk Details - [Document Title]"
- Position dialog next to main window
- Use same color scheme and styling
- Add "Stay on Top" option if users request it
- Ensure ESC key always closes dialog

### Risk 3: Token Cost Estimates Inaccurate

**Probability:** Medium  
**Impact:** Medium  
**Mitigation:**
- Add prominent disclaimer: "Approximate estimates only"
- Update pricing constants when OpenAI changes rates
- Recommend checking OpenAI dashboard for exact billing
- Label as "Estimated Cost" not "Actual Cost"
- Consider adding link to OpenAI usage dashboard

### Risk 4: Cancellation Leaves Partial State

**Probability:** Low  
**Impact:** Low  
**Mitigation:**
- Complete processing of current paper before stopping
- Ensure partial index is valid and searchable
- Add status message: "Indexing cancelled - N papers indexed"
- Test cancellation at various stages thoroughly
- Keep transaction boundaries intact

---

## Conclusion

These 6 enhancements address real-world usability issues discovered through manual testing of the completed application. All solutions are technically feasible, low-risk, and provide measurable improvements to user experience.

**Key Benefits:**
- Dramatically improved usability on low-resolution screens (80% less scrolling)
- Full user control over long operations (100% cancellable)
- 1600% increase in chunk text visibility
- Complete API cost transparency
- Better informed decision-making through metadata visibility

**Implementation Approach:**
- 2 focused sprints (approximately 2 work days total effort)
- Minimal breaking changes (all existing functionality preserved)
- Comprehensive testing strategy (unit, integration, manual, regression)
- Low-risk, high-value improvements

**Next Steps:**
1. Create formal PRD from this specification
2. Break down into detailed user stories with acceptance criteria
3. Create UI mockups/wireframes for tab layout and chunk dialog
4. Begin Phase 1 implementation (Stories 6.1, 6.2, 6.4)
5. Conduct user testing after Phase 1
6. Complete Phase 2 based on Phase 1 feedback
7. Final QA and release

---

**Document Status:** Approved by user - Ready for PRD creation  
**Approved Solutions:**
- ✅ Tab-based interface (4 tabs: Search, Index, AI Analysis, Settings)
- ✅ Cancellation mechanism with safe worker interrupt
- ✅ Collection paper counts with SQL GROUP BY query
- ✅ Non-modal chunk detail dialog with navigation (Option 4A.2)
- ✅ Chunk count selector repositioning to search bar
- ✅ API token usage tracking with transparency widget

**For PRD Creation:**
This document provides complete technical specifications and user experience details. The PRD should include:
- User stories with Given-When-Then acceptance criteria
- UI mockups for tab layout and chunk dialog
- API contracts for new methods
- Test plans with specific test cases
- Definition of Done for each story
