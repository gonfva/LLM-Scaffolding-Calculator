"""Theme definitions for dynamic UI styling."""

from typing import TypedDict


class ThemeVariables(TypedDict, total=False):
    """CSS variables for a theme."""

    # Primary colors
    primary_color: str
    primary_dark: str
    primary_light: str

    # Secondary colors
    secondary_color: str
    accent_color: str

    # Backgrounds and text
    bg_primary: str
    bg_secondary: str
    text_primary: str
    text_secondary: str

    # Borders
    border_color: str
    border_width: str
    border_radius: str

    # Fonts
    font_family: str
    font_size_base: str
    font_size_large: str
    font_size_small: str
    font_weight_normal: str
    font_weight_bold: str

    # Spacing
    spacing_unit: str

    # Shadows
    shadow_sm: str
    shadow_md: str
    shadow_lg: str

    # Button specific
    button_bg: str
    button_text: str
    button_hover_bg: str
    button_border: str

    # Input specific
    input_bg: str
    input_text: str
    input_border: str

    # Animations
    transition_duration: str


class Theme(TypedDict):
    """Complete theme definition."""

    name: str
    description: str
    variables: ThemeVariables


# Light/Minimal Theme
THEME_MINIMAL: Theme = {
    "name": "minimal",
    "description": "Clean, minimal design with light colors and sans-serif fonts",
    "variables": {
        "primary_color": "#0066cc",
        "primary_dark": "#0052a3",
        "primary_light": "#e6f0ff",
        "secondary_color": "#666666",
        "accent_color": "#0066cc",
        "bg_primary": "#ffffff",
        "bg_secondary": "#f9f9f9",
        "text_primary": "#333333",
        "text_secondary": "#666666",
        "border_color": "#dddddd",
        "border_width": "1px",
        "border_radius": "4px",
        "font_family": "'Segoe UI', Roboto, sans-serif",
        "font_size_base": "14px",
        "font_size_large": "18px",
        "font_size_small": "12px",
        "font_weight_normal": "400",
        "font_weight_bold": "600",
        "spacing_unit": "8px",
        "shadow_sm": "0 1px 2px rgba(0, 0, 0, 0.05)",
        "shadow_md": "0 4px 6px rgba(0, 0, 0, 0.1)",
        "shadow_lg": "0 10px 15px rgba(0, 0, 0, 0.15)",
        "button_bg": "#0066cc",
        "button_text": "#ffffff",
        "button_hover_bg": "#0052a3",
        "button_border": "none",
        "input_bg": "#ffffff",
        "input_text": "#333333",
        "input_border": "#dddddd",
        "transition_duration": "0.2s",
    },
}

# Pirate Theme
THEME_PIRATE: Theme = {
    "name": "pirate",
    "description": "Pirate-inspired theme with browns, golds, and maritime colors",
    "variables": {
        "primary_color": "#8B4513",
        "primary_dark": "#654321",
        "primary_light": "#D2B48C",
        "secondary_color": "#DAA520",
        "accent_color": "#FFD700",
        "bg_primary": "#1a1410",
        "bg_secondary": "#2d2419",
        "text_primary": "#F5DEB3",
        "text_secondary": "#D2B48C",
        "border_color": "#654321",
        "border_width": "2px",
        "border_radius": "2px",
        "font_family": "Georgia, serif",
        "font_size_base": "14px",
        "font_size_large": "18px",
        "font_size_small": "12px",
        "font_weight_normal": "400",
        "font_weight_bold": "700",
        "spacing_unit": "10px",
        "shadow_sm": "0 2px 4px rgba(0, 0, 0, 0.5)",
        "shadow_md": "0 4px 8px rgba(0, 0, 0, 0.6)",
        "shadow_lg": "0 8px 16px rgba(0, 0, 0, 0.7)",
        "button_bg": "#8B4513",
        "button_text": "#F5DEB3",
        "button_hover_bg": "#A0522D",
        "button_border": "2px solid #654321",
        "input_bg": "#2d2419",
        "input_text": "#F5DEB3",
        "input_border": "2px solid #654321",
        "transition_duration": "0.3s",
    },
}

# Halloween Theme
THEME_HALLOWEEN: Theme = {
    "name": "halloween",
    "description": "Spooky Halloween theme with oranges, purples, and blacks",
    "variables": {
        "primary_color": "#ff6600",
        "primary_dark": "#cc5500",
        "primary_light": "#ffcc99",
        "secondary_color": "#9933ff",
        "accent_color": "#ff3300",
        "bg_primary": "#1a0f2e",
        "bg_secondary": "#2d1b4e",
        "text_primary": "#ffd700",
        "text_secondary": "#ff9999",
        "border_color": "#9933ff",
        "border_width": "2px",
        "border_radius": "8px",
        "font_family": "'Georgia', 'serif'",
        "font_size_base": "14px",
        "font_size_large": "18px",
        "font_size_small": "12px",
        "font_weight_normal": "400",
        "font_weight_bold": "700",
        "spacing_unit": "8px",
        "shadow_sm": "0 0 5px rgba(153, 51, 255, 0.3)",
        "shadow_md": "0 0 10px rgba(255, 102, 0, 0.4)",
        "shadow_lg": "0 0 20px rgba(255, 51, 0, 0.5)",
        "button_bg": "#ff6600",
        "button_text": "#ffffff",
        "button_hover_bg": "#ff8533",
        "button_border": "2px solid #9933ff",
        "input_bg": "#2d1b4e",
        "input_text": "#ffd700",
        "input_border": "2px solid #9933ff",
        "transition_duration": "0.25s",
    },
}

