# Future Considerations (Out of Scope for MVP)

*   **Real-time Sync with Zotero:** The current design relies on manual or periodic re-indexing. A future version could use a file system watcher or a Zotero plugin to trigger updates in real-time.
*   **Alternative Embedding Models:** While the API is "OpenAI-compatible," the UI could be enhanced to explicitly support other models (e.g., Cohere, local sentence-transformers) with different embedding dimensions.
*   **Advanced Search Filters:** Post-MVP, the UI could support filtering search results by date, author, or Zotero tags.
*   **Cloud-Based Version:** A future product line could offer a cloud-hosted version for users who want to access their library from multiple devices, though this would require a complete architectural redesign around a client-server model.
*   **Collaborative Features:** Sharing indexed libraries or search results with other users is a potential future direction but is explicitly out of scope for the local-first MVP.

