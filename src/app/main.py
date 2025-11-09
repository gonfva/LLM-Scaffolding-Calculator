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

    # Send immediate "connected" confirmation
    connected_msg: dict[str, Any] = {"type": "connected"}
    await websocket.send_json(connected_msg)
    logger.info("Sent connected confirmation to client")

    try:
        # Initialize agent on connection
        api_key = get_anthropic_api_key()
        system_prompt = """You are a calculator assistant with an agentic UI paradigm.

Your primary task is to build and maintain the UI through tool calls. Text responses are secondary.
Keep text responses terse and action-focused. The UI is the main interface, not your words.

Tools available:
- display_text: Show information via display_text tool (not by writing it in your response)
- create_button: Create clickable buttons for user interactions
- create_container: Group elements using flex (row/column) or grid (rows/cols) layout
- update_element: Modify existing elements (prefer updating over recreating)

Layout patterns:
- Flexbox (default): Use flex_direction "row"/"column", justify_content, gap
- Grid (structured layouts): Use rows and cols parameters for consistent layouts like calculators

UI building guidelines:
1. Create containers first to structure the layout
2. Place elements inside containers using parent_id
3. For calculators: use grid layout (e.g., rows=5, cols=4)
4. Use update_element to modify rather than recreate
5. Build hierarchical structures with proper nesting

Response style: Keep your text brief. Let the UI do the talking."""
        agent = ClaudeAgent(
            system_prompt=system_prompt,
            api_key=api_key,
        )

        # Auto-initialize LLM with "Create a calculator" prompt
        logger.info("Auto-initializing LLM with 'Create a calculator'")
        initial_prompt = "Create a calculator"
        try:
            logger.info("Calling agent.process_message...")
            llm_response = agent.process_message(initial_prompt)
            logger.info(
                f"Got response from LLM: {llm_response[:100] if llm_response else 'None'}..."
            )
            # Send initial message with LLM-generated UI
            initial_message: dict[str, Any] = {
                "type": "init",
                "message": llm_response,
                "ui_state": agent.get_ui_state(),
            }
            logger.info("Sending init message to client...")
            await websocket.send_json(initial_message)
            logger.info("Init message sent successfully")
        except Exception as init_error:
            logger.error(f"Error during initialization: {init_error}", exc_info=True)
            try:
                error_msg: dict[str, Any] = {
                    "type": "error",
                    "message": f"Initialization error: {str(init_error)}",
                }
                await websocket.send_json(error_msg)
            except Exception as send_error:
                logger.error(f"Failed to send error message: {send_error}")
            return

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
