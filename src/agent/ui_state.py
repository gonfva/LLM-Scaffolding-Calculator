"""Manages the current UI state."""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class UIElement:
    """Represents a single UI element."""

    type: str  # "text" or "button"
    id: str
    properties: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "type": self.type,
            "id": self.id,
            "properties": self.properties,
        }


class UIState:
    """Manages UI state - tracks all elements currently displayed."""

    def __init__(self) -> None:
        """Initialize empty UI state."""
        self.elements: list[UIElement] = []

    def add_text(self, content: str, element_id: str) -> None:
        """Add a text element to the UI.

        Args:
            content: Text content to display
            element_id: Unique identifier for this element
        """
        element = UIElement(
            type="text",
            id=element_id,
            properties={"content": content},
        )
        self.elements.append(element)

    def add_button(self, label: str, element_id: str) -> None:
        """Add a button element to the UI.

        Args:
            label: Text to display on the button
            element_id: Unique identifier for this button
        """
        element = UIElement(
            type="button",
            id=element_id,
            properties={"label": label},
        )
        self.elements.append(element)

    def get_state(self) -> dict[str, Any]:
        """Get current UI state as a dictionary.

        Returns:
            Dictionary representation of current UI elements
        """
        return {
            "elements": [elem.to_dict() for elem in self.elements],
        }

    def reset(self) -> None:
        """Clear all UI elements."""
        self.elements = []
