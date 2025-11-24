### Epic 11: Performance-Oriented PDF Library Migration

#### Expanded Goal:

This epic addresses the performance limitations observed with the `pdfplumber` library. The goal is to migrate the PDF extraction implementation to `pypdfium2`, a library known for higher performance and efficiency, to significantly improve indexing speed and reduce resource consumption, directly addressing a key performance bottleneck.

#### Story 11.1: Replace PDF Extraction with PyPDFium2

As a **developer**,
I want to **replace the `pdfplumber`-based text extraction with a `pypdfium2`-based implementation**,
so that **the application's PDF processing is faster and more efficient**.

##### Acceptance Criteria

1.  11.1.1: All code referencing `pdfplumber` is removed and replaced with `pypdfium2` equivalents.
2.  11.1.2: The application successfully extracts text content from a sample PDF using `pypdfium2`.
3.  11.1.3: The application logs errors for PDFs from which text extraction fails but continues processing other PDFs.
4.  11.1.4: The extracted text is available for subsequent processing steps in the same format as the previous implementation.

#### Story 11.2: Benchmark and Verify Performance Gains

As a **user**,
I want to **ensure that the new PDF extraction library provides a measurable performance improvement**,
so that **the indexing process is noticeably faster**.

##### Acceptance Criteria

1.  11.2.1: PDF extraction performance with `pypdfium2` is benchmarked against `pdfplumber` using a representative set of 100 documents of varying complexity.
2.  11.2.2: The new implementation demonstrates at least a 30% reduction in average processing time per document.
3.  11.2.3: Memory usage during PDF processing is measured and does not exceed previous levels.
4.  11.2.4: Integration tests for the indexing process pass successfully with the new library, and error handling for corrupted PDFs remains robust.
