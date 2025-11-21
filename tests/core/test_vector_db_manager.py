"""Tests for vector database manager."""

import json
from pathlib import Path
from types import SimpleNamespace

import numpy as np

from zoterorag.core.services import vector_db_manager
from zoterorag.core.services.vector_db_manager import VectorDBManager


class FakeIndex:
    def __init__(self, dimension: int) -> None:
        self.dimension = dimension
        self.vectors: dict[int, list[float]] = {}

    def add_with_ids(self, vectors, ids) -> None:
        for vector, vector_id in zip(vectors, ids):
            self.vectors[int(vector_id)] = list(vector)

    def search(self, queries, k: int):
        query = list(queries[0])
        ids = list(self.vectors.keys())
        distances = []
        for vector_id in ids:
            vec = self.vectors[vector_id]
            distances.append(float(sum((a - b) ** 2 for a, b in zip(query, vec))))

        sorted_pairs = sorted(zip(distances, ids), key=lambda item: item[0])[:k]
        if not sorted_pairs:
            sorted_pairs = [(0.0, -1)] * k

        dist_row = np.array([[pair[0] for pair in sorted_pairs]], dtype="float32")
        id_row = np.array([[pair[1] for pair in sorted_pairs]], dtype="int64")
        return dist_row, id_row


class FakeIDMap:
    """Fake IndexIDMap that wraps a FakeIndex."""
    def __init__(self, base_index: FakeIndex) -> None:
        self.index = base_index
        self.dimension = base_index.dimension
        self.vectors = base_index.vectors

    def add_with_ids(self, vectors, ids) -> None:
        self.index.add_with_ids(vectors, ids)

    def search(self, queries, k: int):
        return self.index.search(queries, k)


def _install_fake_faiss(monkeypatch, tmp_path: Path):
    def write_index(index: FakeIDMap, path: str) -> None:
        serializable = {
            "dimension": index.dimension,
            "vectors": {k: [float(x) for x in v] for k, v in index.vectors.items()},
        }
        Path(path).write_text(json.dumps(serializable))

    def read_index(path: str) -> FakeIDMap:
        payload = json.loads(Path(path).read_text())
        fake_base = FakeIndex(payload["dimension"])
        fake_base.vectors = {int(k): [float(x) for x in v] for k, v in payload["vectors"].items()}
        return FakeIDMap(fake_base)

    fake_module = SimpleNamespace(
        IndexFlatL2=FakeIndex, 
        IndexIDMap=FakeIDMap,
        write_index=write_index, 
        read_index=read_index
    )
    monkeypatch.setattr(vector_db_manager, "faiss", fake_module)


def test_vector_manager_creates_persists_and_searches(tmp_path: Path, monkeypatch) -> None:
    _install_fake_faiss(monkeypatch, tmp_path)
    manager = VectorDBManager(dimension=3, data_dir=tmp_path)
    manager.initialize_index()
    manager.add_vectors([[0.0, 0.0, 0.0]], [1])
    manager.save_index()
    assert (tmp_path / "zoterorag.faiss").exists()

    # Simulate a new process loading the index
    _install_fake_faiss(monkeypatch, tmp_path)
    manager_reloaded = VectorDBManager(dimension=3, data_dir=tmp_path)
    manager_reloaded.load_index()
    distances, ids = manager_reloaded.search([0.0, 0.0, 0.0], k=1)
    assert ids[0] == 1
    assert distances[0] == 0.0
