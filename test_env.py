import os
from dotenv import load_dotenv

load_dotenv()
key = os.getenv("DEEPSEEK_API_KEY")

if key:
    print("key 读取成功")
else:
    print("key 没读到，检查 .env")