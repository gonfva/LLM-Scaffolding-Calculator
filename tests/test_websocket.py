"""Tests for WebSocket functionality."""

from fastapi.testclient import TestClient


def test_websocket_connect_and_disconnect(client: TestClient) -> None:
    """Test WebSocket connection and disconnection."""
    with client.websocket_connect("/ws") as websocket:
        # Connection should succeed without errors
        assert websocket is not None


def test_websocket_echo_message(client: TestClient) -> None:
    """Test WebSocket message echo."""
    with client.websocket_connect("/ws") as websocket:
        # Receive welcome message from agent
        welcome = websocket.receive_text()
        assert "Welcome" in welcome

        # Send test message and receive echo
        test_message = "Hello, Server!"
        websocket.send_text(test_message)
        data = websocket.receive_text()
        assert f"Echo: {test_message}" == data


def test_websocket_multiple_messages(client: TestClient) -> None:
    """Test multiple messages over WebSocket."""
    with client.websocket_connect("/ws") as websocket:
        # Receive welcome message from agent
        welcome = websocket.receive_text()
        assert "Welcome" in welcome

        # Send multiple messages and verify echoes
        messages = ["first", "second", "third"]
        for msg in messages:
            websocket.send_text(msg)
            response = websocket.receive_text()
            assert f"Echo: {msg}" == response
