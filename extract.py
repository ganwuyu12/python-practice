import json
from client import chat, LLMError

REQUIRED_KEYS = {"name", "gender", "birth_year", "email"}


def parse_json(reply: str) -> dict:
    text = reply.strip()

    if text.startswith("```"):
        if text.startswith("```json"):
            text = text[len("```json"):].strip()
        if text.endswith("```"):
            text = text[:-len("```")].strip()

    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1:
        text = text[start:end+1]

    return json.loads(text)


def validate(data: dict) -> None:
    missing = REQUIRED_KEYS - data.keys()
    if missing:
        raise ValueError(f"缺少字段或字段名不对: {missing}")

    if all(v is None for v in data.values()):
        raise ValueError("所有字段都是 None，提取失败")

    if data.get("gender") not in ("男", "女"):
        raise ValueError(f"gender 不合法: {data.get('gender')}")


def build_prompt(text: str, version: str) -> str:
    if version == "A":
        return f"""从下面文本提取信息，严格输出纯 JSON，不要任何解释、不要用代码块包裹。
要求的字段（key 必须用英文）：
- name: 姓名
- gender: 性别
- birth_year: 出生年份（整数）
- email: 邮箱

文本：{text}"""
    else:
        return f"""从下面文本提取人员信息，严格输出纯 JSON，不要任何解释、不要用代码块包裹。

示例：
输入：李明，男，1995年出生，邮箱 liming@test.com
输出：{{"name": "李明", "gender": "男", "birth_year": 1995, "email": "liming@test.com"}}

现在处理：
输入：{text}
输出："""


def extract_with_retry(text: str, version: str = "A", max_retries: int = 3) -> dict:
    messages = [{"role": "user", "content": build_prompt(text, version)}]

    for attempt in range(max_retries):
        try:
            reply = chat(messages)          
            data = parse_json(reply)
            validate(data)
            return data
        except LLMError:                   
            raise
        except (json.JSONDecodeError, ValueError) as e:
            messages.append({"role": "assistant", "content": reply})
            messages.append({"role": "user", "content": f"你上次输出有问题：{e}。请只输出纯 JSON..."})

    raise ValueError("多次重试仍无法解析")

if __name__ == '__main__':
    text = "张三，男，1990年出生，邮箱 zhang@example.com"
    result = extract_with_retry(text)
    print("提取结果:", result)
    print("name:", result["name"])