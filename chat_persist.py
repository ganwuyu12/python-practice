import os
import sys
import time
import json
import requests
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()
api_key = os.getenv("DEEPSEEK_API_KEY")

HISTORY_FILE = Path("chat_history.json")

messages = []

if HISTORY_FILE.exists() and HISTORY_FILE.stat().st_size > 0:
    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        messages = json.load(f)

def ask(prompt):
    messages.append({"role": "user", "content": prompt})
    data = {
        "model": "deepseek-chat",
        "messages": messages,
    }
    url = "https://api.deepseek.com/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    response = requests.post(url, headers=headers, json=data)
    reply = response.json()['choices'][0]['message']['content']
    messages.append({"role": "assistant", "content": reply})
    return reply

if __name__ == '__main__':
    while True:
        user_input = input("你: ")
        if user_input == "exit":
            with open(HISTORY_FILE, "w", encoding="utf-8") as f:
                json.dump(messages, f, ensure_ascii=False, indent=2)
            break
        reply = ask(user_input)
        print(f"AI: {reply}")