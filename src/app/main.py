import logging

from fastapi import FastAPI, WebSocket
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from src.agent.agent import Agent

logger = logging.getLogger(__name__)

app = FastAPI(title="Agentic Calculator")

# Mount static files
app.mount("/static", StaticFiles(directory="src/static"), name="static")

# Global agent instance (single client assumption for now)
agent: Agent | None = None


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

    # Initialize agent on connection
    agent = Agent(system_prompt="You are a helpful calculator assistant.")
    welcome_msg = agent.send_welcome_message()
    await websocket.send_text(welcome_msg)

    try:
        while True:
            data = await websocket.receive_text()
            logger.info(f"Received: {data}")
            if agent:
                response = agent.process_message(data)
                await websocket.send_text(response)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        logger.info("Client disconnected")
        agent = None
