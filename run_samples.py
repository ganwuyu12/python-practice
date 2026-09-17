import json
from extract import extract_with_retry

with open("samples.json", "r", encoding="utf-8") as f:
    samples = json.load(f)

for version in ("A", "B"):
    success = 0
    for text in samples:
        try:
            extract_with_retry(text, version=version)
            success += 1
        except Exception:
            pass
    print(f"版本 {version}: {success}/{len(samples)} 成功")