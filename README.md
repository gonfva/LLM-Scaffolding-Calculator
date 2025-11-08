# Calc 2

Second attempt building a calculator using agentic AI

## Development Setup

### Prerequisites
- Python 3.11+
- pip

### Initial Setup

1. Create and activate virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

### Running the App

Start the FastAPI backend server:
```bash
python -m uvicorn src.app.main:app --reload
```

The app will be available at `http://127.0.0.1:8000/`
- Main UI: `http://127.0.0.1:8000/` (connects via WebSocket)
- Health check: `http://127.0.0.1:8000/health`

### Testing & Code Quality

**Run tests:**
```bash
pytest                    # Run all tests
pytest -v               # Verbose output
pytest tests/test_agent.py  # Run specific test file
```

**Format code:**
```bash
black src/ tests/
```

**Lint code:**
```bash
ruff check src/ tests/
```

**Type check:**
```bash
mypy src/
```

**Run all checks (format, lint, type check):**
```bash
black src/ tests/ && ruff check src/ tests/ && mypy src/
```

### Project Structure

```
calc2/
├── src/
│   ├── agent/          # Agent logic
│   │   └── agent.py    # Core agent class
│   ├── app/
│   │   └── main.py     # FastAPI app & WebSocket handler
│   └── static/         # Client-side code
│       ├── index.html  # Web UI
│       └── client.js   # WebSocket client
├── tests/              # Test suite
│   ├── test_agent.py
│   ├── test_endpoints.py
│   ├── test_websocket.py
│   └── conftest.py
├── requirements.txt    # Python dependencies
├── pyproject.toml      # Linting/formatting config
└── .env.example        # Environment variables template
```

## Architecture Overview

The application follows an agentic UI pattern:
- **Backend (Python/FastAPI):** Runs an agent that processes user inputs
- **Client (Vanilla JS):** Connects via WebSocket, sends messages, displays responses
- **Agent:** Currently echoes messages; will be extended with Claude API integration

See `CLAUDE.md` for more details on the design vision.
