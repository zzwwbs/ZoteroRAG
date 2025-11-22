# Epic 7, 8, 9 Planning Summary

**Created:** November 22, 2025  
**Status:** Approved - Ready for Implementation

## Overview

Three new epics created to address UX improvements, AI enhancements, and interface reorganization based on post-MVP feedback.

## Implementation Decisions

### Epic Structure
✅ **Approved:** Domain-based organization (by functional area)
- Epic 7: AI Configuration & Chat
- Epic 8: Indexing UX
- Epic 9: Search Tab Actions

### Key Design Decisions

#### Epic 7: Enhanced AI Configuration & Chat Experience

**Chat Interface:**
- ✅ All messages left-aligned (not chat-app style)
- ✅ User messages: lighter background, "You:" prefix
- ✅ AI messages: distinct background, "Assistant:" prefix

**Retrieval Control:**
- ✅ Story 7.6 positioned as LAST story in epic
- ✅ Toggle default: ON, chunk count: 5
- ✅ State NOT persisted across sessions (session-only)
- ✅ Range: 1-20 chunks

**Configuration:**
- ✅ Split config for embedding vs chat providers
- ✅ Migration: copy existing settings to both configs
- ✅ No migration warnings needed (not released yet)

#### Epic 8: Indexing & Search UX Improvements

**Status Column:**
- ✅ Icons: ⚪ ✅ ⚠️ ❌ (Unicode or PySide6 icons)
- ✅ Colored text matching icon semantics
- ✅ Four statuses: Not Indexed (default), Indexed, No PDF, PDF Error

**Indexing Summary:**
- ✅ Display: Simple text label below "Start Indexing" button
- ✅ Format: "✅ Indexed: 45 | ⚠️ No PDF: 3 | ❌ Errors: 2"
- ✅ Clears on next indexing start

**Navigation:**
- ✅ Remove auto-switch to Search tab after indexing
- ✅ Default tab on startup: Search (not Index)

**Out of Scope:**
- ❌ Per-collection indexing counts (too complex)

#### Epic 9: Search Tab Action Reorganization

**Button Layout:**
- ✅ Move buttons to bottom of Search tab
- ✅ Rename: "Copy to ChatGPT" → "Copy as Prompt"

## Epic Priorities & Sequencing

**Recommended Implementation Order:**
1. **Epic 9** (1 story) - Quick win, ~2 story points
2. **Epic 8** (4 stories) - Medium effort, ~13 story points
3. **Epic 7** (6 stories) - Most complex, ~21 story points

**Total Effort:** 36 story points

**Dependencies:**
- Epic 7 stories must be sequential (7.1 → 7.2 → 7.3 → 7.4 → 7.5 → 7.6)
- Epic 8: Story 8.1 must precede 8.2; others flexible
- Epic 9: No dependencies

## Story Breakdown

### Epic 7 Stories (6)
1. 7.1: Split API Configuration (5 pts)
2. 7.2: Move Analyze Button (3 pts)
3. 7.3: Remove Duplicate Token Display (2 pts)
4. 7.4: Convert to Chat Interface (5 pts)
5. 7.5: Implement Chat Logic & API Integration (5 pts)
6. 7.6: Add Retrieval Toggle & Chunk Control (1 pt) ⭐ LAST

### Epic 8 Stories (4)
1. 8.1: Add Status Column (3 pts)
2. 8.2: Real-Time Status Updates (5 pts)
3. 8.3: Indexing Summary Display (3 pts)
4. 8.4: Remove Auto-Switch & Default Tab (2 pts)

### Epic 9 Stories (1)
1. 9.1: Move Buttons & Rename (2 pts)

## Files Created

```
docs/prd/
├── 5-epic-list.md          (updated with Epics 7-9)
├── epic-7.md               (17KB - Enhanced AI Configuration & Chat)
├── epic-8.md               (12KB - Indexing & Search UX Improvements)
├── epic-9.md               (6KB - Search Tab Action Reorganization)
├── epic-7-8-9-summary.md   (this file)
└── index.md                (updated with new epic links)
```

## Next Steps

1. ✅ Epic documentation created
2. ✅ Epic list and index updated
3. ⏳ **Pending:** Create detailed user stories in `docs/stories/` folder
4. ⏳ **Pending:** Begin implementation starting with Epic 9

## Notes

- All epics approved without breaking changes (application not released yet)
- No user migration required
- Focus on UX improvements based on internal testing feedback
- Design decisions documented for future reference

