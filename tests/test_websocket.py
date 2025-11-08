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
    """Test WebSocket receives welcome message from agent on connect."""
    with (
        patch("src.app.main.get_anthropic_api_key", return_value="test-api-key"),
        patch("src.agent.claude_agent.Anthropic"),
    ):
        with client.websocket_connect("/ws") as websocket:
            welcome = websocket.receive_text()
            assert "Welcome" in welcome
            assert "Claude" in welcome


def test_websocket_message_to_claude(client: TestClient) -> None:
    """Test WebSocket sends message to Claude and receives response."""
    # Mock Claude response
    from anthropic.types import TextBlock

    mock_text_block = TextBlock(type="text", text="Claude's answer")
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
            # Receive welcome message
            websocket.receive_text()

            # Send message to Claude
            websocket.send_text("What is 2+2?")
            response = websocket.receive_text()

            assert response == "Claude's answer"


def test_websocket_multiple_messages(client: TestClient) -> None:
    """Test WebSocket maintains conversation context across messages."""
    # Mock multiple Claude responses
    from anthropic.types import TextBlock

    mock_text_block1 = TextBlock(type="text", text="First answer")
    mock_response1 = MagicMock()
    mock_response1.content = [mock_text_block1]

    mock_text_block2 = TextBlock(type="text", text="Second answer")
    mock_response2 = MagicMock()
    mock_response2.content = [mock_text_block2]

    with (
        patch("src.app.main.get_anthropic_api_key", return_value="test-api-key"),
        patch("src.agent.claude_agent.Anthropic") as mock_anthropic,
    ):
        mock_anthropic_instance = MagicMock()
        mock_anthropic.return_value = mock_anthropic_instance
        mock_anthropic_instance.messages.create.side_effect = [
            mock_response1,
            mock_response2,
        ]

        with client.websocket_connect("/ws") as websocket:
            # Receive welcome message
            websocket.receive_text()

            # Send multiple messages
            websocket.send_text("First question")
            response1 = websocket.receive_text()
            assert response1 == "First answer"

            websocket.send_text("Second question")
            response2 = websocket.receive_text()
            assert response2 == "Second answer"
