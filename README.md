[![CI](https://github.com/ganwuyu12/python-practice/actions/workflows/ci.yml/badge.svg)](https://github.com/ganwuyu12/python-practice/actions/workflows/ci.yml)
# Python 练习项目

## 这是什么
Python 学习过程中的工程实践：模块化的 LLM 对话工具 + 信息抽取 + RAG 检索。

## 项目结构
- `main.py` — 主入口：多轮对话 + 持久化
- `client.py` — LLM 请求封装（重试、4xx 判断、日志）
- `config.py` — 配置（API key、URL）
- `extract.py` — 信息抽取（JSON 结构化输出 + 校验 + 重试）
- `rag_load.py` — RAG 索引构建（加载、切分、向量化）
- `rag_search.py` — RAG 检索
- `rag_ask.py` — RAG 问答
- `eval_retrieval.py` — 检索评测（HitRate@K）
- `tool.py` — 文件统计工具

## 怎么跑
1. 安装 [uv](https://docs.astral.sh/uv/)：`pip install uv`
2. 同步依赖：`uv sync`
3. 在根目录创建 `.env`，写入：`DEEPSEEK_API_KEY=你的key`
4. 运行：
   - 多轮对话：`uv run python main.py`
   - RAG 问答：`uv run python rag_ask.py`
   - 检索评测：`uv run python eval_retrieval.py`
   - 跑测试：`uv run pytest -v`

## 需要什么环境
- Python 3.10+
- DeepSeek API key（platform.deepseek.com 申请）
- `.env` 需自己创建，不包含在仓库里