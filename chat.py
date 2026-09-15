import os
import sys
import time
import requests
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("DEEPSEEK_API_KEY")

def ask(prompt,max_retries=3):
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
    for attempt in range(max_retries):
        response = None
        try:
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            response_dict = response.json()
            return response_dict['choices'][0]['message']['content']
        except requests.RequestException as e:
            status =  response.status_code if response is not None else None
            if status is not None and 400 <= status < 500 and status != 429:
                return f"请求错误（不重试） : {e} 状态码: {status}"
            if attempt < max_retries - 1:
                wait = 2 ** attempt
                print(f"第 {attempt + 1} 次请求失败，错误: {e}. 正在等待 {wait} 秒后重试...")
                time.sleep(wait)  
            else:
                return f"请求失败: {e}. 已达到最大重试次数。"
    

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("用法: python chat.py \"你的问题\"")
        sys.exit(1)
    prompt = sys.argv[1]
    reply = ask(prompt)
    print(reply)