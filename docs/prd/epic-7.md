# Epic 7: Enhanced AI Configuration & Chat Experience

## Epic Goal
Enable flexible AI provider configuration and transform AI Analysis into an interactive chat interface with user-controlled retrieval.

## Epic Priority
High - Enhances core AI functionality and provides better user control over AI interactions.

## Business Value
- **User Flexibility**: Users can choose different providers for embedding vs chat, optimizing for cost or performance
- **Enhanced Interaction**: Chat interface enables iterative exploration and refinement of research questions
- **Cost Control**: Token usage transparency and retrieval control help users manage API costs
- **Better UX**: Natural conversation flow improves usability over single-shot analysis

## Target Users
- Researchers who want conversational AI interaction with their research papers
- Users with specific AI provider preferences or constraints
- Cost-conscious users who need fine-grained control over API usage

## Dependencies
- Existing AIService and EmbeddingClient architecture (Epic 4)
- Settings infrastructure (Epic 5)
- Token tracking system (Story 6.6)

## Technical Scope
- Settings schema updates for split configuration
- UI reorganization and new chat components
- Conversation context management
- Retrieval toggle and chunk selection

---

## Story 7.1: Split API Configuration for Embedding vs Chat Models

### User Story
As a researcher, I want to configure separate AI providers for embedding generation and chat analysis, so that I can optimize my costs and use the best model for each purpose.

### Acceptance Criteria

1. **Settings Schema Extended**
   - Settings include separate fields for embedding and chat configurations:
     - `embedding_provider` (dropdown: OpenAI, Azure OpenAI, Custom)
     - `embedding_model` (text field)
     - `embedding_api_key` (secure text field)
     - `embedding_base_url` (text field, optional for custom endpoints)
     - `chat_provider` (dropdown: OpenAI, Azure OpenAI, Custom)
     - `chat_model` (text field)
     - `chat_api_key` (secure text field)
     - `chat_base_url` (text field, optional for custom endpoints)
   - All fields stored securely in settings file

2. **Settings UI Updated**
   - Settings dialog shows two distinct configuration sections:
     - "Embedding Configuration" section with provider, model, API key, base URL
     - "Chat Configuration" section with provider, model, API key, base URL
   - Each section can be configured independently
   - Visual separation between sections (group boxes or tabs)
   - Help text explains purpose of each configuration type

3. **Configuration Migration**
   - On first launch after upgrade, existing `api_provider`, `api_model`, `api_key`, `base_url` settings are copied to both `embedding_*` and `chat_*` fields
   - Original fields retained for backward compatibility but marked deprecated
   - Migration logged for troubleshooting

4. **Service Integration**
   - `EmbeddingClient` constructed using `embedding_*` settings
   - `AIService` constructed using `chat_*` settings
   - Settings changes trigger service reconstruction with new configurations
   - Error handling for invalid or missing configurations

5. **Validation**
   - Both configurations validated before saving
   - Required fields enforced (provider, model, API key)
   - Clear error messages for validation failures
   - Test connection button for each configuration (optional but recommended)

### Technical Notes
- Update `SettingsManager` schema to include new fields
- Modify `MainWindow._load_state_from_settings()` to use appropriate settings for each service
- Add migration logic in settings loading path
- Consider using `QGroupBox` or `QTabWidget` to organize settings sections

### Definition of Done
- [ ] Settings schema includes all new fields with proper types
- [ ] Settings UI displays both configuration sections clearly
- [ ] Migration logic preserves existing user settings
- [ ] EmbeddingClient uses embedding_* settings
- [ ] AIService uses chat_* settings
- [ ] Settings validation prevents invalid configurations
- [ ] Manual testing confirms both services work with different providers
- [ ] Unit tests cover settings migration and service construction

---

## Story 7.2: Move Analyze Button to AI Analysis Tab

### User Story
As a user, I want the Analyze button to be located in the AI Analysis tab where I see the results, so that the interface is more intuitive and context-appropriate.

### Acceptance Criteria

1. **Button Removed from Search Tab**
   - "Analyze" button no longer appears in Search tab action bar
   - Search tab action bar contains only: Open in Zotero, Open PDF, Copy as Prompt

2. **Button Added to AI Analysis Tab**
   - AI Analysis tab displays "Analyze Selected Papers" button prominently
   - Button positioned at top of tab, above any results/chat area
   - Button uses clear, action-oriented label

3. **Button State Management**
   - Button disabled when no search results are available
   - Button enabled when search results exist (papers selected)
   - Tooltip explains why button is disabled when applicable
   - Visual feedback on hover/press states

4. **Functionality Preserved**
   - Button triggers same analysis workflow as before
   - Analysis results appear in AI Analysis tab (chat area)
   - Token usage tracking continues to work
   - Error handling unchanged

### Technical Notes
- Remove button from `search_tab` action bar layout
- Add button to `ai_analysis_tab` at appropriate position
- Update button enabled/disabled logic based on search results availability
- Ensure signal/slot connections remain functional after relocation

