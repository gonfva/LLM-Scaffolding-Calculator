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
    parent_id: str | None = None  # Parent container ID (None = root level)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        result = {
            "type": self.type,
            "id": self.id,
            "properties": self.properties,
        }
        if self.layout:
            result["layout"] = self.layout
        if self.parent_id:
            result["parent_id"] = self.parent_id
        return result


class UIState:
    """Manages UI state - tracks all elements currently displayed."""

    def __init__(self) -> None:
        """Initialize empty UI state."""
        self.elements: list[UIElement] = []
        self.current_theme: str = "minimal"
        self.theme_variables: ThemeVariables | None = None

    def _validate_parent(self, parent_id: str | None) -> str | None:
        """Validate and return parent ID, or None for root level.

        Falls back to None (root) if parent_id is invalid or not a container.

        Args:
            parent_id: Parent container ID to validate

        Returns:
            Valid parent_id, or None to place at root level
        """
        if parent_id is None:
            return None

        # Find parent element
        parent = next((elem for elem in self.elements if elem.id == parent_id), None)
        if parent is None:
            # Parent doesn't exist, fall back to root
            return None

        # Check if parent is a container
        if parent.type != "container":
            # Parent is not a container, fall back to root
            return None

        return parent_id

    def get_element(self, element_id: str) -> UIElement | None:
        """Get element by ID.

        Args:
            element_id: Element ID to find

        Returns:
            UIElement if found, None otherwise
        """
        return next((elem for elem in self.elements if elem.id == element_id), None)

    def add_text(
        self,
        content: str,
        element_id: str,
        parent_id: str | None = None,
        flex_grow: float | None = None,
        width: str | None = None,
    ) -> None:
        """Add a text element to the UI.

        Args:
            content: Text content to display
            element_id: Unique identifier for this element
            parent_id: Parent container ID (None = root level)
            flex_grow: CSS flex-grow property
            width: CSS width property
        """
        layout: dict[str, float | str] = {}
        if flex_grow is not None:
            layout["flex_grow"] = flex_grow
        if width is not None:
            layout["width"] = width

        validated_parent = self._validate_parent(parent_id)

        element = UIElement(
            type="text",
            id=element_id,
            properties={"content": content},
            layout=layout,
            parent_id=validated_parent,
        )
        self.elements.append(element)

    def add_button(
        self,
        label: str,
        element_id: str,
        callback_id: str,
        parent_id: str | None = None,
        flex_grow: float | None = None,
        width: str | None = None,
    ) -> None:
        """Add a button element to the UI.

        Args:
            label: Text to display on the button
            element_id: Unique identifier for this button
            callback_id: Identifier sent back when button is clicked
            parent_id: Parent container ID (None = root level)
            flex_grow: CSS flex-grow property
            width: CSS width property
        """
        layout: dict[str, float | str] = {}
        if flex_grow is not None:
            layout["flex_grow"] = flex_grow
        if width is not None:
            layout["width"] = width

        validated_parent = self._validate_parent(parent_id)

        element = UIElement(
            type="button",
            id=element_id,
            properties={"label": label, "callback_id": callback_id},
            layout=layout,
            parent_id=validated_parent,
        )
        self.elements.append(element)

    def add_container(
        self,
        element_id: str,
        flex_direction: str,
        parent_id: str | None = None,
        justify_content: str | None = None,
        gap: str | None = None,
    ) -> None:
        """Add a container element for grouping other elements.

        Args:
            element_id: Unique identifier for this container
            flex_direction: Direction of flex layout ("row" or "column")
            parent_id: Parent container ID (None = root level)
            justify_content: Alignment along main axis
            gap: Space between items
        """
        layout: dict[str, str] = {"flex_direction": flex_direction}
        if justify_content is not None:
            layout["justify_content"] = justify_content
        if gap is not None:
            layout["gap"] = gap

        validated_parent = self._validate_parent(parent_id)

        element = UIElement(
            type="container",
            id=element_id,
            layout=layout,
            parent_id=validated_parent,
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

    def update_element(
        self,
        element_id: str,
        content: str | None = None,
        callback_id: str | None = None,
        flex_grow: float | None = None,
        width: str | None = None,
    ) -> bool:
        """Update an existing element's properties.

        Preserves element type, parent, and other layout properties not specified.
        Only updates the properties that are provided.

        Args:
            element_id: ID of element to update
            content: New content/label (for text and button elements)
            callback_id: New callback_id (for button elements)
            flex_grow: New flex_grow value
            width: New width value

        Returns:
            True if element was updated, False if element not found
        """
        element = self.get_element(element_id)
        if element is None:
            return False

        # Update properties if provided
        if content is not None:
            if element.type in ("text", "button"):
                if element.type == "text":
                    element.properties["content"] = content
                else:  # button
                    element.properties["label"] = content

        if callback_id is not None:
            if element.type == "button":
                element.properties["callback_id"] = callback_id

        # Update layout if provided
        if flex_grow is not None:
            element.layout["flex_grow"] = flex_grow
        if width is not None:
            element.layout["width"] = width

        return True

    def reset(self) -> None:
        """Clear all UI elements."""
        self.elements = []
