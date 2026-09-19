import json
from dataclasses import dataclass
from pathlib import Path
import numpy as np
from sentence_transformers import SentenceTransformer


@dataclass
class Hit:
    text: str
    source: str
    score: float


class Retriever:
    def __init__(self, data_dir: Path, model_name: str = "BAAI/bge-small-zh-v1.5") -> None:
        self.data_dir = data_dir
        self.model_name = model_name
        self._model = None
        self._vectors = None
        self._chunks = None

    @property
    def model(self):
        if self._model is None:
            self._model = SentenceTransformer(self.model_name)
        return self._model

    def _ensure_loaded(self) -> None:
        if self._vectors is None:
            vectors = np.load(self.data_dir / "embeddings.npy")
            self._vectors = vectors / np.linalg.norm(vectors, axis=1, keepdims=True)
            self._chunks = json.loads(
                (self.data_dir / "chunks.json").read_text(encoding="utf-8")
            )

    def search(self, query: str, top_k: int = 3) -> list[Hit]:
        self._ensure_loaded()
        assert self._vectors is not None
        assert self._chunks is not None
        q = self.model.encode(query)
        q = q / np.linalg.norm(q)
        sims = self._vectors @ q
        idx = np.argsort(sims)[::-1][:top_k]
        return [
            Hit(
                text=self._chunks[i]["text"],
                source=self._chunks[i]["source"],
                score=float(sims[i]),
            )
            for i in idx
        ]


if __name__ == '__main__':
    retriever = Retriever(Path("data"))
    results = retriever.search("匹配逻辑怎么实现的")
    for r in results:
        print(f"[{r.score:.3f}] {r.source}")
        print(r.text[:100])
        print("---")