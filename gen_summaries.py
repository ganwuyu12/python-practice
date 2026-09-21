import json
from pathlib import Path
from client import chat

DATA_DIR = Path("data/game_match_server")
OUTPUT = Path("data/summaries.json")

def summarize(filename: str, content: str) -> str:
    # TODO: 调 chat，让它总结这个文件的作用
    prompt = f"""用一段话（100字以内）总结这个文件的作用：

文件名：{filename}
内容：
{content[:3000]}
"""
    messages = [{"role": "user", "content": prompt}]
    return chat(messages)

def main():
    summaries = {}
    for f in DATA_DIR.iterdir():
        if not f.is_file():
            continue
        content = f.read_text(encoding="utf-8", errors="ignore")
        print(f"总结 {f.name}...")
        summaries[f.name] = summarize(f.name, content)

    OUTPUT.write_text(json.dumps(summaries, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"已保存 {len(summaries)} 个摘要到 {OUTPUT}")

if __name__ == '__main__':
    main()