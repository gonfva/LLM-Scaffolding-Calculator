"""Tests for Phase 5 features: layout properties and button callbacks."""

from unittest.mock import MagicMock, patch

from anthropic.types import TextBlock, ToolUseBlock

from src.agent.claude_agent import ClaudeAgent
from src.agent.ui_state import UIState


def test_ui_element_layout_properties() -> None:
    """Test UIElement stores text properties without layout styling."""
    ui_state = UIState()
    ui_state.add_text("Hello", "text_1")

    state = ui_state.get_state()
    assert len(state["elements"]) == 1
    elem = state["elements"][0]
    assert elem["type"] == "text"
    assert elem["properties"]["content"] == "Hello"


def test_button_with_callback_id() -> None:
    """Test button element stores callback_id."""
    ui_state = UIState()
    ui_state.add_button("Click me", "btn_1", "on_click")

    state = ui_state.get_state()
    assert len(state["elements"]) == 1
    elem = state["elements"][0]
    assert elem["type"] == "button"
    assert elem["properties"]["label"] == "Click me"
    assert elem["properties"]["callback_id"] == "on_click"


def test_container_creation() -> None:
    """Test container element with flex layout."""
    ui_state = UIState()
    ui_state.add_container("container_1", "row", justify_content="space-between", gap="10px")

    state = ui_state.get_state()
    assert len(state["elements"]) == 1
    elem = state["elements"][0]
    assert elem["type"] == "container"
    assert elem["layout"]["flex_direction"] == "row"
    assert elem["layout"]["justify_content"] == "space-between"
    assert elem["layout"]["gap"] == "10px"


def test_container_tool_execution() -> None:
    """Test create_container tool execution."""
    ui_state = UIState()

    from src.agent.tool_executor import ToolExecutor

    executor = ToolExecutor(ui_state)
    result = executor.execute_tool(
        "create_container",
        {"id": "cont_1", "flex_direction": "column", "gap": "8px"},
    )

    assert "successfully" in result
    state = ui_state.get_state()
    assert len(state["elements"]) == 1
    assert state["elements"][0]["type"] == "container"


def test_button_callback_id_in_tool() -> None:
    """Test create_button tool with callback_id."""
    ui_state = UIState()

    from src.agent.tool_executor import ToolExecutor

    executor = ToolExecutor(ui_state)
    result = executor.execute_tool(
        "create_button",
        {
            "label": "Submit",
            "id": "btn_submit",
            "callback_id": "on_submit",
        },
    )

    assert "successfully" in result
    state = ui_state.get_state()
    assert len(state["elements"]) == 1
    elem = state["elements"][0]
    assert elem["properties"]["callback_id"] == "on_submit"


def test_text_with_layout_properties() -> None:
    """Test display_text tool creates text element."""
    ui_state = UIState()

    from src.agent.tool_executor import ToolExecutor

    executor = ToolExecutor(ui_state)
    result = executor.execute_tool(
        "display_text",
        {
            "content": "Result: 42",
            "id": "result_text",
        },
    )

    assert "successfully" in result
    state = ui_state.get_state()
    elem = state["elements"][0]
    assert elem["type"] == "text"
    assert elem["properties"]["content"] == "Result: 42"


def test_agent_tool_use_with_layout() -> None:
    """Test agent handles tool use for creating buttons."""
    mock_tool_use = ToolUseBlock(
        type="tool_use",
        id="tool_123",
        name="create_button",
        input={
            "label": "Calculate",
            "id": "btn_1",
            "callback_id": "on_calculate",
        },
    )
    mock_text = TextBlock(type="text", text="Button created")

    mock_response_with_tool = MagicMock()
    mock_response_with_tool.content = [mock_tool_use, mock_text]

    # Second response should have no tools (to break the agentic loop)
    mock_text_final = TextBlock(type="text", text="All done!")
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

        # Verify response
        assert response == "All done!"

        # Verify UI state has button
        ui_state = agent.get_ui_state()
        assert len(ui_state["elements"]) == 1
        elem = ui_state["elements"][0]
        assert elem["type"] == "button"
        assert elem["properties"]["callback_id"] == "on_calculate"


def test_multiple_buttons_with_callbacks() -> None:
    """Test multiple buttons with different callbacks."""
    ui_state = UIState()

    from src.agent.tool_executor import ToolExecutor

    executor = ToolExecutor(ui_state)

    # Create multiple buttons
    executor.execute_tool(
        "create_button",
        {"label": "Add", "id": "btn_add", "callback_id": "on_add"},
    )
    executor.execute_tool(
        "create_button",
        {"label": "Subtract", "id": "btn_sub", "callback_id": "on_subtract"},
    )
    executor.execute_tool(
        "create_button",
        {"label": "Clear", "id": "btn_clr", "callback_id": "on_clear"},
    )

    state = ui_state.get_state()
    assert len(state["elements"]) == 3
    assert state["elements"][0]["properties"]["callback_id"] == "on_add"
    assert state["elements"][1]["properties"]["callback_id"] == "on_subtract"
    assert state["elements"][2]["properties"]["callback_id"] == "on_clear"


def test_container_with_row_layout() -> None:
    """Test container with row flex direction."""
    ui_state = UIState()

    from src.agent.tool_executor import ToolExecutor

    executor = ToolExecutor(ui_state)

    executor.execute_tool(
        "create_container",
        {
            "id": "button_row",
            "flex_direction": "row",
            "justify_content": "center",
            "gap": "5px",
        },
    )

    state = ui_state.get_state()
    elem = state["elements"][0]
    assert elem["layout"]["flex_direction"] == "row"
    assert elem["layout"]["justify_content"] == "center"
    assert elem["layout"]["gap"] == "5px"


def test_container_with_column_layout() -> None:
    """Test container with column flex direction."""
    ui_state = UIState()

    from src.agent.tool_executor import ToolExecutor

    executor = ToolExecutor(ui_state)

    executor.execute_tool(
        "create_container",
        {
            "id": "form_column",
            "flex_direction": "column",
            "justify_content": "flex-start",
            "gap": "12px",
        },
    )

    state = ui_state.get_state()
    elem = state["elements"][0]
    assert elem["layout"]["flex_direction"] == "column"
    assert elem["layout"]["justify_content"] == "flex-start"


def test_tool_definitions_have_layout_properties() -> None:
    """Verify tool definitions have correct properties."""
    from src.agent.tools import CREATE_BUTTON_TOOL, CREATE_CONTAINER_TOOL, DISPLAY_TEXT_TOOL

    # Check display_text has content and id
    assert "content" in DISPLAY_TEXT_TOOL["input_schema"]["properties"]
    assert "id" in DISPLAY_TEXT_TOOL["input_schema"]["properties"]

    # Check create_button has callback_id and label
    assert "callback_id" in CREATE_BUTTON_TOOL["input_schema"]["properties"]
    assert "callback_id" in CREATE_BUTTON_TOOL["input_schema"]["required"]
    assert "label" in CREATE_BUTTON_TOOL["input_schema"]["properties"]
    assert "label" in CREATE_BUTTON_TOOL["input_schema"]["required"]

    # Check create_container exists and has proper properties
    assert "flex_direction" in CREATE_CONTAINER_TOOL["input_schema"]["properties"]
    assert "justify_content" in CREATE_CONTAINER_TOOL["input_schema"]["properties"]
    assert "gap" in CREATE_CONTAINER_TOOL["input_schema"]["properties"]
