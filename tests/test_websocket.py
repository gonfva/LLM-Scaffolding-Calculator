"""Tests for WebSocket functionality."""

from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient


def test_websocket_connect_and_disconnect(client: TestClient) -> None:
    """Test WebSocket connection and disconnection."""
    with (
        patch("src.app.main.get_anthropic_api_key", return_value="test-api-key"),
        patch("src.agent.claude_agent.Anthropic"),
    ):
        with client.websocket_connect("/ws") as websocket:
            # Connection should succeed without errors
            assert websocket is not None


def test_websocket_receives_welcome_message(client: TestClient) -> None:
    """Test WebSocket receives init message with LLM response on connect."""
    from anthropic.types import TextBlock

    # Mock the response to "Create a calculator" prompt
    mock_text_block = TextBlock(type="text", text="Calculator created successfully")
    mock_response = MagicMock()
    mock_response.content = [mock_text_block]

    with (
        patch("src.app.main.get_anthropic_api_key", return_value="test-api-key"),
        patch("src.agent.claude_agent.Anthropic") as mock_anthropic,
    ):
        mock_anthropic_instance = MagicMock()
        mock_anthropic.return_value = mock_anthropic_instance
        mock_anthropic_instance.messages.create.return_value = mock_response

        with client.websocket_connect("/ws") as websocket:
            # First message is connection confirmation
            msg = websocket.receive_json()
            assert msg["type"] == "connected"

            # Then init message with LLM response
            msg = websocket.receive_json()
            assert msg["type"] == "init"
            assert "Calculator" in msg["message"]
            assert "ui_state" in msg


def test_websocket_message_to_claude(client: TestClient) -> None:
    """Test WebSocket sends button click message to Claude and receives response."""
    # Mock Claude responses for both initialization and button click
    from anthropic.types import TextBlock

    mock_text_block_init = TextBlock(type="text", text="Calculator ready")
    mock_response_init = MagicMock()
    mock_response_init.content = [mock_text_block_init]

    mock_text_block_click = TextBlock(type="text", text="Button pressed: 5")
    mock_response_click = MagicMock()
    mock_response_click.content = [mock_text_block_click]

    with (
        patch("src.app.main.get_anthropic_api_key", return_value="test-api-key"),
        patch("src.agent.claude_agent.Anthropic") as mock_anthropic,
    ):
        mock_anthropic_instance = MagicMock()
        mock_anthropic.return_value = mock_anthropic_instance
        mock_anthropic_instance.messages.create.side_effect = [
            mock_response_init,
            mock_response_click,
        ]

        with client.websocket_connect("/ws") as websocket:
            # Receive connected message
            connected_msg = websocket.receive_json()
            assert connected_msg["type"] == "connected"

            # Receive init message
            init_msg = websocket.receive_json()
            assert init_msg["type"] == "init"

            # Send button click to Claude
            websocket.send_json({"type": "button_click", "callback_id": "on_5"})
            msg = websocket.receive_json()

            assert msg["type"] == "response"
            assert "Button pressed: 5" in msg["message"]
            assert "ui_state" in msg


def test_websocket_multiple_messages(client: TestClient) -> None:
    """Test WebSocket maintains conversation context across button clicks."""
    # Mock multiple Claude responses
    from anthropic.types import TextBlock

    mock_text_block_init = TextBlock(type="text", text="Ready")
    mock_response_init = MagicMock()
    mock_response_init.content = [mock_text_block_init]

    mock_text_block1 = TextBlock(type="text", text="Display: 5")
    mock_response1 = MagicMock()
    mock_response1.content = [mock_text_block1]

    mock_text_block2 = TextBlock(type="text", text="Display: 10")
    mock_response2 = MagicMock()
    mock_response2.content = [mock_text_block2]

    with (
        patch("src.app.main.get_anthropic_api_key", return_value="test-api-key"),
        patch("src.agent.claude_agent.Anthropic") as mock_anthropic,
    ):
        mock_anthropic_instance = MagicMock()
        mock_anthropic.return_value = mock_anthropic_instance
        mock_anthropic_instance.messages.create.side_effect = [
            mock_response_init,
            mock_response1,
            mock_response2,
        ]

        with client.websocket_connect("/ws") as websocket:
            # Receive connected message
            websocket.receive_json()

            # Receive init message
            websocket.receive_json()

            # Send multiple button clicks
            websocket.send_json({"type": "button_click", "callback_id": "on_5"})
            msg1 = websocket.receive_json()
            assert msg1["type"] == "response"
            assert "Display: 5" in msg1["message"]

            websocket.send_json({"type": "button_click", "callback_id": "on_10"})
            msg2 = websocket.receive_json()
            assert msg2["type"] == "response"
            assert "Display: 10" in msg2["message"]


def test_websocket_initialization_error_handling(client: TestClient) -> None:
    """Test that initialization errors are sent to client properly."""
    with (
        patch("src.app.main.get_anthropic_api_key", return_value="test-api-key"),
        patch("src.agent.claude_agent.Anthropic") as mock_anthropic,
    ):
        mock_anthropic_instance = MagicMock()
        mock_anthropic.return_value = mock_anthropic_instance
        # Make process_message raise an exception
        mock_anthropic_instance.messages.create.side_effect = RuntimeError("API connection failed")

        with client.websocket_connect("/ws") as websocket:
            # First message is connection confirmation
            msg = websocket.receive_json()
            assert msg["type"] == "connected"

            # Then error message from initialization
            msg = websocket.receive_json()
            assert msg["type"] == "error"
            assert "Initialization error" in msg["message"]
            assert "API connection failed" in msg["message"]


def test_websocket_receives_connected_message_immediately(client: TestClient) -> None:
    """Test that client receives 'connected' message immediately, before LLM init.

    This test verifies that WebSocket doesn't block on LLM initialization.
    Client should know it's connected right away, then receive init message when ready.
    """
    from anthropic.types import TextBlock

    mock_text_block = TextBlock(type="text", text="Calculator ready")
    mock_response = MagicMock()
    mock_response.content = [mock_text_block]

    with (
        patch("src.app.main.get_anthropic_api_key", return_value="test-api-key"),
        patch("src.agent.claude_agent.Anthropic") as mock_anthropic,
    ):
        mock_anthropic_instance = MagicMock()
        mock_anthropic.return_value = mock_anthropic_instance
        mock_anthropic_instance.messages.create.return_value = mock_response

        with client.websocket_connect("/ws") as websocket:
            # First message should be "connected" confirmation (not waiting for LLM)
            msg = websocket.receive_json()
            assert msg["type"] == "connected"

            # Then eventually receive init with LLM response
            msg = websocket.receive_json()
            assert msg["type"] == "init"
            assert "ui_state" in msg
