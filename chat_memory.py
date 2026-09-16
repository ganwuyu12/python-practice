import os
import sys
import time
import requests
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("DEEPSEEK_API_KEY")

messages = []
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
            break
        reply = ask(user_input)
        print(f"AI: {reply}")