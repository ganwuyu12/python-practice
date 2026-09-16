import json
from pathlib import Path
from client import chat

HISTORY_FILE = Path("chat_history.json")
messages = []

if HISTORY_FILE.exists() and HISTORY_FILE.stat().st_size > 0:
    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        messages = json.load(f)

def main():
    while True:
        user_input = input("你: ")
        if user_input == "exit":
            with open(HISTORY_FILE, "w", encoding="utf-8") as f:
                json.dump(messages, f, ensure_ascii=False, indent=2)
            break
        messages.append({"role": "user", "content": user_input})
        reply = chat(messages)
        messages.append({"role": "assistant", "content": reply})
        print(f"AI: {reply}")

if __name__ == '__main__':
    main()