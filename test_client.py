from client import chat

messages = [{"role": "user", "content": "你好"}]
reply = chat(messages)
print(reply)