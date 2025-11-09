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
            "parent_id": {
                "type": "string",
                "description": "Parent container ID to place this element in (optional, defaults to root)",
            },
        },
        "required": ["content", "id"],
    },
}

# Create button tool
CREATE_BUTTON_TOOL: ToolDefinition = {
    "name": "create_button",
    "description": "Create a clickable button on the UI. When clicked, sends back the callback_id.",
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
            "callback_id": {
                "type": "string",
                "description": "Identifier sent back to the agent when button is clicked (e.g., 'on_submit', 'increment')",
            },
            "parent_id": {
                "type": "string",
                "description": "Parent container ID to place this button in (optional, defaults to root)",
            },
        },
        "required": ["label", "id", "callback_id"],
    },
}

# Create container tool
CREATE_CONTAINER_TOOL: ToolDefinition = {
    "name": "create_container",
    "description": "Create a container to group UI elements with flexbox layout.",
    "input_schema": {
        "type": "object",
        "properties": {
            "id": {
                "type": "string",
                "description": "Unique identifier for this container (e.g., 'container_1')",
            },
            "flex_direction": {
                "type": "string",
                "enum": ["row", "column"],
                "description": "Direction of flex layout (row for horizontal, column for vertical)",
            },
            "parent_id": {
                "type": "string",
                "description": "Parent container ID to place this container in (optional, defaults to root)",
            },
            "justify_content": {
                "type": "string",
                "enum": ["flex-start", "center", "flex-end", "space-between", "space-around"],
                "description": "Alignment along main axis",
            },
            "gap": {
                "type": "string",
                "description": "Space between items (e.g., '10px', '1rem')",
            },
        },
        "required": ["id", "flex_direction"],
    },
}

# Update element tool
UPDATE_ELEMENT_TOOL: ToolDefinition = {
    "name": "update_element",
    "description": "Update properties of an existing element. Preserves element type, parent, and other properties.",
    "input_schema": {
        "type": "object",
        "properties": {
            "id": {
                "type": "string",
                "description": "ID of the element to update",
            },
            "content": {
                "type": "string",
                "description": "New content for text elements or label for buttons",
            },
            "callback_id": {
                "type": "string",
                "description": "New callback_id for button elements",
            },
        },
        "required": ["id"],
    },
}

# All available tools
TOOLS = [
    DISPLAY_TEXT_TOOL,
    CREATE_BUTTON_TOOL,
    CREATE_CONTAINER_TOOL,
    UPDATE_ELEMENT_TOOL,
]
