"""Manages the current UI state."""

from dataclasses import dataclass, field
from typing import Any

from src.agent.themes import ThemeVariables, get_theme


@dataclass
class UIElement:
    """Represents a single UI element."""

    type: str  # "text", "button", or "container"
    id: str
    properties: dict[str, Any] = field(default_factory=dict)
    layout: dict[str, Any] = field(default_factory=dict)  # flex properties

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        result = {
            "type": self.type,
            "id": self.id,
            "properties": self.properties,
        }
        if self.layout:
            result["layout"] = self.layout
        return result


class UIState:
    """Manages UI state - tracks all elements currently displayed."""

    def __init__(self) -> None:
        """Initialize empty UI state."""
        self.elements: list[UIElement] = []
        self.current_theme: str = "minimal"
        self.theme_variables: ThemeVariables | None = None

    def add_text(
        self,
        content: str,
        element_id: str,
        flex_grow: float | None = None,
        width: str | None = None,
    ) -> None:
        """Add a text element to the UI.

        Args:
            content: Text content to display
            element_id: Unique identifier for this element
            flex_grow: CSS flex-grow property
            width: CSS width property
        """
        layout: dict[str, float | str] = {}
        if flex_grow is not None:
            layout["flex_grow"] = flex_grow
        if width is not None:
            layout["width"] = width

        element = UIElement(
            type="text",
            id=element_id,
            properties={"content": content},
            layout=layout,
        )
        self.elements.append(element)

    def add_button(
        self,
        label: str,
        element_id: str,
        callback_id: str,
        flex_grow: float | None = None,
        width: str | None = None,
    ) -> None:
        """Add a button element to the UI.

        Args:
            label: Text to display on the button
            element_id: Unique identifier for this button
            callback_id: Identifier sent back when button is clicked
            flex_grow: CSS flex-grow property
            width: CSS width property
        """
        layout: dict[str, float | str] = {}
        if flex_grow is not None:
            layout["flex_grow"] = flex_grow
        if width is not None:
            layout["width"] = width

        element = UIElement(
            type="button",
            id=element_id,
            properties={"label": label, "callback_id": callback_id},
            layout=layout,
        )
        self.elements.append(element)

    def add_container(
        self,
        element_id: str,
        flex_direction: str,
        justify_content: str | None = None,
        gap: str | None = None,
    ) -> None:
        """Add a container element for grouping other elements.

        Args:
            element_id: Unique identifier for this container
            flex_direction: Direction of flex layout ("row" or "column")
            justify_content: Alignment along main axis
            gap: Space between items
        """
        layout = {"flex_direction": flex_direction}
        if justify_content is not None:
            layout["justify_content"] = justify_content
        if gap is not None:
            layout["gap"] = gap

        element = UIElement(
            type="container",
            id=element_id,
            layout=layout,
        )
        self.elements.append(element)

    def apply_theme(
        self,
        theme_name: str,
        custom_overrides: dict[str, str] | None = None,
    ) -> bool:
        """Apply a theme to the UI.

        Args:
            theme_name: Name of the theme to apply
            custom_overrides: Optional custom CSS variable overrides

        Returns:
            True if theme was applied successfully, False otherwise
        """
        theme = get_theme(theme_name)
        if not theme:
            return False

        self.current_theme = theme_name
        variables = dict(theme["variables"])
        if custom_overrides:
            variables.update(custom_overrides)
        self.theme_variables = variables  # type: ignore[assignment]
        return True

    def get_state(self) -> dict[str, Any]:
        """Get current UI state as a dictionary.

        Returns:
            Dictionary representation of current UI elements and theme
        """
        state: dict[str, Any] = {
            "elements": [elem.to_dict() for elem in self.elements],
        }
        if self.theme_variables:
            state["theme"] = {
                "name": self.current_theme,
                "variables": self.theme_variables,
            }
        return state

    def reset(self) -> None:
        """Clear all UI elements."""
        self.elements = []
