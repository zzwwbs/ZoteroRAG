## Epic 3: Semantic Search & Results Display

### Expanded Goal:

This epic delivers the core value proposition of the application: semantic search. It will enable users to ask natural language questions, have those questions converted into embeddings, and see the most relevant results retrieved from their local index. The focus is on creating a fluid and intuitive user interface for exploring the search results, both as individual text chunks and as a list of source papers.

### Story 3.1: Implement Search Bar and Query Embedding

As a **user**,
I want **a search bar where I can type my question**,
so that **I can initiate a semantic search**.

#### Acceptance Criteria

1.  3.1.1: The main UI includes a prominent text input field for search queries.
2.  3.1.2: When a user executes a search, the application sends the query text to the configured cloud embedding API.
3.  3.1.3: The application receives the resulting query embedding vector.
4.  3.1.4: The UI indicates that a search is in progress.

### Story 3.2: Implement Vector Search and Retrieval

As a **developer**,
I want to **use the query embedding to search the local FAISS index and retrieve the most relevant text chunks**,
so that **I can find the best matches for the user's question**.

#### Acceptance Criteria

1.  3.2.1: The application performs a similarity search on the FAISS index using the query embedding.
2.  3.2.2: The search returns a list of the top K most similar chunk IDs (where K is configurable).
3.  3.2.3: The application then retrieves the full metadata for these chunks from the SQLite database.
4.  3.2.4: The retrieval process is performant, returning results in under a second for a typical query.

### Story 3.3: Implement Results Display UI

As a **user**,
I want to **see the search results displayed clearly in a split-pane view**,
so that **I can easily explore the relevant papers and text snippets**.

#### Acceptance Criteria

1.  3.3.1: The UI is divided into two main panels: a "Papers" view and a "Chunks" view.
2.  3.3.2: The "Papers" view lists the unique source documents for the retrieved chunks, showing title, authors, year, and the number of matching chunks.
3.  3.3.3: The "Chunks" view displays the text of each relevant snippet, along with its source paper and page number.
4.  3.3.4: Initially, the "Chunks" view shows all retrieved chunks, sorted by relevance.

### Story 3.4: Implement Interactive Results Filtering

As a **user**,
I want to be able to **click on a paper in the "Papers" view to filter the "Chunks" view**,
so that **I can focus on the results from a single document**.

#### Acceptance Criteria

1.  3.4.1: Clicking a paper in the "Papers" view updates the "Chunks" view to show only the chunks from that selected paper.
2.  3.4.2: The UI provides a clear way to remove the filter and return to viewing all chunks.
3.  3.4.3: The application includes a button next to each paper and/or chunk to "Open full PDF", which opens the corresponding PDF file in the system's default viewer.
