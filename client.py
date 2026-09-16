import time
import requests
import logging
from config import API_KEY, API_URL

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    filename="app.log",
    encoding="utf-8",
)


def chat(messages: list, max_retries: int = 3) -> str:
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "deepseek-chat",
        "messages": messages,
    }

    for attempt in range(max_retries):
        response = None
        try:
            response = requests.post(API_URL, headers=headers, json=data, timeout=30)
            response.raise_for_status()
            # TODO 1: 解析 JSON，取出回复文本，return
            response_dict =  response.json()
            return response_dict['choices'][0]['message']['content']
        except requests.RequestException as e:
            # TODO 2: 把 chat.py 里那套 4xx / 重试 / 超次数 逻辑搬过来
            status =  response.status_code if response is not None else None
            if status is not None and 400 <= status < 500 and status != 429:
                return f"请求错误（不重试） : {e} 状态码: {status}"
            if attempt < max_retries - 1:
                wait = 2 ** attempt
                logging.warning(f"第 {attempt + 1} 次请求失败，错误: {e}. 正在等待 {wait} 秒后重试...")
                time.sleep(wait)
            else:
                return f"请求失败: {e}. 已达到最大重试次数。"