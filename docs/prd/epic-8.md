# Epic 8: Indexing & Search UX Improvements

## Epic Goal
Improve visibility of indexing status and optimize post-indexing workflow by adding real-time status tracking, indexing summaries, and better default navigation.

## Epic Priority
High - Significantly improves core user experience and reduces confusion during indexing operations.

## Business Value
- **Status Transparency**: Users understand what's happening during indexing (no more "black box" experience)
- **Problem Diagnosis**: Clear error indicators help users identify and fix PDF issues
- **Workflow Efficiency**: Users stay on Index tab to review results instead of being forced to Search tab
- **User Confidence**: Real-time feedback and completion summaries build trust in the application

## Target Users
- All users who perform indexing operations
- Users managing large libraries with mixed PDF availability
- Users troubleshooting indexing issues

## Dependencies
- Existing IndexingService architecture (Epic 2)
- Index tab UI (Epic 6.1)
- Paper list display in Index tab

## Technical Scope
- UI changes to Index tab paper list
- Real-time status update signals from IndexingService
- Indexing summary display logic
- Application startup default tab configuration

---

## Story 8.1: Add Indexing Status Column to Paper List in Index Tab

### User Story
As a user, I want to see the indexing status of each paper at a glance, so that I can quickly identify which papers are indexed, which have issues, and which haven't been processed yet.

### Acceptance Criteria

1. **Status Column Added**
   - Index tab paper table/list displays new "Status" column
   - Column positioned prominently (e.g., after Title or Author column)
   - Column header labeled "Status"
   - Column sortable (status priority: PDF Error > No PDF > Not Indexed > Indexed)

2. **Status Values Defined**
   - **Not Indexed** (default): Paper has not been processed by indexing service
   - **Indexed**: Paper successfully processed and added to vector index
   - **No PDF**: Paper exists in Zotero but has no attached PDF
   - **PDF Error**: PDF exists but text extraction or processing failed

3. **Visual Indicators**
   - Each status has distinct icon and colored text:
     - **Not Indexed**: ⚪ gray circle, gray text "Not Indexed"
     - **Indexed**: ✅ green checkmark, green text "Indexed"
     - **No PDF**: ⚠️ yellow warning triangle, yellow text "No PDF"
     - **PDF Error**: ❌ red X, red text "PDF Error"
   - Icons rendered as Unicode characters or PySide6 icons
   - Colors accessible (sufficient contrast, colorblind-friendly)

4. **Default State**
   - All papers display "Not Indexed" status initially (on app launch or library load)
   - Status persists across app sessions (stored in metadata database)

5. **Column Behavior**
   - Status column width auto-sized to fit longest status text + icon
   - Column resizable by user
   - Column position configurable (user can reorder columns if table supports it)

### Technical Notes
- Add `indexing_status` field to paper data model (if not already present)
- Store status in metadata database (`paper_metadata` or `documents` table)
- Add column to `QTableWidget` or `QTableView` in Index tab
- Use `QTableWidgetItem` with icon and styled text for each cell
- Default status: "not_indexed" in database, displayed as "Not Indexed" with gray icon

### Definition of Done
- [ ] Status column visible in Index tab paper list
- [ ] All four status values display correctly with icons and colors
- [ ] Default status is "Not Indexed" for all papers
- [ ] Column sortable by status
- [ ] Visual design reviewed and approved
- [ ] Status values persisted in metadata database
- [ ] Manual testing confirms column displays correctly with sample data

---

## Story 8.2: Update Indexing Status in Real-Time During Indexing

### User Story
As a user, I want to see each paper's status update in real-time as indexing progresses, so that I can monitor progress and identify problems immediately.

### Acceptance Criteria

