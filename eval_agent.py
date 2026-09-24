import json
from my_agent import run_agent

with open("agent_tasks.json", "r", encoding="utf-8") as f:
    tasks = json.load(f)

for i, task in enumerate(tasks):
    print(f"\n{'='*60}")
    print(f"任务 {i+1}: {task['question']}")
    print('='*60)
    answer = run_agent(task["question"])
    print(f"\n回答:\n{answer[:400]}...")