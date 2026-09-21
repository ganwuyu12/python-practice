from sentence_transformers import CrossEncoder

model = CrossEncoder("BAAI/bge-reranker-base")

query = "匹配逻辑怎么实现的"
docs = [
    "void try_match() { ... }",
    "今天天气不错",
]
scores = model.predict([(query, d) for d in docs])
print(scores)