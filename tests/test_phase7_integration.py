"""Integration tests for Phase 7: Full calculator flow with nesting."""

from unittest.mock import MagicMock, patch

from anthropic.types import TextBlock, ToolUseBlock

from src.agent.claude_agent import ClaudeAgent


class TestCalculatorNested:
    """Integration tests for calculator with nested hierarchy."""

    def test_nested_calculator_ui_creation(self) -> None:
        """Test creating a complete calculator UI with proper nesting."""
        # Simulate Claude creating a nested calculator interface
        tools = [
            # Create root container
            ToolUseBlock(
                type="tool_use",
                id="tool_1",
                name="create_container",
                input={"id": "calc_root", "flex_direction": "column", "gap": "10px"},
            ),
            # Create display section
            ToolUseBlock(
                type="tool_use",
                id="tool_2",
                name="display_text",
                input={
                    "id": "display",
                    "content": "0",
                    "parent_id": "calc_root",
                    "width": "100%",
                },
            ),
            # Create button grid container
            ToolUseBlock(
                type="tool_use",
                id="tool_3",
                name="create_container",
                input={
                    "id": "button_grid",
                    "flex_direction": "row",
                    "parent_id": "calc_root",
                    "gap": "5px",
                },
            ),
            # Add buttons to grid
            ToolUseBlock(
                type="tool_use",
                id="tool_4",
                name="create_button",
                input={
                    "id": "btn_1",
                    "label": "1",
                    "callback_id": "digit_1",
                    "parent_id": "button_grid",
                    "flex_grow": 1,
                },
            ),
            ToolUseBlock(
                type="tool_use",
                id="tool_5",
                name="create_button",
                input={
                    "id": "btn_2",
                    "label": "2",
                    "callback_id": "digit_2",
                    "parent_id": "button_grid",
                    "flex_grow": 1,
                },
            ),
            ToolUseBlock(
                type="tool_use",
                id="tool_6",
                name="create_button",
                input={
                    "id": "btn_add",
                    "label": "+",
                    "callback_id": "op_add",
                    "parent_id": "button_grid",
                    "flex_grow": 1,
                },
            ),
        ]

        mock_text = TextBlock(type="text", text="Calculator ready")

        mock_response = MagicMock()
        mock_response.content = tools + [mock_text]

        mock_response_final = MagicMock()
        mock_response_final.content = [TextBlock(type="text", text="Ready")]

        with patch("src.agent.claude_agent.Anthropic") as mock_anthropic:
            mock_client = MagicMock()
            mock_anthropic.return_value = mock_client
            mock_client.messages.create.side_effect = [mock_response, mock_response_final]

            agent = ClaudeAgent(
                system_prompt="You are a calculator assistant", api_key="test-key"
            )
            agent.process_message("Create a calculator with buttons 1, 2 and +")

            ui_state = agent.get_ui_state()
            elements = ui_state["elements"]

            # Verify structure
            assert len(elements) == 6  # 2 containers + 1 display + 3 buttons

            # Check root container
            root = next(e for e in elements if e["id"] == "calc_root")
            assert root["type"] == "container"
            assert "parent_id" not in root or root.get("parent_id") is None

            # Check display is nested in root
            display = next(e for e in elements if e["id"] == "display")
            assert display["type"] == "text"
            assert display["parent_id"] == "calc_root"

            # Check button grid is nested in root
            grid = next(e for e in elements if e["id"] == "button_grid")
            assert grid["type"] == "container"
            assert grid["parent_id"] == "calc_root"

            # Check all buttons are nested in grid
            for btn_id in ["btn_1", "btn_2", "btn_add"]:
                btn = next(e for e in elements if e["id"] == btn_id)
                assert btn["type"] == "button"
                assert btn["parent_id"] == "button_grid"

    def test_calculator_display_update(self) -> None:
        """Test updating calculator display without creating new element."""
        # First create the calculator
        create_tools = [
            ToolUseBlock(
                type="tool_use",
                id="tool_1",
                name="create_container",
                input={"id": "calc", "flex_direction": "column"},
            ),
            ToolUseBlock(
                type="tool_use",
                id="tool_2",
                name="display_text",
                input={
                    "id": "result",
                    "content": "0",
                    "parent_id": "calc",
                },
            ),
        ]

        mock_response_create = MagicMock()
        mock_response_create.content = create_tools + [
            TextBlock(type="text", text="Calculator created")
        ]

        mock_response_create_final = MagicMock()
        mock_response_create_final.content = [TextBlock(type="text", text="Ready")]

        # Then update the display
        update_tools = [
            ToolUseBlock(
                type="tool_use",
                id="tool_3",
                name="update_element",
                input={"id": "result", "content": "42"},
            )
        ]

        mock_response_update = MagicMock()
        mock_response_update.content = update_tools + [
            TextBlock(type="text", text="Display updated")
        ]

        mock_response_update_final = MagicMock()
        mock_response_update_final.content = [TextBlock(type="text", text="Done")]

        with patch("src.agent.claude_agent.Anthropic") as mock_anthropic:
            mock_client = MagicMock()
            mock_anthropic.return_value = mock_client
            mock_client.messages.create.side_effect = [
                mock_response_create,
                mock_response_create_final,
                mock_response_update,
                mock_response_update_final,
            ]

            agent = ClaudeAgent(
                system_prompt="You are a calculator", api_key="test-key"
            )

            # Create calculator
            agent.process_message("Create calculator")
            ui_state_1 = agent.get_ui_state()
            assert len(ui_state_1["elements"]) == 2  # Container + display

            # Update display
            agent.process_message("Update display to 42")
            ui_state_2 = agent.get_ui_state()

            # Should still have 2 elements, not 3
            assert len(ui_state_2["elements"]) == 2
            display = next(e for e in ui_state_2["elements"] if e["id"] == "result")
            assert display["properties"]["content"] == "42"

    def test_complex_nested_layout(self) -> None:
        """Test complex nested layout with multiple levels."""
        tools = [
            # Root container
            ToolUseBlock(
                type="tool_use",
                id="tool_1",
                name="create_container",
                input={"id": "main", "flex_direction": "column", "gap": "20px"},
            ),
            # Header section
            ToolUseBlock(
                type="tool_use",
                id="tool_2",
                name="create_container",
                input={
                    "id": "header",
                    "flex_direction": "row",
                    "parent_id": "main",
                    "justify_content": "space-between",
                    "gap": "10px",
                },
            ),
            ToolUseBlock(
                type="tool_use",
                id="tool_3",
                name="display_text",
                input={"id": "title", "content": "Calculator", "parent_id": "header"},
            ),
            ToolUseBlock(
                type="tool_use",
                id="tool_4",
                name="create_button",
                input={
                    "id": "btn_settings",
                    "label": "⚙️",
                    "callback_id": "settings",
                    "parent_id": "header",
                },
            ),
            # Content section
            ToolUseBlock(
                type="tool_use",
                id="tool_5",
                name="create_container",
                input={
                    "id": "content",
                    "flex_direction": "column",
                    "parent_id": "main",
                    "gap": "15px",
                },
            ),
            # Display area
            ToolUseBlock(
                type="tool_use",
                id="tool_6",
                name="display_text",
                input={
                    "id": "display",
                    "content": "0",
                    "parent_id": "content",
                    "width": "100%",
                },
            ),
            # Controls area
            ToolUseBlock(
                type="tool_use",
                id="tool_7",
                name="create_container",
                input={
                    "id": "controls",
                    "flex_direction": "row",
                    "parent_id": "content",
                    "gap": "5px",
                },
            ),
            # Control buttons
            ToolUseBlock(
                type="tool_use",
                id="tool_8",
                name="create_button",
                input={
                    "id": "btn_clear",
                    "label": "C",
                    "callback_id": "clear",
                    "parent_id": "controls",
                    "flex_grow": 1,
                },
            ),
            ToolUseBlock(
                type="tool_use",
                id="tool_9",
                name="create_button",
                input={
                    "id": "btn_equals",
                    "label": "=",
                    "callback_id": "equals",
                    "parent_id": "controls",
                    "flex_grow": 1,
                },
            ),
        ]

        mock_response = MagicMock()
        mock_response.content = tools + [TextBlock(type="text", text="Layout created")]

        mock_response_final = MagicMock()
        mock_response_final.content = [TextBlock(type="text", text="Done")]

        with patch("src.agent.claude_agent.Anthropic") as mock_anthropic:
            mock_client = MagicMock()
            mock_anthropic.return_value = mock_client
            mock_client.messages.create.side_effect = [mock_response, mock_response_final]

            agent = ClaudeAgent(
                system_prompt="You are a calculator assistant", api_key="test-key"
            )
            agent.process_message("Create a complex calculator layout")

            ui_state = agent.get_ui_state()
            elements = ui_state["elements"]

            # Verify total count: 4 containers + 5 elements = 9
            assert len(elements) == 9

            # Verify hierarchy
            main = next(e for e in elements if e["id"] == "main")
            assert "parent_id" not in main

            header = next(e for e in elements if e["id"] == "header")
            assert header["parent_id"] == "main"

            content = next(e for e in elements if e["id"] == "content")
            assert content["parent_id"] == "main"

            controls = next(e for e in elements if e["id"] == "controls")
            assert controls["parent_id"] == "content"

            # Check deeply nested button
            btn_equals = next(e for e in elements if e["id"] == "btn_equals")
            assert btn_equals["parent_id"] == "controls"

            # Verify display is at correct level
            display = next(e for e in elements if e["id"] == "display")
            assert display["parent_id"] == "content"
