import json
from pathlib import Path
from client import chat_with_tools
from rag_search import Retriever
from read_file import read_file
from write_file import write_file

retriever = Retriever(Path("data/fixed"))
OUTPUT_DIR = Path("data/output")


def search_docs(query: str) -> str:
    """搜索本地文档"""
    hits = retriever.search(query, top_k=3)
    if not hits:
        return "没有找到相关文档"
    return "\n\n".join(f"[来源: {h.source}]\n{h.text}" for h in hits)


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_docs",
            "description": "搜索本地算法题解文档，回答关于题解内容的问题时使用",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "搜索关键词或问题"
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "读取指定文件的完整内容，需要查看文件源码时使用",
            "parameters": {
                "type": "object",
                "properties": {
                    "filename": {
                        "type": "string",
                        "description": "要读取的文件名，例如 match_server.cpp"
                    }
                },
                "required": ["filename"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "写入文件，将内容写入到指定的文件中",
            "parameters": {
                "type": "object",
                "properties": {
                    "filename": {
                        "type": "string",
                        "description": "要写入的文件名"
                    },
                    "content": {
                        "type": "string",
                        "description": "要写入的内容"
                    }
                },
                "required": ["filename", "content"]
            }
        }
    }
]


def run_agent(user_input: str, max_turns: int = 8) -> str:
    messages = [{"role": "user", "content": user_input}]
    recent_calls = []                              # 记录最近的调用签名

    for turn in range(max_turns):
        message = chat_with_tools(messages, TOOLS)

        if not message.get("tool_calls"):
            return message["content"]

        messages.append(message)

        for call in message["tool_calls"]:
            name = call["function"]["name"]
            args = json.loads(call["function"]["arguments"])

            # 生成签名：工具名 + 排序后的参数
            signature = f"{name}:{json.dumps(args, sort_keys=True)}"

            # 检查：这个签名在 recent_calls 里出现 3 次以上？
            if recent_calls.count(signature) >= 3:
                messages.append({
                    "role": "user",
                    "content": "你已经重复调用同一个工具多次，请换一种方式，或直接给出最终答案。"
                })
                continue                          # 跳过这次工具执行

            # 执行工具
            if name == "search_docs":
                result = search_docs(**args)
            elif name == "read_file":
                result = read_file(**args)
            elif name == "write_file":
                result = write_file(**args)
            else:
                result = f"未知工具: {name}"

            # 把结果和签名记录
            messages.append({
                "role": "tool",
                "tool_call_id": call["id"],
                "content": result,
            })
            recent_calls.append(signature)

    return "达到最大轮数"

if __name__ == '__main__':
    answer = run_agent(
        "读一下 config.json 这个文件，告诉我它里面有什么配置"
    )
    print(answer)