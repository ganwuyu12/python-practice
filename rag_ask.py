from rag_search import search
from client import chat,LLMError

def build_rag_prompt(query: str, contexts: list) -> str:
    context_text = "\n\n".join(
        f"[来源: {c['source']}]\n{c['text']}" for c in contexts
    )
    return f"""基于以下资料回答问题。如果资料里没有答案，就说"资料中没有相关信息"。

资料：
{context_text}

问题：{query}
"""

def rag_ask(query: str, top_k: int = 3) -> str:
    contexts = search(query, top_k)
    prompt = build_rag_prompt(query, contexts)
    messages = [{"role": "user", "content": prompt}]
    return chat(messages)

if __name__ == '__main__':
    try:
        answer = rag_ask("匹配逻辑是怎么实现的？")
        print(answer)
    except LLMError as e:
        print(f"Error: {e}")