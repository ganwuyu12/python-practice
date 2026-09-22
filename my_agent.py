import json
from pathlib import Path
from client import chat_with_tools
from rag_search import Retriever

retriever = Retriever(Path("data/fixed"))


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
                    "query": {"type": "string", "description": "搜索关键词或问题"}
                },
                "required": ["query"]
            }
        }
    }
]


def run_agent(user_input: str, max_turns: int = 8) -> str:
    messages = [{"role": "user", "content": user_input}]

    for turn in range(max_turns):
        message = chat_with_tools(messages, TOOLS)

        if not message.get("tool_calls"):
            return message["content"]

        messages.append(message)

        for call in message["tool_calls"]:
            name = call["function"]["name"]
            args = json.loads(call["function"]["arguments"])

            if name == "search_docs":
                result = search_docs(**args)
            else:
                result = f"未知工具: {name}"

            messages.append({
                "role": "tool",
                "tool_call_id": call["id"],
                "content": result,
            })

    return "达到最大轮数"


if __name__ == '__main__':
    answer = run_agent("帮我查一下 match_server.cpp 里的匹配逻辑")
    print(answer)