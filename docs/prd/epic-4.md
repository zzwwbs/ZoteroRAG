## Epic 4: AI Integration & Export Workflows

### Expanded Goal:

This epic extends the core search functionality by enabling users to act upon their retrieved information. It will implement the optional in-app AI analysis using a user-provided API key, allowing for synthesized answers with citations. Additionally, it will provide robust export options, including a formatted prompt for external LLMs like ChatGPT and the ability to **export the actual PDF files into a new folder**, enhancing the utility and flexibility of the application.

### Story 4.1: Implement BYOK LLM API Configuration

As a **user**,
I want to **securely enter and manage my OpenAI (or compatible) API key within the application settings**,
so that **I can enable in-app AI analysis**.

#### Acceptance Criteria

1.  4.1.1: A dedicated section in the application settings allows users to input their LLM API key.
2.  4.1.2: The API key is stored securely (e.g., encrypted at rest) and never transmitted externally by the application itself.
3.  4.1.3: A "Test Connection" button verifies the validity of the entered API key without performing a full analysis.
4.  4.1.4: A toggle switch allows users to enable/disable in-app AI analysis, which is off by default.

### Story 4.2: Implement In-App AI Analysis

As a **user**,
when in-app AI analysis is enabled, I want to **click a button to get a synthesized answer based on my query and the retrieved chunks**,
so that **I can quickly understand the key insights**.

#### Acceptance Criteria

1.  4.2.1: An "Analyze with AI" button is visible and enabled when an API key is configured and in-app analysis is toggled on.
2.  4.2.2: Clicking the button sends the user's query and a selection of top retrieved chunks to the configured LLM API.
3.  4.2.3: The application displays the LLM's synthesized answer in a dedicated area of the UI.
4.  4.2.4: The synthesized answer includes inline citations that map back to the source papers and chunks.
5.  4.2.5: The application handles API errors (e.g., rate limits, invalid response) gracefully, displaying informative messages.

### Story 4.3: Implement ChatGPT Export (Text Prompt)

As a **user**,
I want a **"Copy to ChatGPT" button that formats my query and relevant chunks into a ready-to-paste prompt**,
so that **I can easily continue my analysis in an external LLM**.

#### Acceptance Criteria

1.  4.3.1: A "Copy to ChatGPT" button is available on the search results screen.
2.  4.3.2: Clicking the button generates a text block containing the original query, a clear instruction for the LLM, and a numbered list of top N chunks with their metadata.
3.  4.3.3: The generated text block is automatically copied to the user's clipboard.
4.  4.3.4: A brief notification confirms that the content has been copied.

### Story 4.4: Implement PDF File Export

As a **user**,
I want to **export the actual PDF files from my search results to a new folder**,
so that **I have a self-contained collection of relevant papers for sharing or external use**.

#### Acceptance Criteria

1.  4.4.1: An "Export PDFs" button is available on the search results screen.
2.  4.4.2: Clicking the button prompts the user to select a destination folder for the export.
3.  4.4.3: The application creates a new subfolder in the selected destination (e.g., named with the current date/time or a user-provided name).
4.  4.4.4: The application copies all unique PDF files corresponding to the search results into the newly created subfolder.
5.  4.4.5: A notification confirms that the files have been successfully exported and provides the path to the new folder.