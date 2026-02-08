import os
import json
import asyncio
import pandas as pd
from typing import List, Dict, Any
from tsh.core.agent import Agent
from tsh.tools.file_tools import FileReadTool, ListDirTool, FileSearchTool
from tsh.tools.web_tools import WebSearchTool, WebFetchTool

class GAIABenchmark:
    def __init__(self, agent: Agent):
        self.agent = agent

    async def evaluate_task(self, task_description: str, expected_answer: str) -> Dict[str, Any]:
        print(f"Running GAIA Task: {task_description[:50]}...")
        result = await self.agent.run(task_description)

        # Simple string matching for evaluation (in real GAIA this is more complex)
        passed = expected_answer.lower() in result.lower()

        return {
            "task": task_description,
            "expected": expected_answer,
            "actual": result,
            "passed": passed
        }

    async def run_suite(self, tasks: List[Dict[str, str]]):
        results = []
        for task in tasks:
            res = await self.evaluate_task(task["question"], task["answer"])
            results.append(res)

        df = pd.DataFrame(results)
        print("\nGAIA Evaluation Results:")
        print(df[["task", "passed"]])
        print(f"\nPass Rate: {df['passed'].mean() * 100:.2f}%")
        return results

# Example setup for running benchmark
async def run_benchmark_example():
    tools = [FileReadTool(), ListDirTool(), FileSearchTool(), WebSearchTool()]
    agent = Agent(provider="anthropic", tools=tools)
    benchmark = GAIABenchmark(agent)

    gaia_tasks = [
        {"question": "What is the capital of France?", "answer": "Paris"},
        {"question": "Find the file named 'README.md' in the current directory and tell me its size.", "answer": "bytes"}
    ]

    await benchmark.run_suite(gaia_tasks)

if __name__ == "__main__":
    # asyncio.run(run_benchmark_example())
    pass
