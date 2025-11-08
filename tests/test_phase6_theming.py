"""Tests for Phase 6: Advanced dynamic styling and theming."""

from unittest.mock import MagicMock, patch

from anthropic.types import TextBlock, ToolUseBlock

from src.agent.claude_agent import ClaudeAgent
from src.agent.themes import (
    THEME_CYBERPUNK,
    THEME_FOREST,
    THEME_HALLOWEEN,
    THEME_MINIMAL,
    THEME_PIRATE,
    THEME_RETRO,
    get_available_themes,
    get_theme,
    merge_theme_variables,
)
from src.agent.ui_state import UIState


class TestThemeRetrieval:
    """Tests for theme retrieval functions."""

    def test_get_theme_minimal(self) -> None:
        """Test retrieving minimal theme."""
        theme = get_theme("minimal")
        assert theme is not None
        assert theme["name"] == "minimal"
        assert "variables" in theme
        assert theme["variables"]["primary_color"] == "#0066cc"

    def test_get_theme_pirate(self) -> None:
        """Test retrieving pirate theme."""
        theme = get_theme("pirate")
        assert theme is not None
        assert theme["name"] == "pirate"
        assert theme["variables"]["primary_color"] == "#8B4513"

    def test_get_theme_halloween(self) -> None:
        """Test retrieving halloween theme."""
        theme = get_theme("halloween")
        assert theme is not None
        assert theme["name"] == "halloween"
        assert theme["variables"]["primary_color"] == "#ff6600"

    def test_get_theme_cyberpunk(self) -> None:
        """Test retrieving cyberpunk theme."""
        theme = get_theme("cyberpunk")
        assert theme is not None
        assert theme["name"] == "cyberpunk"
        assert theme["variables"]["primary_color"] == "#00ffff"

    def test_get_theme_retro(self) -> None:
        """Test retrieving retro theme."""
        theme = get_theme("retro")
        assert theme is not None
        assert theme["name"] == "retro"
        assert theme["variables"]["primary_color"] == "#ff006e"

    def test_get_theme_forest(self) -> None:
        """Test retrieving forest theme."""
        theme = get_theme("forest")
        assert theme is not None
        assert theme["name"] == "forest"
        assert theme["variables"]["primary_color"] == "#2d5016"

    def test_get_theme_invalid(self) -> None:
        """Test retrieving non-existent theme."""
        theme = get_theme("nonexistent")
        assert theme is None

    def test_get_theme_case_insensitive(self) -> None:
        """Test theme retrieval is case insensitive."""
        theme = get_theme("PIRATE")
        assert theme is not None
        assert theme["name"] == "pirate"

    def test_get_available_themes(self) -> None:
        """Test getting list of available themes."""
        themes = get_available_themes()
        assert isinstance(themes, list)
        assert len(themes) == 6
        assert "minimal" in themes
        assert "pirate" in themes
        assert "halloween" in themes
        assert "cyberpunk" in themes
        assert "retro" in themes
        assert "forest" in themes


class TestThemeVariables:
    """Tests for theme variable merging."""

    def test_merge_theme_variables_no_overrides(self) -> None:
        """Test merging with no custom overrides."""
        base = THEME_MINIMAL["variables"]
        merged = merge_theme_variables(base)
        assert merged["primary_color"] == "#0066cc"

    def test_merge_theme_variables_with_overrides(self) -> None:
        """Test merging with custom overrides."""
        base = THEME_MINIMAL["variables"]
        overrides = {"primary_color": "#ff0000", "text_primary": "#000000"}
        merged = merge_theme_variables(base, overrides)
        assert merged["primary_color"] == "#ff0000"
        assert merged["text_primary"] == "#000000"
        assert merged["secondary_color"] == base["secondary_color"]

    def test_merge_theme_preserves_original(self) -> None:
        """Test that merge doesn't modify original theme."""
        base = dict(THEME_PIRATE["variables"])
        overrides = {"primary_color": "#ffffff"}
        merged = merge_theme_variables(base, overrides)
        assert base["primary_color"] == "#8B4513"
        assert merged["primary_color"] == "#ffffff"


class TestUIStateThemeManagement:
    """Tests for UIState theme management."""

    def test_apply_theme_minimal(self) -> None:
        """Test applying minimal theme to UI state."""
        ui_state = UIState()
        success = ui_state.apply_theme("minimal")
        assert success is True
        assert ui_state.current_theme == "minimal"
        assert ui_state.theme_variables is not None

    def test_apply_theme_pirate(self) -> None:
        """Test applying pirate theme to UI state."""
        ui_state = UIState()
        success = ui_state.apply_theme("pirate")
        assert success is True
        assert ui_state.current_theme == "pirate"
        assert ui_state.theme_variables["primary_color"] == "#8B4513"

    def test_apply_invalid_theme(self) -> None:
        """Test applying invalid theme fails gracefully."""
        ui_state = UIState()
        success = ui_state.apply_theme("invalid_theme")
        assert success is False
        assert ui_state.current_theme == "minimal"  # Unchanged

    def test_apply_theme_with_overrides(self) -> None:
        """Test applying theme with custom variable overrides."""
        ui_state = UIState()
        overrides = {"primary_color": "#ff0000"}
        success = ui_state.apply_theme("minimal", overrides)
        assert success is True
        assert ui_state.theme_variables["primary_color"] == "#ff0000"

    def test_theme_in_ui_state_output(self) -> None:
        """Test that theme is included in UI state output."""
        ui_state = UIState()
        ui_state.apply_theme("pirate")
        state = ui_state.get_state()
        assert "theme" in state
        assert state["theme"]["name"] == "pirate"
        assert "variables" in state["theme"]

    def test_ui_state_without_theme(self) -> None:
        """Test UI state without applied theme."""
        ui_state = UIState()
        # Don't apply a theme
        state = ui_state.get_state()
        # Theme should not be in state if not explicitly applied
        assert "theme" not in state or state.get("theme") is None


