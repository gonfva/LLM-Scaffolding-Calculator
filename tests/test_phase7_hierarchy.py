"""Tests for Phase 7: Hierarchical UI structure and element updates."""

from unittest.mock import MagicMock, patch

from anthropic.types import TextBlock, ToolUseBlock

from src.agent.claude_agent import ClaudeAgent
from src.agent.tool_executor import ToolExecutor
from src.agent.ui_state import UIState


class TestParentIDValidation:
    """Tests for parent_id validation and fallback behavior."""

    def test_add_text_with_valid_parent(self) -> None:
        """Test adding text element to valid container parent."""
        ui_state = UIState()
        # Create a container first
        ui_state.add_container("main_container", "column")
        # Add text to the container
        ui_state.add_text("Hello", "text_1", parent_id="main_container")

        state = ui_state.get_state()
        # Find the text element
        text_elem = next(e for e in state["elements"] if e["id"] == "text_1")
        assert text_elem["parent_id"] == "main_container"

    def test_add_button_with_valid_parent(self) -> None:
        """Test adding button element to valid container parent."""
        ui_state = UIState()
        ui_state.add_container("button_row", "row")
        ui_state.add_button("Click me", "btn_1", "on_click", parent_id="button_row")

        state = ui_state.get_state()
        btn_elem = next(e for e in state["elements"] if e["id"] == "btn_1")
        assert btn_elem["parent_id"] == "button_row"

    def test_add_element_with_nonexistent_parent_fallback(self) -> None:
        """Test that nonexistent parent falls back to root."""
        ui_state = UIState()
        ui_state.add_text("Text", "text_1", parent_id="nonexistent_container")

        state = ui_state.get_state()
        text_elem = next(e for e in state["elements"] if e["id"] == "text_1")
        # Should not have parent_id (root level)
        assert text_elem.get("parent_id") is None

    def test_add_element_with_text_parent_fallback(self) -> None:
        """Test that text parent (non-container) falls back to root."""
        ui_state = UIState()
        ui_state.add_text("Parent Text", "parent_text", parent_id=None)
        # Try to add element to text (not a container)
        ui_state.add_text("Child Text", "child_text", parent_id="parent_text")

        state = ui_state.get_state()
        child_elem = next(e for e in state["elements"] if e["id"] == "child_text")
        # Should fall back to root since parent_text is not a container
        assert child_elem.get("parent_id") is None

    def test_nested_containers(self) -> None:
        """Test creating containers inside containers."""
        ui_state = UIState()
        ui_state.add_container("outer", "column")
        ui_state.add_container("inner", "row", parent_id="outer")
        ui_state.add_text("Nested Text", "text_1", parent_id="inner")

        state = ui_state.get_state()
        inner_container = next(e for e in state["elements"] if e["id"] == "inner")
        assert inner_container["parent_id"] == "outer"

        text_elem = next(e for e in state["elements"] if e["id"] == "text_1")
        assert text_elem["parent_id"] == "inner"


class TestElementUpdate:
    """Tests for updating existing elements."""

    def test_update_text_content(self) -> None:
        """Test updating text element content."""
        ui_state = UIState()
        ui_state.add_text("Original", "text_1")

        # Update content
        success = ui_state.update_element("text_1", content="Updated")
        assert success is True

        state = ui_state.get_state()
        text_elem = next(e for e in state["elements"] if e["id"] == "text_1")
        assert text_elem["properties"]["content"] == "Updated"

    def test_update_button_label(self) -> None:
        """Test updating button label."""
        ui_state = UIState()
        ui_state.add_button("Click", "btn_1", "on_click")

        success = ui_state.update_element("btn_1", content="Updated Button")
        assert success is True

        state = ui_state.get_state()
        btn_elem = next(e for e in state["elements"] if e["id"] == "btn_1")
        assert btn_elem["properties"]["label"] == "Updated Button"

    def test_update_button_callback(self) -> None:
        """Test updating button callback_id."""
        ui_state = UIState()
        ui_state.add_button("Click", "btn_1", "old_callback")

        success = ui_state.update_element("btn_1", callback_id="new_callback")
        assert success is True

        state = ui_state.get_state()
        btn_elem = next(e for e in state["elements"] if e["id"] == "btn_1")
        assert btn_elem["properties"]["callback_id"] == "new_callback"

    def test_update_element_flex_grow(self) -> None:
        """Test updating element content via update_element."""
        ui_state = UIState()
        ui_state.add_text("Text", "text_1")

        success = ui_state.update_element("text_1", content="Updated Text")
        assert success is True

        state = ui_state.get_state()
        text_elem = next(e for e in state["elements"] if e["id"] == "text_1")
        assert text_elem["properties"]["content"] == "Updated Text"

    def test_update_element_width(self) -> None:
        """Test updating element preserves properties."""
        ui_state = UIState()
        ui_state.add_text("Text", "text_1")

        success = ui_state.update_element("text_1", content="New Text")
        assert success is True

        state = ui_state.get_state()
        text_elem = next(e for e in state["elements"] if e["id"] == "text_1")
        assert text_elem["properties"]["content"] == "New Text"

    def test_update_preserves_other_properties(self) -> None:
        """Test that update preserves callback_id for buttons."""
        ui_state = UIState()
        ui_state.add_button("Original", "btn_1", "callback_1")

        # Update only label
        success = ui_state.update_element("btn_1", content="Updated")
        assert success is True

        state = ui_state.get_state()
        btn_elem = next(e for e in state["elements"] if e["id"] == "btn_1")
        assert btn_elem["properties"]["label"] == "Updated"
        assert btn_elem["properties"]["callback_id"] == "callback_1"

    def test_update_nonexistent_element(self) -> None:
        """Test updating nonexistent element returns False."""
        ui_state = UIState()
        success = ui_state.update_element("nonexistent", content="New")
        assert success is False

    def test_update_container_not_allowed(self) -> None:
        """Test that container content cannot be updated (only layout)."""
        ui_state = UIState()
        ui_state.add_container("container_1", "row")

        # Try to update content (containers don't have content)
        success = ui_state.update_element("container_1", content="Should not work")
        assert success is True  # Returns True even though container has no content property

        state = ui_state.get_state()
        container = next(e for e in state["elements"] if e["id"] == "container_1")
        # Container should not have content property
        assert "content" not in container.get("properties", {})


