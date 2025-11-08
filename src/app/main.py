import logging

from fastapi import FastAPI, WebSocket
from fastapi.staticfiles import StaticFiles

logger = logging.getLogger(__name__)

app = FastAPI(title="Agentic Calculator")

# Mount static files
app.mount("/static", StaticFiles(directory="src/static"), name="static")


@app.get("/health")
def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok"}


@app.get("/")
def read_root() -> dict[str, str]:
    """Root endpoint."""
    return {"message": "Agentic Calculator Backend"}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    """WebSocket endpoint for client communication."""
    await websocket.accept()
    logger.info("Client connected")

    try:
        while True:
            data = await websocket.receive_text()
            logger.info(f"Received: {data}")
            # Echo back for now
            await websocket.send_text(f"Echo: {data}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        logger.info("Client disconnected")