class TestToolExecutorThemeApplication:
    """Tests for ToolExecutor theme application."""

    def test_execute_apply_theme_tool(self) -> None:
        """Test executing apply_theme tool."""
        ui_state = UIState()

        from src.agent.tool_executor import ToolExecutor

        executor = ToolExecutor(ui_state)
        result = executor.execute_tool("apply_theme", {"theme_name": "pirate"})

        assert "successfully" in result
        assert ui_state.current_theme == "pirate"

    def test_execute_apply_theme_with_overrides(self) -> None:
        """Test executing apply_theme tool with custom overrides."""
        ui_state = UIState()

        from src.agent.tool_executor import ToolExecutor

        executor = ToolExecutor(ui_state)
        result = executor.execute_tool(
            "apply_theme",
            {
                "theme_name": "halloween",
                "custom_overrides": {"primary_color": "#00ff00"},
            },
        )

        assert "successfully" in result
        assert ui_state.theme_variables["primary_color"] == "#00ff00"

    def test_execute_apply_invalid_theme(self) -> None:
        """Test executing apply_theme with invalid theme."""
        ui_state = UIState()

        from src.agent.tool_executor import ToolExecutor

        executor = ToolExecutor(ui_state)
        result = executor.execute_tool("apply_theme", {"theme_name": "invalid"})

        assert "not found" in result or "Error" in result


class TestAgentToolUseWithTheme:
    """Tests for agent tool use with theme application."""

    def test_agent_applies_theme_tool(self) -> None:
        """Test agent can apply theme via tool."""
        mock_tool_use = ToolUseBlock(
            type="tool_use",
            id="tool_123",
            name="apply_theme",
            input={"theme_name": "pirate"},
        )
        mock_text = TextBlock(type="text", text="Theme applied!")

        mock_response_with_tool = MagicMock()
        mock_response_with_tool.content = [mock_tool_use, mock_text]

        mock_text_final = TextBlock(type="text", text="Done!")
        mock_response_final = MagicMock()
        mock_response_final.content = [mock_text_final]

        with patch("src.agent.claude_agent.Anthropic") as mock_anthropic:
            mock_client = MagicMock()
            mock_anthropic.return_value = mock_client
            mock_client.messages.create.side_effect = [
                mock_response_with_tool,
                mock_response_final,
            ]

            agent = ClaudeAgent(system_prompt="Test", api_key="test-key")
            response = agent.process_message("Apply pirate theme")

            assert response == "Done!"
            ui_state = agent.get_ui_state()
            assert "theme" in ui_state
            assert ui_state["theme"]["name"] == "pirate"

    def test_agent_combines_theme_and_buttons(self) -> None:
        """Test agent can create buttons and apply theme in same response."""
        mock_button_tool = ToolUseBlock(
            type="tool_use",
            id="tool_1",
            name="create_button",
            input={
                "label": "Click me",
                "id": "btn_1",
                "callback_id": "on_click",
            },
        )
        mock_theme_tool = ToolUseBlock(
            type="tool_use",
            id="tool_2",
            name="apply_theme",
            input={"theme_name": "cyberpunk"},
        )
        mock_text = TextBlock(type="text", text="UI created!")

        mock_response_with_tools = MagicMock()
        mock_response_with_tools.content = [mock_button_tool, mock_theme_tool, mock_text]

        mock_text_final = TextBlock(type="text", text="All set!")
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
            response = agent.process_message("Create a cyberpunk calculator")

            assert response == "All set!"
            ui_state = agent.get_ui_state()

            # Check button was created
            assert len(ui_state["elements"]) == 1
            assert ui_state["elements"][0]["type"] == "button"

            # Check theme was applied
            assert "theme" in ui_state
            assert ui_state["theme"]["name"] == "cyberpunk"


class TestThemeCharacteristics:
    """Tests for theme definitions and characteristics."""

    def test_pirate_theme_characteristics(self) -> None:
        """Test pirate theme has expected characteristics."""
        theme = THEME_PIRATE
        # Should have warm, pirate-like colors
        assert "#8B4513" in theme["variables"]["primary_color"]
        assert "Georgia" in theme["variables"]["font_family"]

    def test_halloween_theme_characteristics(self) -> None:
        """Test halloween theme has spooky characteristics."""
        theme = THEME_HALLOWEEN
        # Should have orange and purple colors
        assert theme["variables"]["primary_color"] == "#ff6600"
        assert theme["variables"]["secondary_color"] == "#9933ff"

    def test_cyberpunk_theme_characteristics(self) -> None:
        """Test cyberpunk theme has neon characteristics."""
        theme = THEME_CYBERPUNK
        # Should have neon colors and monospace font
        assert theme["variables"]["primary_color"] == "#00ffff"
        assert "monospace" in theme["variables"]["font_family"]

    def test_all_themes_have_required_variables(self) -> None:
        """Test all themes have all required CSS variables."""
        required_vars = {
            "primary_color",
            "bg_primary",
            "text_primary",
            "button_bg",
            "button_text",
            "font_family",
            "border_color",
        }
        all_themes = [
            THEME_MINIMAL,
            THEME_PIRATE,
            THEME_HALLOWEEN,
            THEME_CYBERPUNK,
            THEME_RETRO,
            THEME_FOREST,
        ]
        for theme in all_themes:
            for var in required_vars:
                assert var in theme["variables"], f"{theme['name']} missing {var}"
