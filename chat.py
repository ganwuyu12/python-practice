import os
import sys
import requests
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("DEEPSEEK_API_KEY")

def ask(prompt):
    url = "https://api.deepseek.com/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        response_dict = response.json()
        return response_dict['choices'][0]['message']['content']
    except requests.RequestException as e:
        return f"请求失败: {e}"
    response = requests.post(url, headers=headers, json=data)
    response_dict = response.json()
    return response_dict['choices'][0]['message']['content']

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("用法: python chat.py \"你的问题\"")
        sys.exit(1)
    prompt = sys.argv[1]
    reply = ask(prompt)
    print(reply)