### Definition of Done
- [ ] Analyze button removed from Search tab
- [ ] Analyze button present in AI Analysis tab
- [ ] Button enabled/disabled states work correctly
- [ ] Button triggers analysis as expected
- [ ] Visual design consistent with application style
- [ ] Manual testing confirms all functionality preserved

---

## Story 7.3: Remove Duplicate Token Usage from AI Analysis Tab

### User Story
As a user, I want to see token usage information only in the status bar, so that the interface is cleaner and I'm not confused by duplicate information.

### Acceptance Criteria

1. **Token Widget Removed**
   - Token usage widget no longer displayed in AI Analysis tab
   - AI Analysis tab layout simplified without token display area

2. **Status Bar Display Preserved**
   - Status bar token usage display continues to work
   - All token tracking functionality intact
   - Token usage updates in real-time during operations

3. **No Functional Loss**
   - All token tracking mechanisms continue to function
   - Usage data still recorded to database
   - Historical usage still accessible (if feature exists)

### Technical Notes
- Remove `_token_usage_widget` from AI Analysis tab layout
- Verify status bar widget still receives token usage signals
- Clean up any unused code related to AI Analysis tab token display
- Ensure layout adjusts properly after widget removal

### Definition of Done
- [ ] Token usage widget removed from AI Analysis tab
- [ ] Status bar token display works correctly
- [ ] Token tracking functionality verified
- [ ] UI layout looks clean without widget
- [ ] Manual testing confirms no regression in token tracking

---

## Story 7.4: Convert AI Analysis to Chat Interface

### User Story
As a researcher, I want to interact with AI through a chat interface, so that I can have a natural conversation about my research papers and iteratively refine my questions.

### Acceptance Criteria

1. **Chat Message Display**
   - Replace single read-only text output with scrollable chat message area
   - Display conversation history with distinct visual styling:
     - All messages left-aligned (user and AI)
     - User messages: lighter background, "You:" prefix
     - AI messages: distinct background color, "Assistant:" prefix
   - Messages show timestamps
   - Auto-scroll to latest message on new message arrival

2. **Chat Input Area**
   - Text input field at bottom of AI Analysis tab
   - "Send" button next to input field (or Enter key sends)
   - Multi-line input support (Shift+Enter for newline)
   - Clear visual separation from message display area

3. **Initial Message Handling**
   - When user clicks "Analyze Selected Papers", first AI response appears as first message in chat
   - Chat history starts fresh for each analysis session
   - Clear indication when starting new analysis vs continuing conversation

4. **Visual Design**
   - Clean, readable message formatting
   - Appropriate padding and spacing between messages
   - Color scheme consistent with application theme
   - Loading indicator while AI processes message

5. **Message State Indicators**
   - "Analyzing..." or loading spinner shown while AI is responding
   - Error messages displayed inline in chat (e.g., "Failed to get response from AI")
   - Sent messages appear immediately, AI responses appear after processing

### Technical Notes
- Use `QScrollArea` + `QVBoxLayout` for message display
- Create message widget components for user and AI messages
- Use `QTextEdit` or `QPlainTextEdit` for input (multi-line support)
- Implement auto-scrolling to bottom on new messages
- Consider using `QLabel` with word wrap for individual messages

### Definition of Done
- [ ] Chat message area displays conversation history
- [ ] User and AI messages visually distinct
- [ ] Input field at bottom accepts multi-line text
- [ ] Send button and Enter key both send messages
- [ ] Auto-scrolling works correctly
- [ ] Loading states displayed during AI processing
- [ ] Visual design reviewed and approved
- [ ] Manual testing confirms smooth conversation flow

---

## Story 7.5: Implement Chat Message Handling & API Integration

### User Story
As a user, I want my chat messages to be processed by AI with conversation context, so that I can have meaningful back-and-forth discussions about my research.

### Acceptance Criteria

1. **Message Processing**
   - User input captured from text field
   - Input validated (not empty, reasonable length)
   - User message immediately displayed in chat
   - Input field cleared after sending

2. **Conversation Context**
   - Previous messages included in API request for context
   - Context limited to reasonable size (e.g., last 10 messages or 4000 tokens)
   - System message or initial prompt includes instructions about research analysis
   - Conversation context maintained for session duration

3. **API Integration**
   - AIService called with user message + conversation history
   - Response handling for streaming (if supported) or complete responses
   - Partial responses displayed as they arrive (streaming) or full response shown after completion
   - Error handling for API failures, rate limits, timeouts

4. **Response Display**
   - AI responses appear in chat with proper formatting
   - Markdown support for formatted responses (optional but recommended)
   - Code blocks, lists, bold/italic rendered appropriately
   - Long responses wrapped and scrollable

5. **Token Tracking**
   - Token usage recorded for each chat message exchange
   - Status bar token display updated after each interaction
   - Token usage signals emitted with correct model and provider info

