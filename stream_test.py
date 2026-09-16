import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("DEEPSEEK_API_KEY")

url = "https://api.deepseek.com/chat/completions"
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}
data = {
    "model": "deepseek-chat",
    "messages": [{"role": "user", "content": "你好"}],
    "stream": True
}

response = requests.post(url, headers=headers, json=data, stream=True)
for line in response.iter_lines():
    if not line:
        continue
    text = line.decode('utf-8')
    if not text.startswith('data: '):
        continue
    payload = text[6:]
    if payload == '[DONE]':
        break
    chunk = json.loads(payload)
    if 'choices' in chunk and len(chunk['choices']) > 0:
        delta = chunk['choices'][0]['delta']
        if 'content' in delta:
            print(delta['content'], end='', flush=True)