1. **Status Updates During Indexing**
   - As IndexingService processes each paper, status changes from "Not Indexed" to appropriate final status
   - Status updates visible in UI within 1 second of processing completion
   - UI remains responsive during indexing (updates don't block)

2. **Success Case**
   - Papers successfully indexed change status to "Indexed" (green checkmark)
   - Status update includes timestamp of indexing (optional: hover tooltip shows timestamp)

3. **No PDF Case**
   - Papers without attached PDFs change status to "No PDF" (yellow warning)
   - Status set before attempting text extraction
   - No error logged (this is expected state, not an error)

4. **PDF Error Case**
   - Papers with PDF processing failures change status to "PDF Error" (red X)
   - Error logged with details (paper ID, error message)
   - Optional: tooltip or detail view shows error reason

5. **Concurrent Indexing Handling**
   - Multiple papers can be processed concurrently (if indexing is parallel)
   - Status updates don't conflict or race
   - Final status reflects actual processing outcome

6. **Re-indexing Behavior**
   - When user re-runs indexing, statuses reset or update appropriately
   - Previously indexed papers can be re-indexed (status updates from "Indexed" to "Indexed" with new timestamp)
   - Failed papers can be retried (status updates from "PDF Error" to "Indexed" if successful)

### Technical Notes
- IndexingService emits signals for each paper: `paper_indexed(paper_id, status, error_msg)`
- MainWindow connects to signal and updates status column cell
- Use Qt's thread-safe signal/slot mechanism for updates
- Store status + timestamp in metadata database
- Consider batch updates if indexing is very fast (update UI every N papers or every X ms)

### Definition of Done
- [ ] Status updates appear in real-time during indexing
- [ ] All three final statuses (Indexed, No PDF, PDF Error) work correctly
- [ ] UI remains responsive during indexing
- [ ] Status changes persisted to database
- [ ] Re-indexing updates statuses correctly
- [ ] Manual testing with sample library confirms correct behavior
- [ ] Unit tests verify signal emission and status update logic
- [ ] Integration tests confirm database persistence

---

## Story 8.3: Display Indexing Summary After Completion

### User Story
As a user, I want to see a summary of indexing results after completion, so that I understand what was processed and can quickly identify any issues.

### Acceptance Criteria

1. **Summary Display Location**
   - Summary appears directly below "Start Indexing" button in Index tab
   - Summary displayed as text label or small info banner
   - Summary positioned prominently, easy to spot

2. **Summary Content**
   - Total papers processed: count
   - Successfully indexed: count (green text or icon)
   - No PDF: count (yellow text or icon)
   - Errors: count (red text or icon)
   - Example format: "✅ Indexed: 45 | ⚠️ No PDF: 3 | ❌ Errors: 2"

3. **Summary Timing**
   - Summary appears immediately after indexing completes
   - Summary replaces any previous summary
   - Summary persists until next indexing operation starts

4. **Summary Lifecycle**
   - Summary cleared/hidden when "Start Indexing" button is clicked again
   - Summary not persisted across app sessions (shown only for current indexing run)
   - Optional: summary includes completion timestamp

5. **Visual Design**
   - Summary uses color-coded text matching status column colors
   - Summary has appropriate padding and spacing
   - Summary doesn't interfere with button or other controls
   - Summary style consistent with application theme

6. **Edge Cases**
   - If no papers processed (empty selection): summary shows "No papers to index"
   - If indexing cancelled: summary shows partial results + "Cancelled" indicator
   - If indexing fails completely: summary shows error message

### Technical Notes
- Add `QLabel` below "Start Indexing" button in Index tab layout
- Update label text when indexing completes (connect to `indexing_finished` signal)
- Format summary string with counts and icons
- Use HTML or styled text for colored output
- Hide label initially (or show "Ready to index" placeholder)

### Definition of Done
- [ ] Summary label displays below Start Indexing button
- [ ] Summary shows counts for indexed, no PDF, and errors
- [ ] Summary appears immediately after indexing completes
- [ ] Summary uses color-coded text matching status icons
- [ ] Summary clears when indexing restarts
- [ ] Edge cases handled (empty selection, cancellation, errors)
- [ ] Visual design reviewed and approved
- [ ] Manual testing confirms summary accuracy with various scenarios

---

## Story 8.4: Remove Auto-Tab-Switch After Indexing & Default to Search Tab

### User Story
As a user, I want to stay on the Index tab after indexing completes so I can review the results, and I want the app to open to the Search tab by default since that's my primary activity.

### Acceptance Criteria

1. **Remove Auto-Switch After Indexing**
   - After indexing completes, user remains on Index tab
   - No automatic switch to Search tab or any other tab
   - User can manually switch tabs if desired

2. **Default Tab on Startup**
   - Application opens to Search tab on launch (not Index tab)
   - Default tab setting applies to all users (not configurable in MVP)

3. **Manual Tab Switching Preserved**
   - User can switch tabs at any time (before, during, or after indexing)
   - Tab switching via clicks, keyboard shortcuts (if implemented) works normally
   - No interference with manual navigation

4. **State Consistency**
   - Active tab state preserved if user manually switches during indexing
   - Indexing completion doesn't override user's tab choice
   - No unexpected tab switches in any scenario

### Technical Notes
- Remove `self.tabs.setCurrentIndex(SEARCH_TAB_INDEX)` call from indexing completion handler
- Change `MainWindow.__init__()` to set default tab: `self.tabs.setCurrentIndex(SEARCH_TAB_INDEX)`
- Verify no other code automatically switches tabs
- Test all indexing completion paths (success, error, cancellation)

### Definition of Done
- [ ] Auto-switch to Search tab after indexing removed
- [ ] Application opens to Search tab on launch
- [ ] Manual tab switching works correctly
- [ ] User stays on Index tab after indexing completes
- [ ] Manual testing confirms no unexpected tab switches
- [ ] Regression testing confirms existing navigation still works
- [ ] Unit tests verify default tab initialization

---

## Epic Acceptance Criteria

1. **Status Visibility Working**
   - Status column displays all four statuses correctly with icons and colors
   - Real-time updates work during indexing
   - Status values persist across sessions

2. **Summary Display Functional**
   - Indexing summary appears after completion with accurate counts
   - Summary format is clear and easy to read
   - Summary clears appropriately on re-indexing

3. **Navigation Improvements Complete**
   - Auto-switch after indexing removed
   - Application opens to Search tab by default
   - User workflow improved (stays on Index tab to review results)

4. **Quality Standards Met**
   - All acceptance criteria verified
   - Manual testing confirms improved user experience
   - No regressions in existing indexing functionality
   - Performance acceptable (status updates don't slow indexing)

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Real-time updates slow indexing | Medium | Use batch updates or throttle UI refreshes; prioritize indexing speed over instant updates |
| Status column clutter with large libraries | Low | Ensure sortable and filterable; consider default sort by status (errors first) |
| Summary format unclear | Low | User test summary designs; iterate on clarity and conciseness |
| Default tab change confuses existing users | Low | Document change in release notes; most users will appreciate Search as default |

## Out of Scope for This Epic

- Filtering papers by status (future enhancement)
- Exporting indexing report (CSV, PDF)
- Detailed error messages in status column (only tooltip or separate view)
- Per-collection indexing summaries
- Historical indexing logs or reports
- Status change notifications or alerts
- Customizable status icons or colors
- Remember last active tab preference

