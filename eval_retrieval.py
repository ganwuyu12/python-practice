import json
from rag_search import search

with open("questions.json", "r", encoding="utf-8") as f:
    questions = json.load(f)

K = 3
hits = 0

for q in questions:
    results = search(q["question"], top_k=K)
    sources = [r["source"] for r in results]
    hit = q["expected_source"] in sources
    hits += hit
    print(f"{'✅' if hit else '❌'} {q['question']}")
    print(f"   期望: {q['expected_source']}")
    print(f"   实际: {sources}")

print(f"\nHitRate@{K}: {hits}/{len(questions)} = {hits/len(questions):.0%}")