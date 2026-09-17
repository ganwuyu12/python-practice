import json
import numpy as np
from pathlib import Path
from sentence_transformers import SentenceTransformer

DATA_DIR = Path("data")

# 加载存好的数据
vectors = np.load(DATA_DIR / "embeddings.npy")
with open(DATA_DIR / "chunks.json", "r", encoding="utf-8") as f:
    chunks = json.load(f)

model = SentenceTransformer("BAAI/bge-small-zh-v1.5")


def search(query: str, top_k: int = 3):
    query_vector = model.encode(query)

    query_norm = query_vector / np.linalg.norm(query_vector)
    vectors_norm = vectors / np.linalg.norm(vectors, axis=1, keepdims=True)
    similarities = vectors_norm @ query_norm

    top_indices = np.argsort(similarities)[::-1][:top_k]
    return [chunks[i] for i in top_indices]

if __name__ == '__main__':
    results = search("匹配逻辑怎么实现的")
    for r in results:
        print(f"来源: {r['source']}")
        print(f"内容: {r['text'][:100]}...")
        print("---")