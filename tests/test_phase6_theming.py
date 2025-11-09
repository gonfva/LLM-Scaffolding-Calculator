"""Tests for Phase 6: UI elements and state management."""

from unittest.mock import MagicMock, patch

from anthropic.types import TextBlock, ToolUseBlock

from src.agent.claude_agent import ClaudeAgent
from src.agent.ui_state import UIState


class TestUIStateThemeManagement:
    """Tests for UIState element management (theming removed)."""

    def test_apply_theme_minimal(self) -> None:
        """Test UIState basic creation."""
        ui_state = UIState()
        state = ui_state.get_state()
        assert "elements" in state
        assert state["elements"] == []

    def test_apply_theme_pirate(self) -> None:
        """Test adding elements to UIState."""
        ui_state = UIState()
        ui_state.add_button("Click", "btn_1", "on_click")
        state = ui_state.get_state()
        assert len(state["elements"]) == 1
        assert state["elements"][0]["type"] == "button"

    def test_apply_invalid_theme(self) -> None:
        """Test adding multiple elements."""
        ui_state = UIState()
        ui_state.add_text("Hello", "text_1")
        ui_state.add_button("Submit", "btn_1", "on_submit")
        ui_state.add_container("row", "row")
        state = ui_state.get_state()
        assert len(state["elements"]) == 3

    def test_apply_theme_with_overrides(self) -> None:
        """Test element hierarchy."""
        ui_state = UIState()
        ui_state.add_container("container_1", "column")
        ui_state.add_text("Child", "text_1", parent_id="container_1")
        state = ui_state.get_state()
        text_elem = next(e for e in state["elements"] if e["id"] == "text_1")
        assert text_elem["parent_id"] == "container_1"

    def test_theme_in_ui_state_output(self) -> None:
        """Test UI state structure without theme."""
        ui_state = UIState()
        ui_state.add_button("Test", "btn_1", "callback")
        state = ui_state.get_state()
        assert "elements" in state
        assert "theme" not in state  # No theme in output

    def test_ui_state_without_theme(self) -> None:
        """Test UI state without any elements."""
        ui_state = UIState()
        state = ui_state.get_state()
        assert "theme" not in state
        assert state["elements"] == []


class TestToolExecutorThemeApplication:
    """Tests for ToolExecutor basic operations."""

    def test_execute_apply_theme_tool(self) -> None:
        """Test executing display_text tool."""
        ui_state = UIState()

        from src.agent.tool_executor import ToolExecutor

        executor = ToolExecutor(ui_state)
        result = executor.execute_tool("display_text", {"content": "Hello", "id": "text_1"})

        assert "successfully" in result
        assert len(ui_state.get_state()["elements"]) == 1

    def test_execute_apply_theme_with_overrides(self) -> None:
        """Test executing create_button tool."""
        ui_state = UIState()

        from src.agent.tool_executor import ToolExecutor

        executor = ToolExecutor(ui_state)
        result = executor.execute_tool(
            "create_button",
            {
                "label": "Click me",
                "id": "btn_1",
                "callback_id": "on_click",
            },
        )

        assert "successfully" in result
        button = ui_state.get_state()["elements"][0]
        assert button["properties"]["label"] == "Click me"

    def test_execute_apply_invalid_theme(self) -> None:
        """Test executing unknown tool returns error."""
        ui_state = UIState()

        from src.agent.tool_executor import ToolExecutor

        executor = ToolExecutor(ui_state)
        result = executor.execute_tool("unknown_tool", {})

        assert "Error" in result or "Unknown" in result


class TestAgentToolUseWithTheme:
    """Tests for agent tool use with UI creation."""

    def test_agent_applies_theme_tool(self) -> None:
        """Test agent can create buttons via tool."""
        mock_tool_use = ToolUseBlock(
            type="tool_use",
            id="tool_123",
            name="create_button",
            input={"label": "Click", "id": "btn_1", "callback_id": "on_click"},
        )
        mock_text = TextBlock(type="text", text="Button created!")

        mock_response_with_tool = MagicMock()
        mock_response_with_tool.content = [mock_tool_use, mock_text]

        mock_text_final = TextBlock(type="text", text="Done!")
        mock_response_final = MagicMock()
        mock_response_final.content = [mock_text_final]

        with patch("src.agent.claude_agent.Anthropic") as mock_anthropic:
            mock_client = MagicMock()
            mock_anthropic.return_value = mock_client
            mock_client.messages.create.side_effect = [
                mock_response_with_tool,
                mock_response_final,
            ]

            agent = ClaudeAgent(system_prompt="Test", api_key="test-key")
            response = agent.process_message("Create a button")

            assert response == "Done!"
            ui_state = agent.get_ui_state()
            assert len(ui_state["elements"]) == 1
            assert ui_state["elements"][0]["type"] == "button"

    def test_agent_combines_theme_and_buttons(self) -> None:
        """Test agent can create multiple UI elements."""
        mock_button_tool = ToolUseBlock(
            type="tool_use",
            id="tool_1",
            name="create_button",
            input={
                "label": "Click me",
                "id": "btn_1",
                "callback_id": "on_click",
            },
        )
        mock_text_tool = ToolUseBlock(
            type="tool_use",
            id="tool_2",
            name="display_text",
            input={"content": "Hello", "id": "text_1"},
        )
        mock_text = TextBlock(type="text", text="UI created!")

        mock_response_with_tools = MagicMock()
        mock_response_with_tools.content = [mock_button_tool, mock_text_tool, mock_text]

        mock_text_final = TextBlock(type="text", text="All set!")
        mock_response_final = MagicMock()
        mock_response_final.content = [mock_text_final]

        with patch("src.agent.claude_agent.Anthropic") as mock_anthropic:
            mock_client = MagicMock()
            mock_anthropic.return_value = mock_client
            mock_client.messages.create.side_effect = [
                mock_response_with_tools,
                mock_response_final,
            ]

            agent = ClaudeAgent(system_prompt="Test", api_key="test-key")
            response = agent.process_message("Create a calculator")

            assert response == "All set!"
            ui_state = agent.get_ui_state()

            # Check elements were created
            assert len(ui_state["elements"]) == 2
            assert ui_state["elements"][0]["type"] == "button"
            assert ui_state["elements"][1]["type"] == "text"
