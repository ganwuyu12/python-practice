# Python 练习项目

## 这是什么
Python 学习过程中的工程实践：模块化的 LLM 对话工具 + 文件统计工具。

## 项目结构
- `main.py` — 主入口：多轮对话 + 持久化
- `client.py` — LLM 请求封装（重试、4xx 判断、日志）
- `config.py` — 配置（API key、URL）
- `chat.py` — 早期单文件版对话
- `chat_memory.py` — 多轮对话版
- `chat_persist.py` — 持久化版
- `stream_test.py` — 流式输出实验
- `tool.py` — 文件统计工具
- `test_calc.py`、`test_client.py`、`test_config.py` — 测试

## 怎么跑
1. 安装依赖：`pip install requests python-dotenv pytest`
2. 在根目录创建 `.env`，写入：`DEEPSEEK_API_KEY=你的key`
3. 运行：
   - 多轮对话：`python main.py`
   - 文件统计：`python tool.py .`
   - 跑测试：`pytest -v`

## 需要什么环境
- Python 3.10+
- DeepSeek API key（platform.deepseek.com 申请）
- `.env` 需自己创建，不包含在仓库里