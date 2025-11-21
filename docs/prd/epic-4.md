## Epic 4: Configuration and Settings

### Expanded Goal:

This epic focuses on providing users with the ability to configure the application to their needs, with a strong emphasis on security and usability. It will enable users to manage their own API keys for external services, control AI-powered features, and customize application behavior.

### Story 4.1: Implement BYOK LLM API Configuration

As a **user**,
I want **to securely enter and manage my OpenAI (or compatible) API key within the application settings**,
so that **I can enable in-app AI analysis**.

#### Acceptance Criteria

1.  4.1.1: A dedicated section in the application settings allows users to input their LLM API key.
2.  4.1.2: The API key is stored securely (e.g., encrypted at rest) and never transmitted externally by the application itself.
3.  4.1.3: A "Test Connection" button verifies the validity of the entered API key without performing a full analysis.
4.  4.1.4: A toggle switch allows users to enable/disable in-app AI analysis, which is off by default.
