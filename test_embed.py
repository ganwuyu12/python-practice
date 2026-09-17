from sentence_transformers import SentenceTransformer

model = SentenceTransformer("BAAI/bge-small-zh-v1.5")

texts = ["匹配逻辑怎么写", "match 函数实现", "今天天气不错"]
vectors = model.encode(texts)

print("向量数量:", len(vectors))
print("每个向量维度:", len(vectors[0]))
print("第一个向量的前 5 个数:", vectors[0][:5])