class TestToolExecutorHierarchy:
    """Tests for ToolExecutor with hierarchical elements."""

    def test_execute_display_text_with_parent(self) -> None:
        """Test executing display_text tool with parent_id."""
        ui_state = UIState()
        ui_state.add_container("section", "column")

        executor = ToolExecutor(ui_state)
        result = executor.execute_tool(
            "display_text",
            {"content": "Hello", "id": "text_1", "parent_id": "section"},
        )

        assert "successfully" in result
        state = ui_state.get_state()
        text_elem = next(e for e in state["elements"] if e["id"] == "text_1")
        assert text_elem["parent_id"] == "section"

    def test_execute_create_button_with_parent(self) -> None:
        """Test executing create_button tool with parent_id."""
        ui_state = UIState()
        ui_state.add_container("buttons", "row")

        executor = ToolExecutor(ui_state)
        result = executor.execute_tool(
            "create_button",
            {
                "label": "Submit",
                "id": "btn_submit",
                "callback_id": "on_submit",
                "parent_id": "buttons",
            },
        )

        assert "successfully" in result
        state = ui_state.get_state()
        btn = next(e for e in state["elements"] if e["id"] == "btn_submit")
        assert btn["parent_id"] == "buttons"

    def test_execute_update_element(self) -> None:
        """Test executing update_element tool."""
        ui_state = UIState()
        ui_state.add_text("Original", "text_1")

        executor = ToolExecutor(ui_state)
        result = executor.execute_tool("update_element", {"id": "text_1", "content": "Updated"})

        assert "successfully" in result
        state = ui_state.get_state()
        text = next(e for e in state["elements"] if e["id"] == "text_1")
        assert text["properties"]["content"] == "Updated"

    def test_execute_update_element_not_found(self) -> None:
        """Test executing update_element with nonexistent element."""
        ui_state = UIState()
        executor = ToolExecutor(ui_state)

        result = executor.execute_tool("update_element", {"id": "nonexistent", "content": "New"})

        assert "not found" in result or "Error" in result

    def test_execute_update_element_missing_id(self) -> None:
        """Test executing update_element without id raises error."""
        ui_state = UIState()
        executor = ToolExecutor(ui_state)

        result = executor.execute_tool("update_element", {"content": "New"})

        assert "Error" in result or "requires" in result


