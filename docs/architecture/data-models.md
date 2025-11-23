# Data Models

## Document

**Purpose:** Represents a single source document (e.g., a PDF) from the user's Zotero library, storing its essential metadata.

**Key Attributes:**
*   `id`: `int` - The unique identifier for the document in our local database.
*   `zotero_item_key`: `str` - The key of the item in the Zotero database, for cross-referencing.
*   `title`: `str` - The title of the document.
*   `authors`: `list[str]` - A list of the document's authors.
*   `year`: `int` - The publication year.
*   `pdf_file_path`: `str` - The absolute file path to the PDF.
*   `indexed_at`: `datetime` - The timestamp of when the document was last indexed.
*   `indexing_status`: `str` - The current indexing status ('not_indexed', 'indexed', 'no_pdf', 'pdf_error').

### Python Dataclass
```python
from dataclasses import dataclass
from datetime import datetime

@dataclass
class Document:
    id: int
    zotero_item_key: str
    title: str
    authors: list[str]
    year: int
    pdf_file_path: str
    indexed_at: datetime
    indexing_status: str
```

### Relationships
*   Has a one-to-many relationship with `Chunk`.
*   Has a many-to-many relationship with `Collection` (via the `DocumentCollection` link table).

---
## Chunk

**Purpose:** Represents a small, searchable segment of text extracted from a `Document`. This is the unit of retrieval for semantic search.

**Key Attributes:**
*   `id`: `int` - The unique identifier for the chunk in our local database.
*   `document_id`: `int` - A foreign key linking this chunk back to its parent `Document`.
*   `content`: `str` - The actual text content of the chunk.
*   `page_number`: `int` - The page number in the source PDF where this chunk originates.
*   `vector_id`: `int` - The ID of this chunk's embedding within the FAISS vector index.

### Python Dataclass
```python
from dataclasses import dataclass

@dataclass
class Chunk:
    id: int
    document_id: int
    content: str
    page_number: int
    vector_id: int
```

### Relationships
*   Has a many-to-one relationship with `Document`.

---
## Collection

**Purpose:** Represents a collection from the user's Zotero library, allowing for scoped indexing and browsing.

**Key Attributes:**
*   `id`: `int` - The unique identifier for the collection in our local database.
*   `zotero_collection_key`: `str` - The key of the collection in the Zotero database.
*   `name`: `str` - The name of the collection.
*   `parent_id`: `int | None` - A self-referencing foreign key to support nested collections.

### Python Dataclass
```python
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class Collection:
    id: int
    zotero_collection_key: str
    name: str
    parent_id: Optional[int] = None
```

### Relationships
*   Has a many-to-many relationship with `Document` (via the `DocumentCollection` link table).
*   Can have a one-to-many relationship with itself to represent nested structures.

---
## DocumentCollection (Link Table)

**Purpose:** A link table to create the many-to-many relationship between `Document` and `Collection`, as a single document can exist in multiple collections.

**Key Attributes:**
*   `document_id`: `int` - Foreign key to the `Document`.
*   `collection_id`: `int` - Foreign key to the `Collection`.

### Python Dataclass
```python
from dataclasses import dataclass

@dataclass
class DocumentCollection:
    document_id: int
    collection_id: int
```

---
## TokenUsage

**Purpose:** Represents a record of API token consumption for a single operation, enabling transparency and cost tracking for users.

**Key Attributes:**
*   `timestamp`: `datetime` - When the API call was made.
*   `operation`: `str` - The type of operation ("embedding" or "analysis").
*   `tokens_used`: `int` - The number of tokens consumed in this operation.
*   `model`: `str` - The model used for the operation (e.g., "text-embedding-ada-002", "gpt-4").
*   `estimated_cost_usd`: `float` - The estimated cost in USD for this operation.

### Python Dataclass
```python
from dataclasses import dataclass
from datetime import datetime

@dataclass
class TokenUsage:
    timestamp: datetime
    operation: str  # "embedding" or "analysis"
    tokens_used: int
    model: str
    estimated_cost_usd: float
```

### Relationships
*   Stored as a list in application state for session-based tracking.
*   Used by the `TokenUsageWidget` component for display.
