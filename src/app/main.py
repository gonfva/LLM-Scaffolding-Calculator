from fastapi import FastAPI

app = FastAPI(title="Agentic Calculator")


@app.get("/health")
def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok"}


@app.get("/")
def read_root() -> dict[str, str]:
    """Root endpoint."""
    return {"message": "Agentic Calculator Backend"}
