import json
import logging
from typing import Any

from fastapi import FastAPI, WebSocket
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from src.agent.claude_agent import ClaudeAgent
from src.config import get_anthropic_api_key

logger = logging.getLogger(__name__)

app = FastAPI(title="Agentic Calculator")

# Mount static files
app.mount("/static", StaticFiles(directory="src/static"), name="static")

# Global agent instance (single client assumption for now)
agent: ClaudeAgent | None = None


@app.get("/health")
def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok"}


@app.get("/")
def read_root() -> FileResponse:
    """Root endpoint - serves the main HTML client."""
    return FileResponse("src/static/index.html", media_type="text/html")


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    """WebSocket endpoint for client communication."""
    global agent

    await websocket.accept()
    logger.info("Client connected")

    try:
        # Initialize agent on connection
        api_key = get_anthropic_api_key()
        agent = ClaudeAgent(
            system_prompt="You are a helpful calculator assistant.",
            api_key=api_key,
        )
        welcome_msg = agent.send_welcome_message()

        # Send initial message with empty UI state
        initial_message: dict[str, Any] = {
            "type": "init",
            "message": welcome_msg,
            "ui_state": agent.get_ui_state(),
        }
        await websocket.send_json(initial_message)

        while True:
            # Try to receive as JSON first (for button clicks), fall back to text
            try:
                data_raw = await websocket.receive_text()
                # Try to parse as JSON
                if data_raw.startswith("{"):
                    data_json = json.loads(data_raw)
                    if data_json.get("type") == "button_click":
                        # Handle button click callback
                        callback_id = data_json.get("callback_id")
                        logger.info(f"Button callback received: {callback_id}")
                        if agent:
                            response = agent.process_message(f"button_click:{callback_id}")
                            ui_state = agent.get_ui_state()

                            message: dict[str, Any] = {
                                "type": "response",
                                "message": response,
                                "ui_state": ui_state,
                            }
                            await websocket.send_json(message)
                    else:
                        # Unknown JSON message type
                        logger.warning(f"Unknown message type: {data_json.get('type')}")
                else:
                    # Regular text message
                    logger.info(f"Received text: {data_raw}")
                    if agent:
                        response = agent.process_message(data_raw)
                        ui_state = agent.get_ui_state()

                        response_msg: dict[str, Any] = {
                            "type": "response",
                            "message": response,
                            "ui_state": ui_state,
                        }
                        await websocket.send_json(response_msg)
            except Exception as e:
                logger.error(f"Error processing message: {e}")
                error_msg: dict[str, Any] = {
                    "type": "error",
                    "message": f"Error processing message: {e}",
                }
                await websocket.send_json(error_msg)
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        error_msg_value_error: dict[str, Any] = {"type": "error", "message": str(e)}
        await websocket.send_json(error_msg_value_error)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        error_msg_generic: dict[str, Any] = {
            "type": "error",
            "message": f"{type(e).__name__}: {e}",
        }
        await websocket.send_json(error_msg_generic)
    finally:
        logger.info("Client disconnected")
        agent = None