# Cyberpunk Theme
THEME_CYBERPUNK: Theme = {
    "name": "cyberpunk",
    "description": "Neon cyberpunk theme with bright cyans, pinks, and dark backgrounds",
    "variables": {
        "primary_color": "#00ffff",
        "primary_dark": "#00cccc",
        "primary_light": "#00ffff",
        "secondary_color": "#ff0080",
        "accent_color": "#ffff00",
        "bg_primary": "#0a0e27",
        "bg_secondary": "#16213e",
        "text_primary": "#00ffff",
        "text_secondary": "#ff0080",
        "border_color": "#00ffff",
        "border_width": "2px",
        "border_radius": "0px",
        "font_family": "'Courier New', monospace",
        "font_size_base": "14px",
        "font_size_large": "18px",
        "font_size_small": "12px",
        "font_weight_normal": "400",
        "font_weight_bold": "700",
        "spacing_unit": "8px",
        "shadow_sm": "0 0 10px rgba(0, 255, 255, 0.3)",
        "shadow_md": "0 0 20px rgba(0, 255, 255, 0.5)",
        "shadow_lg": "0 0 40px rgba(255, 0, 128, 0.6)",
        "button_bg": "#00ffff",
        "button_text": "#0a0e27",
        "button_hover_bg": "#00cccc",
        "button_border": "2px solid #ff0080",
        "input_bg": "#16213e",
        "input_text": "#00ffff",
        "input_border": "2px solid #00ffff",
        "transition_duration": "0.15s",
    },
}

# Retro/80s Theme
THEME_RETRO: Theme = {
    "name": "retro",
    "description": "Retro 80s theme with bright colors and funky styling",
    "variables": {
        "primary_color": "#ff006e",
        "primary_dark": "#d9006e",
        "primary_light": "#ffb3d9",
        "secondary_color": "#00f5ff",
        "accent_color": "#ffbe0b",
        "bg_primary": "#ffffff",
        "bg_secondary": "#f0f0f0",
        "text_primary": "#ff006e",
        "text_secondary": "#00f5ff",
        "border_color": "#ffbe0b",
        "border_width": "3px",
        "border_radius": "12px",
        "font_family": "'Arial Black', sans-serif",
        "font_size_base": "14px",
        "font_size_large": "18px",
        "font_size_small": "12px",
        "font_weight_normal": "400",
        "font_weight_bold": "900",
        "spacing_unit": "10px",
        "shadow_sm": "3px 3px 0px rgba(255, 0, 110, 0.3)",
        "shadow_md": "6px 6px 0px rgba(255, 190, 11, 0.4)",
        "shadow_lg": "8px 8px 0px rgba(0, 245, 255, 0.3)",
        "button_bg": "#ff006e",
        "button_text": "#ffffff",
        "button_hover_bg": "#ffb3d9",
        "button_border": "3px solid #ffbe0b",
        "input_bg": "#ffffff",
        "input_text": "#ff006e",
        "input_border": "3px solid #ffbe0b",
        "transition_duration": "0.1s",
    },
}

# Forest Theme
THEME_FOREST: Theme = {
    "name": "forest",
    "description": "Natural forest theme with greens, browns, and earth tones",
    "variables": {
        "primary_color": "#2d5016",
        "primary_dark": "#1a2e0a",
        "primary_light": "#4a7c2c",
        "secondary_color": "#6b4423",
        "accent_color": "#a8d73d",
        "bg_primary": "#f5f9f2",
        "bg_secondary": "#e8f0e0",
        "text_primary": "#1a2e0a",
        "text_secondary": "#4a7c2c",
        "border_color": "#6b4423",
        "border_width": "1px",
        "border_radius": "6px",
        "font_family": "'Trebuchet MS', sans-serif",
        "font_size_base": "14px",
        "font_size_large": "18px",
        "font_size_small": "12px",
        "font_weight_normal": "400",
        "font_weight_bold": "600",
        "spacing_unit": "8px",
        "shadow_sm": "0 2px 4px rgba(42, 78, 22, 0.1)",
        "shadow_md": "0 4px 8px rgba(42, 78, 22, 0.15)",
        "shadow_lg": "0 8px 16px rgba(42, 78, 22, 0.2)",
        "button_bg": "#2d5016",
        "button_text": "#f5f9f2",
        "button_hover_bg": "#4a7c2c",
        "button_border": "1px solid #6b4423",
        "input_bg": "#ffffff",
        "input_text": "#1a2e0a",
        "input_border": "1px solid #6b4423",
        "transition_duration": "0.2s",
    },
}

# All available themes
THEMES: dict[str, Theme] = {
    "minimal": THEME_MINIMAL,
    "pirate": THEME_PIRATE,
    "halloween": THEME_HALLOWEEN,
    "cyberpunk": THEME_CYBERPUNK,
    "retro": THEME_RETRO,
    "forest": THEME_FOREST,
}


def get_theme(theme_name: str) -> Theme | None:
    """Get a theme by name.

    Args:
        theme_name: Name of the theme to retrieve

    Returns:
        Theme dict if found, None otherwise
    """
    return THEMES.get(theme_name.lower())


def get_available_themes() -> list[str]:
    """Get list of all available theme names.

    Returns:
        List of theme names
    """
    return list(THEMES.keys())


def merge_theme_variables(
    base_theme: ThemeVariables, overrides: dict[str, str] | None = None
) -> ThemeVariables:
    """Merge custom variables with base theme.

    Args:
        base_theme: Base theme variables
        overrides: Optional custom variable overrides

    Returns:
        Merged theme variables
    """
    result = dict(base_theme)
    if overrides:
        result.update(overrides)
    return result  # type: ignore[return-value]
