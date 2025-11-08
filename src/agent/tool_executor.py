"""Executes tool calls made by Claude."""

import logging
from typing import Any

from src.agent.ui_state import UIState

logger = logging.getLogger(__name__)


class ToolExecutor:
    """Executes tools and updates UI state."""

    def __init__(self, ui_state: UIState) -> None:
        """Initialize executor with UI state.

        Args:
            ui_state: UIState instance to update
        """
        self.ui_state = ui_state

    def execute_tool(self, tool_name: str, tool_input: dict[str, Any]) -> str:
        """Execute a tool call.

        Args:
            tool_name: Name of the tool to execute
            tool_input: Input parameters for the tool

        Returns:
            Result message from tool execution
        """
        logger.info(f"Executing tool: {tool_name} with input: {tool_input}")

        if tool_name == "display_text":
            return self._execute_display_text(tool_input)
        elif tool_name == "create_button":
            return self._execute_create_button(tool_input)
        else:
            return f"Error: Unknown tool '{tool_name}'"

    def _execute_display_text(self, tool_input: dict[str, Any]) -> str:
        """Execute display_text tool.

        Args:
            tool_input: Must contain 'content' and 'id' keys

        Returns:
            Success or error message
        """
        try:
            content = tool_input.get("content")
            element_id = tool_input.get("id")

            if not content or not element_id:
                return "Error: display_text requires 'content' and 'id'"

            self.ui_state.add_text(content, element_id)
            logger.info(f"Displayed text: {element_id}")
            return f"Text '{element_id}' displayed successfully"
        except Exception as e:
            error_msg = f"Error displaying text: {e}"
            logger.error(error_msg)
            return error_msg

    def _execute_create_button(self, tool_input: dict[str, Any]) -> str:
        """Execute create_button tool.

        Args:
            tool_input: Must contain 'label' and 'id' keys

        Returns:
            Success or error message
        """
        try:
            label = tool_input.get("label")
            element_id = tool_input.get("id")

            if not label or not element_id:
                return "Error: create_button requires 'label' and 'id'"

            self.ui_state.add_button(label, element_id)
            logger.info(f"Created button: {element_id}")
            return f"Button '{element_id}' created successfully"
        except Exception as e:
            error_msg = f"Error creating button: {e}"
            logger.error(error_msg)
            return error_msg
