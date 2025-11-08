"""Tests for agent tool use functionality."""

from unittest.mock import MagicMock, patch

from anthropic.types import TextBlock, ToolUseBlock

from src.agent.claude_agent import ClaudeAgent


def test_agent_handles_tool_use() -> None:
    """Test agent processes tool use blocks from Claude."""
    # Mock Claude's first response with tool use, second with no tools
    mock_tool_use = ToolUseBlock(
        type="tool_use",
        id="tool_123",
        name="display_text",
        input={"content": "Hello", "id": "text_1"},
    )
    mock_text_with_tool = TextBlock(type="text", text="I've displayed the text")

    mock_response_with_tool = MagicMock()
    mock_response_with_tool.content = [mock_tool_use, mock_text_with_tool]

    # Second response (after tool execution) should have no tools
    mock_text_final = TextBlock(type="text", text="All done!")
    mock_response_final = MagicMock()
    mock_response_final.content = [mock_text_final]

    with patch("src.agent.claude_agent.Anthropic") as mock_anthropic:
        mock_client = MagicMock()
        mock_anthropic.return_value = mock_client
        # First call returns tool use, second call returns final response
        mock_client.messages.create.side_effect = [
            mock_response_with_tool,
            mock_response_final,
        ]

        agent = ClaudeAgent(system_prompt="Test", api_key="test-key")
        response = agent.process_message("Display hello")

        # Verify response
        assert response == "All done!"

        # Verify UI state was updated
        ui_state = agent.get_ui_state()
        assert len(ui_state["elements"]) == 1
        assert ui_state["elements"][0]["type"] == "text"
        assert ui_state["elements"][0]["properties"]["content"] == "Hello"


def test_agent_conversation_history_format_with_tools() -> None:
    """Test conversation history is properly formatted for tool use."""
    mock_tool_use = ToolUseBlock(
        type="tool_use",
        id="tool_123",
        name="display_text",
        input={"content": "Hello", "id": "text_1"},
    )
    mock_text = TextBlock(type="text", text="Done")

    mock_response = MagicMock()
    mock_response.content = [mock_tool_use, mock_text]

    with patch("src.agent.claude_agent.Anthropic") as mock_anthropic:
        mock_client = MagicMock()
        mock_anthropic.return_value = mock_client
        mock_client.messages.create.return_value = mock_response

        agent = ClaudeAgent(system_prompt="Test", api_key="test-key")
        agent.process_message("Create UI")

        # Verify conversation history structure
        history = agent.conversation_history
        assert len(history) >= 3  # user, assistant (with tool), user (with tool_result)

        # Find the tool_result message
        tool_result_msg = None
        for msg in history:
            if msg["role"] == "user" and isinstance(msg["content"], list):
                for content_block in msg["content"]:
                    if (
                        isinstance(content_block, dict)
                        and content_block.get("type") == "tool_result"
                    ):
                        tool_result_msg = msg
                        break

        assert tool_result_msg is not None, "tool_result message not found in history"

        # Verify tool_result has required fields
        tool_result = tool_result_msg["content"][0]
        assert "tool_use_id" in tool_result
        assert "content" in tool_result
        assert tool_result["tool_use_id"] == "tool_123"
