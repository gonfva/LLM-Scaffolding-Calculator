import logging

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
        await websocket.send_text(welcome_msg)

        while True:
            data = await websocket.receive_text()
            logger.info(f"Received: {data}")
            if agent:
                response = agent.process_message(data)
                await websocket.send_text(response)
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        await websocket.send_text(f"Error: {e}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await websocket.send_text(f"Error: {type(e).__name__}")
    finally:
        logger.info("Client disconnected")
        agent = None
