import os
import pytest
from tsh.core.agent import Agent
from tsh.core.memory import Memory
from tsh.tools.file_tools import FileReadTool, FileWriteTool

def test_memory_creation():
    db_path = "test_memory.sql"
    if os.path.exists(db_path):
        os.remove(db_path)

    memory = Memory(db_path=db_path)
    session_id = "test_session"
    memory.create_session(session_id, "Test Session")

    memory.add_message(session_id, "user", "Hello TSH")
    history = memory.get_history(session_id)

    assert len(history) == 1
    assert history[0]["role"] == "user"
    assert history[0]["content"] == "Hello TSH"

    if os.path.exists(db_path):
        os.remove(db_path)

@pytest.mark.asyncio
async def test_agent_initialization():
    # Mocking provider for initialization test
    agent = Agent(provider="local", memory_db="test_agent.sql")
    assert agent.provider_name == "local"
    assert agent.session_id is not None

    if os.path.exists("test_agent.sql"):
        os.remove("test_agent.sql")

def test_skill_export():
    memory_db = "test_skill.sql"
    skill_file = "test_Skill.md"
    if os.path.exists(memory_db): os.remove(memory_db)
    if os.path.exists(skill_file): os.remove(skill_file)

    agent = Agent(provider="local", memory_db=memory_db)
    agent.memory.add_message(agent.session_id, "user", "Analyze this project")
    agent.memory.add_message(agent.session_id, "assistant", "Project analyzed.")

    agent.export_session_to_skill(skill_file)

    assert os.path.exists(skill_file)
    with open(skill_file, "r") as f:
        content = f.read()
        assert "Analyze this project" in content
        assert "Project analyzed" in content

    if os.path.exists(memory_db): os.remove(memory_db)
    if os.path.exists(skill_file): os.remove(skill_file)
