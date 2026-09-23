import json
from pathlib import Path
from client import chat_with_tools
from rag_search import Retriever
from read_file import read_file
from write_file import write_file
import logging

logger = logging.getLogger(__name__)

retriever = Retriever(Path("data/fixed"))
OUTPUT_DIR = Path("data/output")
MAX_TOKENS = 10000


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
    logger.info(f"开始执行代理，用户输入: {user_input}")
    messages = [{"role": "user", "content": user_input}]
    recent_calls: list[str] = []                              # 记录最近的调用签名
    total_tokens = 0

    for turn in range(max_turns):
        response = chat_with_tools(messages, TOOLS)
        message = response["choices"][0]["message"]
        usage = response["usage"]
        total_tokens += usage["total_tokens"]

        logger.info(f"第 {turn + 1} 轮对话，输入 {usage['prompt_tokens']} tokens, 输出 {usage['completion_tokens']} tokens, 总计 {usage['total_tokens']} tokens, 累计总费用: ¥{total_tokens * 0.02 / 1e6:.6f}")

        if total_tokens > MAX_TOKENS:
            logger.warning(f"达到 token 预算上限（{total_tokens}），已停止")
            return f"达到 token 预算上限（{total_tokens}），已停止"

        if not message.get("tool_calls"):
            logger.info(f"任务结束，总轮数={turn+1}，总 tokens={total_tokens}")
            return message["content"]

        messages.append(message)

        for call in message["tool_calls"]:
            name = call["function"]["name"]
            args = json.loads(call["function"]["arguments"])

            logger.info(f"[轮 {turn+1}] 调用工具 {name}, 参数 {args}")

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
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        filename="agent.log",
        encoding="utf-8",
    )
    answer = run_agent(
        "读一下 config.json 这个文件，告诉我它里面有什么配置"
    )
    print(answer)