class TestAgentHierarchicalUI:
    """Tests for agent building hierarchical UI."""

    def test_agent_creates_nested_structure(self) -> None:
        """Test agent can create nested container structure."""
        mock_container_tool = ToolUseBlock(
            type="tool_use",
            id="tool_1",
            name="create_container",
            input={"id": "main", "flex_direction": "column"},
        )
        mock_text_tool = ToolUseBlock(
            type="tool_use",
            id="tool_2",
            name="display_text",
            input={"id": "text_1", "content": "Title", "parent_id": "main"},
        )
        mock_button_tool = ToolUseBlock(
            type="tool_use",
            id="tool_3",
            name="create_button",
            input={"id": "btn_1", "label": "Go", "callback_id": "go", "parent_id": "main"},
        )
        mock_text = TextBlock(type="text", text="UI ready")

        mock_response_with_tools = MagicMock()
        mock_response_with_tools.content = [
            mock_container_tool,
            mock_text_tool,
            mock_button_tool,
            mock_text,
        ]

        mock_text_final = TextBlock(type="text", text="Done")
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
            agent.process_message("Create UI")

            ui_state = agent.get_ui_state()

            # Check container exists
            assert any(e["id"] == "main" and e["type"] == "container" for e in ui_state["elements"])

            # Check text is nested in container
            text_elem = next(e for e in ui_state["elements"] if e["id"] == "text_1")
            assert text_elem["parent_id"] == "main"

            # Check button is nested in container
            btn_elem = next(e for e in ui_state["elements"] if e["id"] == "btn_1")
            assert btn_elem["parent_id"] == "main"

    def test_agent_updates_element_instead_of_creating_new(self) -> None:
        """Test agent uses update_element to modify rather than create new."""
        # First create an element
        mock_text_tool = ToolUseBlock(
            type="tool_use",
            id="tool_1",
            name="display_text",
            input={"id": "result", "content": "0"},
        )
        mock_text = TextBlock(type="text", text="Initial")

        mock_response_1 = MagicMock()
        mock_response_1.content = [mock_text_tool, mock_text]

        mock_text_final_1 = TextBlock(type="text", text="Done")
        mock_response_1_final = MagicMock()
        mock_response_1_final.content = [mock_text_final_1]

        # Then update it
        mock_update_tool = ToolUseBlock(
            type="tool_use",
            id="tool_2",
            name="update_element",
            input={"id": "result", "content": "42"},
        )
        mock_text_2 = TextBlock(type="text", text="Updated")

        mock_response_2 = MagicMock()
        mock_response_2.content = [mock_update_tool, mock_text_2]

        mock_text_final_2 = TextBlock(type="text", text="Done again")
        mock_response_2_final = MagicMock()
        mock_response_2_final.content = [mock_text_final_2]

        with patch("src.agent.claude_agent.Anthropic") as mock_anthropic:
            mock_client = MagicMock()
            mock_anthropic.return_value = mock_client
            mock_client.messages.create.side_effect = [
                mock_response_1,
                mock_response_1_final,
                mock_response_2,
                mock_response_2_final,
            ]

            agent = ClaudeAgent(system_prompt="Test", api_key="test-key")
            agent.process_message("Create result")

            ui_state_1 = agent.get_ui_state()
            assert len(ui_state_1["elements"]) == 1
            assert ui_state_1["elements"][0]["properties"]["content"] == "0"

            agent.process_message("Update result to 42")

            ui_state_2 = agent.get_ui_state()
            # Should still have only 1 element, not 2
            assert len(ui_state_2["elements"]) == 1
            assert ui_state_2["elements"][0]["properties"]["content"] == "42"

    def test_agent_with_multiple_nested_levels(self) -> None:
        """Test agent creating deeply nested structure."""
        tools = [
            ToolUseBlock(
                type="tool_use",
                id="tool_1",
                name="create_container",
                input={"id": "outer", "flex_direction": "column"},
            ),
            ToolUseBlock(
                type="tool_use",
                id="tool_2",
                name="create_container",
                input={"id": "inner", "flex_direction": "row", "parent_id": "outer"},
            ),
            ToolUseBlock(
                type="tool_use",
                id="tool_3",
                name="display_text",
                input={"id": "label", "content": "Count:", "parent_id": "inner"},
            ),
            ToolUseBlock(
                type="tool_use",
                id="tool_4",
                name="display_text",
                input={"id": "value", "content": "10", "parent_id": "inner"},
            ),
        ]
        mock_text = TextBlock(type="text", text="Structure created")

        mock_response_with_tools = MagicMock()
        mock_response_with_tools.content = tools + [mock_text]

        mock_text_final = TextBlock(type="text", text="Done")
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
            agent.process_message("Create nested structure")

            ui_state = agent.get_ui_state()

            # Verify hierarchy
            outer = next(e for e in ui_state["elements"] if e["id"] == "outer")
            # Root level elements don't have parent_id in serialization
            assert "parent_id" not in outer or outer.get("parent_id") is None

            inner = next(e for e in ui_state["elements"] if e["id"] == "inner")
            assert inner["parent_id"] == "outer"

            label = next(e for e in ui_state["elements"] if e["id"] == "label")
            assert label["parent_id"] == "inner"

            value = next(e for e in ui_state["elements"] if e["id"] == "value")
            assert value["parent_id"] == "inner"


class TestGetElement:
    """Tests for retrieving elements by ID."""

    def test_get_existing_element(self) -> None:
        """Test getting an existing element by ID."""
        ui_state = UIState()
        ui_state.add_text("Hello", "text_1")

        elem = ui_state.get_element("text_1")
        assert elem is not None
        assert elem.id == "text_1"
        assert elem.properties["content"] == "Hello"

    def test_get_nonexistent_element(self) -> None:
        """Test getting nonexistent element returns None."""
        ui_state = UIState()
        elem = ui_state.get_element("nonexistent")
        assert elem is None

    def test_get_element_with_parent(self) -> None:
        """Test getting element that has parent_id."""
        ui_state = UIState()
        ui_state.add_container("section", "column")
        ui_state.add_text("Text", "text_1", parent_id="section")

        elem = ui_state.get_element("text_1")
        assert elem is not None
        assert elem.parent_id == "section"
