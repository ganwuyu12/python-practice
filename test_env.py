import os
from dotenv import load_dotenv

load_dotenv()                              # 从 .env 读进环境变量
key = os.getenv("DEEPSEEK_API_KEY")
print("key 读到了吗:", key is not None)
print("key 前 6 位:", key[:6] if key else "没读到")