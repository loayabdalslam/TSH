import asyncio
from tsh import get_default_agent
from dotenv import load_dotenv

load_dotenv()

async def main():
    # Get the pre-configured agent with all tools
    agent = get_default_agent()

    print("--- TSH Library Usage Example ---")

    # Run a simple task
    task = "Hello! Tell me about the files in this directory."
    print(f"Task: {task}\n")

    response = await agent.run(task)

    print(f"\nTSH Response:\n{response}")

if __name__ == "__main__":
    asyncio.run(main())
