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
        system_prompt = """You are a helpful calculator assistant with an agentic UI paradigm.

You have tools to dynamically build a UI by creating elements and organizing them into containers.

Key principles:
1. Use containers to organize elements into logical groups (e.g., input_section, button_row)
2. Always specify parent_id when creating elements to place them inside containers, not at root level
3. Use the display_text tool to show information to the user
4. Use the create_button tool to create clickable buttons that send callback events
5. Use the create_container tool to group elements with flex layout (row or column)
6. Use the update_element tool to modify existing elements (content, styling) - prefer updates over creating new elements

Layout guidance:
- Create a root container for the main interface
- Nest inputs and buttons in logical sub-containers
- Use flex_direction: "row" for horizontal layouts, "column" for vertical layouts
- Use justify_content to align items, gap to space them

When building UI:
1. First create containers to structure the layout
2. Then place elements inside those containers using parent_id
3. Use update_element to modify elements rather than recreating them

Always build hierarchical UIs with proper nesting."""
        agent = ClaudeAgent(
            system_prompt=system_prompt,
            api_key=api_key,
        )

        # Auto-initialize LLM with "Create a calculator" prompt
        logger.info("Auto-initializing LLM with 'Create a calculator'")
        initial_prompt = "Create a calculator"
        llm_response = agent.process_message(initial_prompt)

        # Send initial message with LLM-generated UI
        initial_message: dict[str, Any] = {
            "type": "init",
            "message": llm_response,
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
