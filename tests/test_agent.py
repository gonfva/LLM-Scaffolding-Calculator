"""Tests for Agent class."""

from src.agent.agent import Agent


def test_agent_initialization() -> None:
    """Test agent initialization with system prompt."""
    system_prompt = "Test prompt"
    agent = Agent(system_prompt=system_prompt)
    assert agent.system_prompt == system_prompt


def test_agent_process_message() -> None:
    """Test agent processes messages."""
    agent = Agent(system_prompt="Test prompt")
    input_msg = "Hello agent"
    response = agent.process_message(input_msg)
    assert response == f"Echo: {input_msg}"


def test_agent_welcome_message() -> None:
    """Test agent sends welcome message on connection."""
    agent = Agent(system_prompt="Test prompt")
    welcome = agent.send_welcome_message()
    assert isinstance(welcome, str)
    assert len(welcome) > 0
    assert "Welcome" in welcome or "welcome" in welcome.lower()
