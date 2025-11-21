"""Manage creation and persistence of the FAISS vector index."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Sequence

import numpy as np

try:  # pragma: no cover - dependency availability handled at runtime
    import faiss  # type: ignore
except ImportError:  # pragma: no cover
    faiss = None  # type: ignore[assignment]

logger = logging.getLogger(__name__)


class VectorDBManager:
    """Orchestrates FAISS index creation, persistence, and querying."""

    def __init__(
        self,
        dimension: int,
        data_dir: Path | None = None,
        index_filename: str = "zoterorag.faiss",
    ) -> None:
        self._dimension = dimension
        self._data_dir = (data_dir or Path.home() / ".zotero_rag").expanduser()
        self._data_dir.mkdir(parents=True, exist_ok=True)
        self._index_path = self._data_dir / index_filename
        self._index = None

    def initialize_index(self) -> None:
        self._ensure_faiss()
        # Create IndexFlatL2 and wrap it in IndexIDMap to support add_with_ids
        base_index = faiss.IndexFlatL2(self._dimension)
        self._index = faiss.IndexIDMap(base_index)

    def load_index(self) -> None:
        self._ensure_faiss()
        if self._index_path.exists():
            self._index = faiss.read_index(str(self._index_path))
        else:
            self.initialize_index()

    def save_index(self) -> None:
        self._ensure_faiss()
        if self._index is None:
            raise RuntimeError("Index has not been initialized")

        faiss.write_index(self._index, str(self._index_path))

    def add_vectors(self, vectors: Sequence[Sequence[float]], vector_ids: Sequence[int]) -> None:
        index = self._require_index()
        arr = np.asarray(vectors, dtype="float32")
        ids = np.asarray(vector_ids, dtype="int64")
        if arr.size == 0:
            return
        if arr.shape[1] != self._dimension:
            raise ValueError("Vector dimension mismatch")
        index.add_with_ids(arr, ids)

    def search(self, query_vector: Sequence[float], k: int) -> tuple[list[float], list[int]]:
        index = self._require_index()
        query = np.asarray([query_vector], dtype="float32")
        if query.shape[1] != self._dimension:
            raise ValueError("Query dimension mismatch")
        distances, ids = index.search(query, k)
        return distances[0].tolist(), ids[0].tolist()

    def _require_index(self):
        if self._index is None:
            self.load_index()
        return self._index

    def _ensure_faiss(self) -> None:
        if faiss is None:
            raise RuntimeError("FAISS is not installed. Please install faiss-cpu to use the vector database.")