### Technical Notes
- Maintain message history in `MainWindow` or dedicated chat manager
- Format conversation for API: `[{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]`
- Use existing `AIService.analyze()` or create new `chat()` method
- Connect chat send action to `_handle_ai_analyze()` or new handler
- Implement token usage signal emission in chat response handling

### Definition of Done
- [ ] User messages sent to AIService with conversation context
- [ ] AI responses received and displayed correctly
- [ ] Conversation context maintained across multiple exchanges
- [ ] Token usage tracked for all chat interactions
- [ ] Error handling prevents crashes on API failures
- [ ] Manual testing confirms smooth multi-turn conversations
- [ ] Unit tests cover message formatting and context management
- [ ] Integration tests verify API calls with conversation history

---

## Story 7.6: Add Retrieval Toggle & Chunk Count Control

### User Story
As a researcher, I want to control whether AI retrieves paper context and how many chunks to include, so that I can balance between detailed context and focused questions.

### Acceptance Criteria

1. **Retrieval Controls UI**
   - Checkbox labeled "Include search context" in AI Analysis tab
   - Spinbox for "Number of chunks to retrieve" (range: 1-20, default: 5)
   - Spinbox enabled only when checkbox is checked
   - Controls positioned near chat input or top of tab
   - Tooltip explains: "Include relevant paper excerpts in AI analysis"

2. **Toggle ON Behavior**
   - When checked: retrieve top N chunks from current search results
   - Retrieved chunks prepended to conversation context as system message or user message prefix
   - Chunk context includes: paper title, author, chunk text
   - Context formatted clearly: "Context from search results: [chunks]"

3. **Toggle OFF Behavior**
   - When unchecked: send only user message to AI (no retrieval)
   - AI receives conversation history but no paper excerpts
   - Allows for general questions not requiring paper context

4. **Spinbox Functionality**
   - Value changes update number of chunks retrieved on next message
   - Immediate visual feedback on value change
   - Invalid values prevented (clamped to 1-20 range)

5. **State Management**
   - Toggle state and chunk count stored in session (not persisted across app restarts)
   - Default state on new analysis: toggle ON, chunk count 5
   - State preserved during conversation session

6. **Integration with Chat**
   - Retrieval happens only when toggle is ON
   - Retrieved context included in API request for that message only
   - Subsequent messages use toggle state at time of sending
   - Clear indication in UI when context was included (optional: show chunk count in message)

### Technical Notes
- Add `QCheckBox` and `QSpinBox` to AI Analysis tab layout
- Implement retrieval logic: query `SearchService` for top N chunks
- Format retrieved context as system message or prepend to user message
- Update `_handle_ai_analyze()` or chat handler to conditionally include retrieval
- Consider showing "Retrieved 5 chunks" indicator in chat message

### Definition of Done
- [ ] Checkbox and spinbox displayed in AI Analysis tab
- [ ] Controls functionally enable/disable retrieval
- [ ] Chunk count changes affect number of retrieved chunks
- [ ] Toggle ON includes paper context in AI request
- [ ] Toggle OFF sends message without retrieval
- [ ] Default state is toggle ON, count 5
- [ ] State preserved during conversation session
- [ ] Manual testing confirms retrieval behavior matches expectations
- [ ] Unit tests verify retrieval logic and context formatting

---

## Epic Acceptance Criteria

1. **Split Configuration Working**
   - Users can configure different providers for embedding and chat
   - Both configurations work independently
   - Settings migration preserves existing user settings

2. **Chat Interface Functional**
   - Users can have multi-turn conversations in AI Analysis tab
   - Conversation context maintained across messages
   - Token usage tracked for all interactions

3. **Retrieval Control Effective**
   - Users can toggle retrieval on/off and adjust chunk count
   - Retrieval behavior matches user expectations
   - Performance acceptable with different chunk counts

4. **UI Improvements Complete**
   - Analyze button relocated to AI Analysis tab
   - Duplicate token display removed
   - Visual design clean and consistent

5. **Quality Standards Met**
   - All acceptance criteria verified
   - Unit and integration tests passing
   - Manual testing confirms smooth user experience
   - No regressions in existing functionality

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Chat interface complexity | Medium | Keep MVP simple: basic input/output, defer advanced features (history persistence, streaming animations) |
| Conversation context token limits | Medium | Implement context window management, limit to last N messages or token budget |
| Retrieval toggle confusion | Low | Provide clear tooltips and help text; consider showing context indicator in messages |
| Config UI becomes cluttered | Medium | Use collapsible sections or tabs for embedding vs chat settings |
| Performance with large chunk counts | Low | Implement chunking limit (20 max), warn user if large count may be slow |

## Out of Scope for This Epic

- Chat history persistence across sessions
- Streaming response animations
- Conversation export/sharing
- Multiple conversation threads
- File attachments in chat
- Voice input/output
- Custom system prompts per conversation
- Token usage budgets or limits

