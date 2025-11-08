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
            "flex_grow": {
                "type": "number",
                "description": "CSS flex-grow property for layout (0-1, default 0)",
            },
            "width": {
                "type": "string",
                "description": "CSS width property (e.g., '100%', '200px', default 'auto')",
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
            "flex_grow": {
                "type": "number",
                "description": "CSS flex-grow property for layout (0-1, default 0)",
            },
            "width": {
                "type": "string",
                "description": "CSS width property (e.g., '100%', '200px', default 'auto')",
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

# Apply theme tool
APPLY_THEME_TOOL: ToolDefinition = {
    "name": "apply_theme",
    "description": "Apply a theme to the UI. Available themes: minimal, pirate, halloween, cyberpunk, retro, forest. Use this to style the entire interface with a consistent look and feel.",
    "input_schema": {
        "type": "object",
        "properties": {
            "theme_name": {
                "type": "string",
                "enum": ["minimal", "pirate", "halloween", "cyberpunk", "retro", "forest"],
                "description": "Name of the theme to apply (e.g., 'pirate', 'halloween', 'cyberpunk')",
            },
            "custom_overrides": {
                "type": "object",
                "description": 'Optional custom CSS variable overrides (e.g., {"primary_color": "#ff0000"})',
                "additionalProperties": {"type": "string"},
            },
        },
        "required": ["theme_name"],
    },
}

# All available tools
TOOLS = [DISPLAY_TEXT_TOOL, CREATE_BUTTON_TOOL, CREATE_CONTAINER_TOOL, APPLY_THEME_TOOL]
