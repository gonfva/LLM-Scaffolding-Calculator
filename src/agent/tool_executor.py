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
        elif tool_name == "create_container":
            return self._execute_create_container(tool_input)
        elif tool_name == "update_element":
            return self._execute_update_element(tool_input)
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

            parent_id = tool_input.get("parent_id")

            self.ui_state.add_text(content, element_id, parent_id=parent_id)
            logger.info(f"Displayed text: {element_id}")
            return f"Text '{element_id}' displayed successfully"
        except Exception as e:
            error_msg = f"Error displaying text: {e}"
            logger.error(error_msg)
            return error_msg

    def _execute_create_button(self, tool_input: dict[str, Any]) -> str:
        """Execute create_button tool.

        Args:
            tool_input: Must contain 'label', 'id', and 'callback_id' keys

        Returns:
            Success or error message
        """
        try:
            label = tool_input.get("label")
            element_id = tool_input.get("id")
            callback_id = tool_input.get("callback_id")

            if not label or not element_id or not callback_id:
                return "Error: create_button requires 'label', 'id', and 'callback_id'"

            parent_id = tool_input.get("parent_id")

            self.ui_state.add_button(
                label,
                element_id,
                callback_id,
                parent_id=parent_id,
            )
            logger.info(f"Created button: {element_id}")
            return f"Button '{element_id}' created successfully"
        except Exception as e:
            error_msg = f"Error creating button: {e}"
            logger.error(error_msg)
            return error_msg

    def _execute_create_container(self, tool_input: dict[str, Any]) -> str:
        """Execute create_container tool.

        Args:
            tool_input: Must contain 'id'. Either 'flex_direction' for flexbox layout,
                       or 'rows'/'cols' for grid layout.

        Returns:
            Success or error message
        """
        try:
            element_id = tool_input.get("id")

            if not element_id:
                return "Error: create_container requires 'id'"

            # Extract parameters
            flex_direction = tool_input.get("flex_direction")
            parent_id = tool_input.get("parent_id")
            justify_content = tool_input.get("justify_content")
            gap = tool_input.get("gap")
            rows = tool_input.get("rows")
            cols = tool_input.get("cols")

            # Validate that either flex_direction or grid parameters are provided
            if not flex_direction and rows is None and cols is None:
                return "Error: create_container requires either 'flex_direction' or 'rows'/'cols'"

            self.ui_state.add_container(
                element_id,
                flex_direction=flex_direction,
                parent_id=parent_id,
                justify_content=justify_content,
                gap=gap,
                rows=rows,
                cols=cols,
            )
            logger.info(f"Created container: {element_id}")
            return f"Container '{element_id}' created successfully"
        except Exception as e:
            error_msg = f"Error creating container: {e}"
            logger.error(error_msg)
            return error_msg

    def _execute_update_element(self, tool_input: dict[str, Any]) -> str:
        """Execute update_element tool.

        Args:
            tool_input: Must contain 'id' key, optional: content, callback_id

        Returns:
            Success or error message
        """
        try:
            element_id = tool_input.get("id")

            if not element_id:
                return "Error: update_element requires 'id'"

            content = tool_input.get("content")
            callback_id = tool_input.get("callback_id")

            success = self.ui_state.update_element(
                element_id,
                content=content,
                callback_id=callback_id,
            )

            if success:
                logger.info(f"Updated element: {element_id}")
                return f"Element '{element_id}' updated successfully"
            else:
                return f"Error: Element '{element_id}' not found"
        except Exception as e:
            error_msg = f"Error updating element: {e}"
            logger.error(error_msg)
            return error_msg
