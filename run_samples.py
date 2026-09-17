import json
from extract import extract_with_retry

with open("samples.json", "r", encoding="utf-8") as f:
    samples = json.load(f)

for i, text in enumerate(samples):
    print(f"--- 样本 {i+1} ---")
    print("输入:", text)
    try:
        result = extract_with_retry(text)
        print("输出:", result)
    except Exception as e:
        print("失败:", e)