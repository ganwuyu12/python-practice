import json
from client import chat

REQUIRED_KEYS = {"name", "gender", "birth_year", "email"}


def parse_json(reply: str) -> dict:
    text = reply.strip()

    # 剥代码块
    if text.startswith("```"):
        if text.startswith("```json"):
            text = text[len("```json"):].strip()
        if text.endswith("```"):
            text = text[:-len("```")].strip()

    # 取第一个 { 到最后一个 } 之间
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1:
        text = text[start:end+1]

    return json.loads(text)


def validate(data: dict) -> None:
    missing = REQUIRED_KEYS - data.keys()
    if missing:
        raise ValueError(f"缺少字段或字段名不对: {missing}")


def extract_with_retry(text: str, max_retries: int = 3) -> dict:
    messages = [
        {"role": "user", "content": f"""从下面文本提取信息，严格输出纯 JSON，不要任何解释、不要用代码块包裹。
要求的字段（key 必须用英文）：
- name: 姓名
- gender: 性别
- birth_year: 出生年份（整数）
- email: 邮箱

文本：{text}"""}
    ]

    for attempt in range(max_retries):
        reply = chat(messages)
        try:
            data = parse_json(reply)
            validate(data)
            return data
        except (json.JSONDecodeError, ValueError) as e:
            messages.append({"role": "assistant", "content": reply})
            messages.append({"role": "user", "content": f"你上次输出有问题：{e}。请只输出纯 JSON，字段名必须用英文 name/gender/birth_year/email。"})

    raise ValueError("多次重试仍无法解析")


if __name__ == '__main__':
    text = "张三，男，1990年出生，邮箱 zhang@example.com"
    result = extract_with_retry(text)
    print("提取结果:", result)
    print("name:", result["name"])