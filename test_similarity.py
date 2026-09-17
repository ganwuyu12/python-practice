from sentence_transformers import SentenceTransformer
import numpy as np

model = SentenceTransformer("BAAI/bge-small-zh-v1.5")

texts = [
    "匹配逻辑怎么写",        # 查询
    "match 函数怎么实现",    # 意思相近
    "今天天气不错",          # 无关
]
vectors = model.encode(texts)

# 算余弦相似度
from numpy.linalg import norm
def cos_sim(a, b):
    return np.dot(a, b) / (norm(a) * norm(b))

print("相似  vs 相近句子:", cos_sim(vectors[0], vectors[1]))
print("相似  vs 无关句子:", cos_sim(vectors[0], vectors[2]))