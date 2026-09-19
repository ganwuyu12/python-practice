import json
import logging
from pathlib import Path
from client import chat,LLMError

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    filename="app.log",
    encoding="utf-8",
)

HISTORY_FILE = Path("chat_history.json")

def load_history(path: Path) -> list:
    if not path.exists() or path.stat().st_size == 0:
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def main():
    messages = load_history(HISTORY_FILE)
    while True:
        user_input = input("你: ")
        if user_input == "exit":
            with open(HISTORY_FILE, "w", encoding="utf-8") as f:
                json.dump(messages, f, ensure_ascii=False, indent=2)
            break
        messages.append({"role": "user", "content": user_input})
        try:
            reply = chat(messages)
        except LLMError as e:
            print(f"Error: {e}")
            messages.pop()
            continue
        messages.append({"role": "assistant", "content": reply})
        print(f"AI: {reply}")

if __name__ == '__main__':
    main()