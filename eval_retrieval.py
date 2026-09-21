import json
from pathlib import Path
from rag_search import Retriever

with open("questions.json", "r", encoding="utf-8") as f:
    questions = json.load(f)

K = 3

for name, data_dir in [
    ("fixed", Path("data/fixed")),
    ("blank", Path("data/blank")),
    ("mixed", Path("data/mixed")),
]:
    for use_rerank in [False, True]:
        retriever = Retriever(data_dir, use_rerank=use_rerank)
        hits = 0
        for q in questions:
            results = retriever.search(q["question"], top_k=K)
            sources = [r.source for r in results]
            if q["expected_source"] in sources:
                hits += 1
        tag = "rerank" if use_rerank else "no-rerank"
        print(f"{name} [{tag}]: {hits}/{len(questions)} = {hits/len(questions):.0%}")