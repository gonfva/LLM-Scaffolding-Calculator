"""Tests for ClaudeAgent class."""

from unittest.mock import MagicMock, patch

import pytest

from src.agent.claude_agent import ClaudeAgent


@pytest.fixture
def mock_anthropic_client() -> MagicMock:
    """Provide a mocked Anthropic client."""
    return MagicMock()


def test_claude_agent_initialization(mock_anthropic_client: MagicMock) -> None:
    """Test ClaudeAgent initialization."""
    with patch("src.agent.claude_agent.Anthropic", return_value=mock_anthropic_client):
        system_prompt = "Test prompt"
        agent = ClaudeAgent(system_prompt=system_prompt, api_key="test-key")

        assert agent.system_prompt == system_prompt
        assert agent.conversation_history == []


def test_claude_agent_welcome_message(mock_anthropic_client: MagicMock) -> None:
    """Test ClaudeAgent sends welcome message."""
    with patch("src.agent.claude_agent.Anthropic", return_value=mock_anthropic_client):
        agent = ClaudeAgent(system_prompt="Test", api_key="test-key")
        welcome = agent.send_welcome_message()

        assert isinstance(welcome, str)
        assert "Welcome" in welcome
        assert "Claude" in welcome


def test_claude_agent_process_message(mock_anthropic_client: MagicMock) -> None:
    """Test ClaudeAgent processes messages through Claude."""
    # Mock Claude response with TextBlock
    from anthropic.types import TextBlock

    mock_text_block = TextBlock(type="text", text="Claude's response")
    mock_response = MagicMock()
    mock_response.content = [mock_text_block]
    mock_anthropic_client.messages.create.return_value = mock_response

    with patch("src.agent.claude_agent.Anthropic", return_value=mock_anthropic_client):
        agent = ClaudeAgent(system_prompt="Test", api_key="test-key")

        response = agent.process_message("Hello Claude")

        assert response == "Claude's response"
        # Verify conversation history was updated
        assert len(agent.conversation_history) == 2
        assert agent.conversation_history[0]["role"] == "user"
        assert agent.conversation_history[1]["role"] == "assistant"


def test_claude_agent_maintains_context(
    mock_anthropic_client: MagicMock,
) -> None:
    """Test ClaudeAgent maintains conversation context."""
    # Mock multiple Claude responses
    from anthropic.types import TextBlock

    text_block1 = TextBlock(type="text", text="First response")
    response1 = MagicMock()
    response1.content = [text_block1]

    text_block2 = TextBlock(type="text", text="Second response")
    response2 = MagicMock()
    response2.content = [text_block2]

    mock_anthropic_client.messages.create.side_effect = [response1, response2]

    with patch("src.agent.claude_agent.Anthropic", return_value=mock_anthropic_client):
        agent = ClaudeAgent(system_prompt="Test", api_key="test-key")

        agent.process_message("First message")
        agent.process_message("Second message")

        # Verify conversation history has 4 messages (2 user, 2 assistant)
        assert len(agent.conversation_history) == 4
        assert agent.conversation_history[0]["content"] == "First message"
        assert agent.conversation_history[2]["content"] == "Second message"
