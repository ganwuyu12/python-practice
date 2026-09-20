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
    retriever = Retriever(data_dir)
    hits = 0
    for q in questions:
        results = retriever.search(q["question"], top_k=K)
        sources = [r.source for r in results]
        if q["expected_source"] in sources:
            hits += 1
    print(f"{name}: {hits}/{len(questions)} = {hits/len(questions):.0%}")