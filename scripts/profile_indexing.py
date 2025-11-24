
import cProfile
import pstats
import logging
from pathlib import Path
from unittest.mock import MagicMock
from zoterorag.core.services.indexing_service import IndexingService
from zoterorag.core.data.models import Chunk, TokenUsage

# Configure logging
logging.basicConfig(level=logging.INFO)

def profile_indexing():
    # Mock dependencies
    mock_zotero = MagicMock()
    mock_zotero.get_items_for_scope.return_value = [
        MagicMock(item_id=1, item_key="TEST", title="Test PDF", authors="Author", year="2023")
    ]
    mock_zotero.get_pdf_attachments.return_value = [Path("tests/test.pdf")]

    mock_embedding = MagicMock()
    # Return a dummy embedding and usage
    mock_embedding.get_embedding.return_value = ([0.1] * 1536, TokenUsage(operation="embedding", tokens_used=10, model="test"))

    mock_metadata = MagicMock()
    mock_metadata.get_document_by_key.return_value = None # Not indexed yet
    mock_metadata.document_repository.insert.return_value = MagicMock(id=1)
    mock_metadata.get_next_vector_id.return_value = 1

    mock_vector = MagicMock()

    # Initialize service
    service = IndexingService(
        zotero_manager=mock_zotero,
        metadata_manager=mock_metadata,
        vector_manager=mock_vector,
        embedding_client=mock_embedding,
    )

    # Run indexing
    print("Starting indexing...")
    service.start_indexing({"scope": "test"})
    print("Indexing complete.")

if __name__ == "__main__":
    profiler = cProfile.Profile()
    profiler.enable()
    profile_indexing()
    profiler.disable()
    
    stats = pstats.Stats(profiler).sort_stats("cumtime")
    stats.print_stats(20)
    stats.dump_stats("profile.out")
