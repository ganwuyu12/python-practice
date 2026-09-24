[![CI](https://github.com/ganwuyu12/python-practice/actions/workflows/ci.yml/badge.svg)](https://github.com/ganwuyu12/python-practice/actions/workflows/ci.yml)
# Python 练习项目

## 这是什么
Python 学习过程中的工程实践：模块化的 LLM 对话工具 + 信息抽取 + RAG 检索 + 手写 Agent 运行时。

## 项目结构

### 核心
- `client.py` — LLM 请求封装（重试、4xx 判断、日志、工具调用）
- `config.py` — 配置（API key、URL）
- `main.py` — 多轮对话入口（持久化）

### 信息抽取
- `extract.py` — 结构化输出（JSON 校验 + 失败回灌重试）

### RAG
- `rag_load.py` — 索引构建（加载、切分、向量化、文件摘要）
- `rag_search.py` — 检索（延迟加载 + rerank）
- `rag_ask.py` — RAG 问答
- `eval_retrieval.py` — 检索评测（HitRate@K）

### Agent
- `my_agent.py` — 手写 ReAct 循环（工具注册、失败回灌、循环终止、token 预算、追踪日志）
- `eval_agent.py` — Agent 评测（多步任务完成率）

### 其它
- `tool.py` — 文件统计工具

## 怎么跑
1. 安装 [uv](https://docs.astral.sh/uv/)：`pip install uv`
2. 同步依赖：`uv sync`
3. 在根目录创建 `.env`，写入：`DEEPSEEK_API_KEY=你的key`
4. 运行：
   - 多轮对话：`uv run python main.py`
   - RAG 问答：`uv run python rag_ask.py`
   - Agent：`uv run python my_agent.py`
   - 检索评测：`uv run python eval_retrieval.py`
   - Agent 评测：`uv run python eval_agent.py`
   - 跑测试：`uv run pytest -v`

## 需要什么环境
- Python 3.10+
- DeepSeek API key（platform.deepseek.com 申请）
- `.env` 需自己创建，不包含在仓库里

## 文档
- [RAG 检索优化记录](RAG_OPTIMIZATION.md) — HitRate@3 从 70% 提升到 97%
- [Agent 评测报告](AGENT_EVAL.md) — 多步任务完成率从 60% 提升到 90%