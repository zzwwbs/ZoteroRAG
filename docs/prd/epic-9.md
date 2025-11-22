# Epic 9: Search Tab Action Reorganization

## Epic Goal
Improve Search tab button layout and labeling clarity by moving action buttons to the bottom and renaming the ChatGPT export button.

## Epic Priority
Medium - Quick UX improvement that enhances usability without major functional changes.

## Business Value
- **Improved Layout**: Bottom placement of action buttons creates cleaner, more intuitive interface
- **Clarity**: "Copy as Prompt" label better describes the button's function
- **Consistency**: Action buttons grouped together in logical location
- **User Satisfaction**: Addresses common user feedback about button placement

## Target Users
- All users who perform searches and use result actions
- Users exporting results to external AI tools
- Users who found top-placed buttons visually cluttered

## Dependencies
- Existing Search tab UI (Epic 3)
- Action button functionality (Open in Zotero, Open PDF, Copy to ChatGPT)

## Technical Scope
- UI layout changes in Search tab
- Button relocation and relabeling
- Preservation of all existing functionality

---

## Story 9.1: Move Action Buttons to Bottom of Search Tab & Rename Copy Button

### User Story
As a user, I want the action buttons at the bottom of the Search tab with clear labels, so that the interface is cleaner and I can easily find the actions I need.

### Acceptance Criteria

1. **Buttons Moved to Bottom**
   - All action buttons relocated from top to bottom of Search tab
   - Buttons appear below search results list/display area
   - Buttons positioned in horizontal row (left to right)
   - Button order: "Open in Zotero" | "Open PDF" | "Copy as Prompt"

2. **Button Renamed**
   - "Copy to ChatGPT" button renamed to "Copy as Prompt"
   - New label clearly indicates function (copies formatted prompt text)
   - No other button labels changed

3. **Layout & Spacing**
   - Buttons have appropriate spacing between them (not cramped)
   - Buttons aligned consistently (left-aligned, centered, or right-aligned based on design)
   - Adequate padding from bottom of search results
   - Adequate padding from bottom of tab area

4. **Button Enabled/Disabled States**
   - All buttons maintain existing enabled/disabled logic:
     - "Open in Zotero": enabled when paper(s) selected
     - "Open PDF": enabled when selected paper has PDF
     - "Copy as Prompt": enabled when search results exist
   - Visual indication of disabled state (grayed out, reduced opacity)

5. **Functionality Preserved**
   - All buttons trigger same actions as before:
     - "Open in Zotero": opens selected paper(s) in Zotero app
     - "Open PDF": opens selected paper's PDF in default viewer
     - "Copy as Prompt": copies formatted search results to clipboard
   - No regression in button behavior
   - Tooltips/hover states remain functional

6. **Visual Design**
   - Buttons consistent with application theme and style
   - Button size and font appropriate for action buttons
   - Visual hierarchy clear (primary actions stand out)
   - Design reviewed and approved by stakeholders

### Technical Notes
- Remove buttons from top `QHBoxLayout` or toolbar in Search tab
- Add buttons to new `QHBoxLayout` at bottom of Search tab
- Use `QHBoxLayout.addStretch()` for appropriate spacing if needed
- Update button text for "Copy as Prompt" using `button.setText()`
- Verify signal/slot connections remain intact after relocation
- Test button enabled/disabled logic with various search result states

### Definition of Done
- [ ] All three action buttons relocated to bottom of Search tab
- [ ] "Copy to ChatGPT" renamed to "Copy as Prompt"
- [ ] Button layout looks clean with appropriate spacing
- [ ] Button enabled/disabled states work correctly
- [ ] All button actions function as expected
- [ ] Visual design consistent with application theme
- [ ] Manual testing confirms all functionality preserved
- [ ] No regressions in existing button behavior
- [ ] User feedback positive on new layout

---

## Epic Acceptance Criteria

1. **Layout Improvement Complete**
   - Action buttons relocated to bottom of Search tab
   - Layout cleaner and more intuitive
   - Buttons easily discoverable

2. **Labeling Clarity Achieved**
   - "Copy as Prompt" label accurately describes function
   - No confusion about button purpose

3. **Functionality Preserved**
   - All buttons work exactly as before
   - No regressions or bugs introduced
   - User workflow unaffected except for improved layout

4. **Quality Standards Met**
   - Visual design approved
   - Manual testing confirms correct behavior
   - User feedback collected and addressed

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Users accustomed to old layout | Low | Minor change, easy to adapt; document in release notes if needed |
| Layout issues on small screens | Low | Test on various screen sizes; ensure buttons don't overlap or get cut off |
| Button alignment looks odd | Low | Test different alignment options (left, center, right) and choose best |

## Out of Scope for This Epic

- Adding new action buttons (future enhancement)
- Keyboard shortcuts for buttons
- Customizable button order or visibility
- Button tooltips redesign (preserve existing)
- Button icons or visual enhancements beyond standard theme
- Accessibility improvements beyond basic functionality

## Optional Enhancement (Story 9.2 - Future Consideration)

### Story 9.2: Remember Last Active Tab Across Sessions

**User Story**: As a user, I want the application to remember which tab I was on when I closed it, so that I can continue where I left off.

**Rationale**: Some users may prefer starting on Index or AI Analysis tab based on their workflow.

**Deferred**: Not included in current epic scope; can be added in future iteration if user feedback indicates strong need.

