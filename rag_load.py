import json
import numpy as np
from pathlib import Path
from sentence_transformers import SentenceTransformer

DATA_DIR = Path("data/game_match_server")
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
OUTPUT_DIR = Path("data")


def load_and_split():
    chunks = []
    for f in DATA_DIR.iterdir():
        if not f.is_file():
            continue
        text = f.read_text(encoding="utf-8", errors="ignore")

        # 按空行切
        parts = text.split("\n\n")
        for part in parts:
            part = part.strip()
            if len(part) < 20:          # 太短的跳过
                continue
            chunks.append({"text": part, "source": f.name})

    return chunks

def main():
    chunks = load_and_split()
    print(f"切出 {len(chunks)} 块")

    model = SentenceTransformer("BAAI/bge-small-zh-v1.5")
    texts = [c["text"] for c in chunks]
    print("开始向量化...")
    vectors = model.encode(texts, show_progress_bar=True)
    print(f"向量化完成，形状: {vectors.shape}")

    # 存盘
    np.save(OUTPUT_DIR / "embeddings.npy", vectors)
    with open(OUTPUT_DIR / "chunks.json", "w", encoding="utf-8") as f:
        json.dump(chunks, f, ensure_ascii=False)
    print("已保存 embeddings.npy 和 chunks.json")


if __name__ == '__main__':
    main()