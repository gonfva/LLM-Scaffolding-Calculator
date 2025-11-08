"""Tool definitions for Claude to interact with the UI."""

from typing import Any, TypedDict


# Tool type definition
class ToolDefinition(TypedDict):
    """Type for tool definition."""

    name: str
    description: str
    input_schema: dict[str, Any]


# Display text tool
DISPLAY_TEXT_TOOL: ToolDefinition = {
    "name": "display_text",
    "description": "Display text content on the UI. Use this to show information to the user.",
    "input_schema": {
        "type": "object",
        "properties": {
            "content": {
                "type": "string",
                "description": "The text content to display",
            },
            "id": {
                "type": "string",
                "description": "Unique identifier for this text element (e.g., 'text_1', 'result')",
            },
        },
        "required": ["content", "id"],
    },
}

# Create button tool
CREATE_BUTTON_TOOL: ToolDefinition = {
    "name": "create_button",
    "description": "Create a clickable button on the UI. When clicked, the button label will be sent back as user input.",
    "input_schema": {
        "type": "object",
        "properties": {
            "label": {
                "type": "string",
                "description": "The text to display on the button (e.g., 'Click me', 'Submit')",
            },
            "id": {
                "type": "string",
                "description": "Unique identifier for this button (e.g., 'btn_1', 'submit_btn')",
            },
        },
        "required": ["label", "id"],
    },
}

# All available tools
TOOLS = [DISPLAY_TEXT_TOOL, CREATE_BUTTON_TOOL]
